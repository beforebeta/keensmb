import os
from subprocess import call
from itertools import chain

from celery import Celery
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from PIL import Image
import mailchimp

from keen.core.models import Customer, Promotion
from keen.web.models import SignupForm


logger = get_task_logger(__name__)

app = Celery('keen')
app.config_from_object('django.conf:settings')


try:
    mailchimp_api_key = settings.MAILCHIMP_API_KEY
except:
    # there is a chance this is configured via environment or via one of
    # mailchimp's configuration file
    logger.warn('Possible misconfiguration: no MAILCHIMP_API_KEY in Django settings!')
else:
    # Mailchimp will look there
    os.environ['MAILCHIMP_APIKEY'] = mailchimp_api_key


@app.task
def take_screenshot(url, file_name, thumbnail=False):
    if call(['bin/phantomjs', 'bin/take-screenshot.js', url, file_name]) != 0:
        logger.error('Failed to take screenshot of %s into %s' % (url, file_name))
    else:
        logger.debug('Screenshot of %s is taken into %s' % (url, file_name))
        if thumbnail:
            size = thumbnail
            img = Image.open(file_name)
            img.thumbnail(size, Image.ANTIALIAS)
            img.save(file_name)
            logger.debug('Converted %s into thumbnail of size %r' % (file_name, size))


@app.task(bind=True)
def mailchimp_subscribe(self, list_id, email, merge_vars, **kw):
    if isinstance(email, basestring):
        email = {'email': email}

    try:
        m = mailchimp.Mailchimp(debug=settings.DEBUG)
        m.lists.subscribe(list_id, email, merge_vars=merge_vars, **kw)
    except mailchimp.Error as exc:
        logger.exception('Failed to subscribe customer to Mailchimp list')
        raise self.retry(exc=exc)


@app.task
def send_email(subject, body, recipients, sender=None, **kw):
    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL

    msg = EmailMessage(subject, body, sender, recipients, **kw)
    msg.content_subtype = 'html'
    msg.send()


@app.task(bind=True)
def promotion_launch(self, promotion_id):
    try:
        promotion = Promotion.objects.get(id=promotion_id)
    except Promotion.DoesNotExist:
        logger.error('Cannot find promotion {0}'.format(promotion_id))
        return

    if promotion.status != Promotion.PROMOTION_STATIS.approved:
        logger.error('Promotion {0}: status must be {1!r}'.format(
            promotion_id, Promotion.PROMOTION_STATIS.approved))
        return

    customers = promotion.customers.values_list('email', 'full_name')
    recipients = [
        {
            'email': email,
            'name': name or 'Valued customer',
        } for email, name in customers if email
    ]

    if recipients:
        ctx = {
            'promotion': promotion,
        }
#        client = promotion.client
#        global_vars = build_vars(
#            client=client.name,
#            description=promotion.description,
#            redemption_instructions=promotion.redemption_instructions,
#            banner_url=promotion.banner_url,
#            image_url=promotion.image_url,
#            additional_information=promotion.additional_information,
#        )
#        rcpt_vars = [
#            {
#                'rcpt': rcpt['email'],
#                'vars': build_vars(rcpt)
#            } for rcpt in recipients
#        ]
        message = {
            'from_name': client.name,
            'from_email': '{0}@keensmb.com'.format(client.slug),
            'to': recipients,
            'subject': promotion.name,
            'html': render_to_string('email/promotion.html', ctx),
            'preserve_recipients': False,
            'track_opens': True,
            'metadata': {
                'client': client.slug,
                'promotion': promotion.id,
            },
#            'merge_vars': rcpt_vars,
#            'global_merge_vars': global_vars,
        }
        m = mandrill.Mandrill(settings.MANDRILL_API_KEY)
        m.messages.send(message=message, async=True)

        promotion.status = Promotion.PROMOTION_STATUS.active
        promotion.save()


def build_vars(*args, **kw):
    """
    Convert dictionary-like data into Mandrill API array of sructs.

    Positional arguments if any expected to be dictionaries.

    WARNING: Mandrill API does not say what happens if some name occures more than once
    so this function does not attempt to deal with duplicate names.
    """
    items = chain(*(d.iteritems() for d in args + (kw,)))
    return [
        {
            'name': name,
            'content': value,
        } for name, value in items]
