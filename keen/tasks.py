import os
from subprocess import call

from celery import Celery
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from django.conf import settings
from django.db import transaction
from django.core.mail import EmailMessage

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
def send_email(subject, body, recipients, sender=None):
    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL

    EmailMessage(subject, body, sender, recipients).send()


@app.task
def import_customers(import_id):
    from keen.core.models import Customer
    from keen.web.models import CustomerField, ImportRequest

    with transaction.atomic():
        imp = ImportRequest.objects.select_for_update().get(id=import_id)

        if imp.status != ImportRequest.STATUS.new:
            logger.error('Cannot process import request in status {0}'.format(imp.status))
            return

        imp.status = ImportRequest.STATUS.in_progress
        imp.data['imported'] = 0
        imp.data['failed'] = 0
        imp.data['errors'] = []
        imp.save()

    client = imp.client
    fields = [
        (CustomerField.objects.get(name=field) if field else None)
        for field in imp.data['import_fields']
    ]

    imp.file.open()
    reader = csv.reader(imp.file.file)
    if imp.data['skip_first_row']:
        reader.next()

    with transaction.atomic():
        source = CustomerSource.objects.create(
            clinet=client,
            slug='import-csv-{0}'.format(imp.id),
            ref_source='import-csv',
            ref_id=imp.id,
        )

        for row in reader:
            data = {}
            for i, field in enumerate(fields):
                if field:
                    data[field.name] = row[i]
            sp = transaction.savepoint()
            try:
                Customer.objects.create(client=client, source=source, data=data)
            except DatabaseError:
                logger.exception('Failed to save imported client')
                transaction.savepoint_rollback(sp)
                imp.data['failed'] += 1
            else:
                transaction.savepoint_commit(sp)
                imp.data['imported'] += 1

            imp.save()

        imp.status = ImportRequest.STATUS.complete
        imp.save()
