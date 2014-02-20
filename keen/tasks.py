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
    import csv
    from keen.core.models import Customer, CustomerSource
    from keen.web.models import CustomerField, ImportRequest

    with transaction.atomic():
        imp = ImportRequest.objects.select_for_update().get(id=import_id)

        if imp.status != ImportRequest.STATUS.new:
            logger.error('Cannot process import request in status {0}'.format(imp.status))
            return

        imp.status = 'in-progress'
        imp.data['imported'] = 0
        imp.data['updated'] = 0
        imp.data['failed'] = 0
        imp.data['errors'] = []
        imp.save()

    try:
        fields = [
            (CustomerField.objects.get(name=field) if field else None)
            for field in imp.data['import_fields']
        ]
    except CustomerField.DoesNotExist:
        imp.status = ImportRequest.STATUS.failed
        imp.errors.append('Failed to build customer field list')
        imp.save()
        return

    num_fields = len(fields)
    client = imp.client

    try:
        source = CustomerSource.objects.create(
            client=client,
            slug='import-csv-{0}'.format(imp.id),
            ref_source='import-csv',
            ref_id=imp.id,
        )
    except DatabaseError:
        imp.status = ImportRequest.STATUS.failed
        imp.errors.append('Failed to create customer source')
        imp.save()
        return

    with transaction.atomic():
        for row in row_reader(imp):
            # malformed rows are skipped
            if len(row) != num_fields:
                imp.data['failed'] += 1
                continue

            data = dict((field.name, row[i]) for i, field in enumerate(fields) if field)
            customer = find_customer(client, data)

            if customer:
                merge_customer_data(customer, data)
                action = 'updated'
            else:
                customer = Customer(client=client, source=source, data=data)
                action = 'imported'

            sp = transaction.savepoint()
            try:
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save customer')
                transaction.savepoint_rollback(sp)
                imp.data['failed'] += 1
            else:
                transaction.savepoint_commit(sp)
                imp.data[action] += 1

        imp.status = ImportRequest.STATUS.complete
        imp.save()


def row_reader(imp):
    imp.file.open()
    reader = csv.reader(imp.file.file)
    if imp.data['skip_first_row']:
        reader.next()
    for row in reader:
        yield map(str.strip, row)


def find_customer(client, data):
    for field in 'email', 'social__facebook', 'social__googleplus', 'social__twitter':
        value = data.get(field, None)
        if value:
            customer = Customer.objects.filter(data__contains={field: value}).first()
            if customer:
                return customer
    # if no identity matches
    # return Customer.objects.filter(data__contains=data).first()
    return None


def merge_customer_data(customer, data):
    for key, value in data.items():
        if value:
            customer.data[key] = value
