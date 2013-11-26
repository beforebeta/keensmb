from django.db import models
from django.contrib.auth.models import *
from django_hstore import hstore
from model_utils import Choices

class Timestamps(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Image(Timestamps):

    IMAGE_TYPES = Choices(
        ('s', 'Small'),
        ('m', 'Medium'),
        ('b', 'Big'),
    )

    url = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=IMAGE_TYPES)
    client = models.ForeignKey('Client')


class Address(Timestamps):

    #subject to change
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    state_province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __unicode__(self):
        return u','.join((self.street, self.city, self.state_province,
                          self.country, self.postal_code))


class Location(Timestamps):

    name = models.CharField(max_length=255)
    client = models.ForeignKey('Client', related_name='locations')
    address = models.ForeignKey('Address')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'client')


class CustomerFieldGroup(Timestamps):

    FIELD_GROUPS = Choices(
        ('basic', 'Basic Information'),
        ('household', 'Household Information'),
        ('custom', 'Custom Fields'),
    )

    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name


class CustomerField(Timestamps):

    FIELD_TYPES = Choices(
        ('string', 'String'),
        ('int', 'Integer'),
        ('date', 'Date'),
        ('url', 'URL'),
        ('email', 'E-mail Address'),
        ('float', 'Float'),
        ('location', 'Location'),
        ('bool', 'Bool')
    )

    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(CustomerFieldGroup)
    group_ranking = models.IntegerField(default=99999999)
    type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Client(Timestamps):

    slug = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    main_location = models.ForeignKey('Location', null=True, blank=True, related_name='+')
    customer_fields = models.ManyToManyField(CustomerField)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class CustomerSource(Timestamps):

    client = models.ForeignKey(Client)
    slug = models.CharField(max_length=50)
    url = models.TextField(blank=True, null=True)
    # this may be a reference to a specific web.models.SignupForm model or a
    # mailchimp list or anything else
    ref_id = models.IntegerField(null=True, blank=True)
    ref_source = models.CharField(max_length=50,null=True, blank=True)

    def __unicode__(self):
        return self.slug

    class Meta:
        unique_together = ('client', 'slug')


class Customer(Timestamps):

    ENRICHMENT_STATUS = Choices(
        ('ne', 'Not Enriched'),
        ('in', 'In Enrichment'),
        ('en', 'Enriched'),
    )

    client = models.ForeignKey('Client')
    source = models.ForeignKey(CustomerSource)
    data = hstore.DictionaryField()
    locations = models.ManyToManyField(Location, related_name='customers')
    enrichment_status = models.CharField(max_length=3, choices=ENRICHMENT_STATUS, default="ne")

    objects = hstore.HStoreManager()
