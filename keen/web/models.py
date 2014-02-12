import os
from uuid import uuid1

from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from model_utils import Choices

from jsonfield import JSONField

from keen import util
from keen.core.models import (
    Timestamps,
    Client,
    CustomerField,
    Customer,
    Promotion,
    CustomerSource,
)

from tracking.models import Visitor


class PageCustomerField(Timestamps):

    PAGE_NAMES = Choices(
        ('db', 'Customer Database View'),
        ('sc', 'Single Customer View'),
    )

    page = models.CharField(max_length=3, choices=PAGE_NAMES)
    client = models.ForeignKey(Client)
    fields = models.CharField(max_length=1024,
                              default='first_name,last_name,email')


class SignupForm(Timestamps):

    STATUS_NAMES = Choices(
        ('draft', 'Dratf'),
        ('published', 'Published'),
    )

    client = models.ForeignKey(Client, related_name='signup_forms')
    slug = models.SlugField()
    status = models.CharField(max_length=32, choices=STATUS_NAMES,
                              default=STATUS_NAMES.draft)
    data = JSONField()
    visits = models.IntegerField(default=0)
    visitors = models.ManyToManyField(Visitor, related_name='signup_forms')

    submission_notification = models.TextField(blank=True, null=True)
    signup_confirmation_subject = models.CharField(max_length=255, null=True,
                                                   blank=True)
    submission_confirmation_html = models.TextField(blank=True, null=True)
    submission_confirmation_sender = models.EmailField(blank=True, null=True)

    @property
    def url(self):
        return reverse('customer_signup',
                       kwargs=dict(client_slug=self.client.slug,
                                   form_slug=self.slug))

    def __unicode__(self):
        return '{0}/{1}'.format(self.client.slug, self.slug)

    @property
    def extra_fields(self):
        fields = self.data.get('extra_fields', [])
        if fields:
            names = [field['name'] for field in fields]
            cache = dict(
                (field.name, field) for field in
                CustomerField.objects.filter(name__in=names)
            )
            fields = [cache[name] for name in names]
        return fields

    class Meta:
        unique_together = ('client', 'slug')


class TrialRequest(Timestamps):
    """Represents free trial request
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    business = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    question = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    visitor = models.ForeignKey(Visitor, null=True)
    source = models.CharField(max_length=255, null=True, blank=True)


def _upload_file_name(import_request, file_name):
    return os.path.join('import', import_request.client.slug, uuid1().hex)


class ImportRequest(Timestamps):

    STATUS = Choices(
        ('new', 'New'),
        ('in_progress', 'In-progress'),
        ('complete', 'Complete'),
        ('aborted', 'Aborted'),
    )

    client = models.ForeignKey(Client)
    status = models.CharField(max_length=32, choices=STATUS, default=STATUS.new)
    file = models.FileField(upload_to=_upload_file_name)
    data = JSONField()
