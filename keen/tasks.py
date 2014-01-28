import os
from subprocess import call

from celery import Celery
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template

from PIL import Image
import mailchimp

from keen.core.models import Customer
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
def mailchimp_subscribe(self, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        logger.error('Failed to find customer with id=%s' % customer_id)
        raise Ignore()

    if customer.client.ref_id_type != 'mailchimp':
        logger.info('Client %s has no Mailchimp list ID' % customer.client.name)
        raise Ignore()

    list_id = customer.client.ref_id

    email = {
        'email': customer.data['email'],
    }

    merge_vars = {
        'CUSTOMERID': customer.id,
        'FNAME': customer.data.get('first_name', ''),
        'LNAME': customer.data.get('last_name', ''),
        'FULLNAME': customer.data.get('full_name', ''),
        'NUMBER': customer.data.get('phone', ''),
        'ZIPCODE': customer.data.get('address__ipcode', ''),
        'BIRTHDAY': customer.data.get('dob', ''),
        'GENDER': customer.data.get('gender', ''),
        'SIGNUPNAME': '',
        'SIGNUPID': '',
    }
    if customer.source and customer.source.ref_source == 'signup':
        try:
            form = SignupForm.objects.get(id=customer.source.ref_id)
        except SignupForm.DoesNotExist:
            logger.warn('Customer signup form with id %s not found' % customer.source.ref_id)
        else:
            merge_vars['SIGNUPNAME'] = form.data.get('pageTitle', '')
            merge_vars['SIGNUPID'] = form.id

    try:
        m = mailchimp.Mailchimp()
        m.lists.subscribe(list_id, email, merge_vars=merge_vars,
                          double_optin=False, update_existing=True,
                          send_welcome=True)
    except mailchimp.Error as exc:
        logger.exception('Failed to subscribe customer to Mailchimp list')
        raise self.retry(exc=exc)


template = Template('''
Client {{ client.name }} wants to enrich data of the following customers:

    {% for customer in customers %}
    {{ customer.data.email }}, {{ customer.data.full_name }}, {{ customer.id }}
    {% endfor %}
''')

@app.task
def enrich_customers_data(client, customers):

    customers = list(Customer.objects.filter(
        client=client, id__in=customers))

    msg = template.render(Context({
        'client': client,
        'customers': customers,
    }))

    send_mail('New Enrichment Request', msg, 'do-not-reply@keensmb.com', ['workflow@keensmb.com'])
