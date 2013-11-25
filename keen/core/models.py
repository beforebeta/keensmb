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

    IMAGE_TYPES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('B', 'Big'),
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


class Location(Timestamps):

    name = models.CharField(max_length=255)
    client = models.ForeignKey('Client', related_name='locations')
    address = models.ForeignKey('Address')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'client')


class CustomerField(Timestamps):

    FIELD_GROUPS = Choices(
        ('basic', 'Basic Information'),
        ('household', 'Household Information'),
        ('custom', 'Custom Fields'),
    )

    FIELD_TYPES = Choices(
        ('int', 'int'),
        ('string', 'string'),
        ('float', 'float'),
        ('bool', 'bool'),
        ('date', 'datetime.date'),
        ('url', 'url'),
        ('email', 'email')
    )

    name = models.CharField(max_length=64, unique=True)
    group = models.CharField(max_length=32)
    type = models.CharField(max_length=1, choices=Choices(FIELD_TYPES))
    description = models.CharField(max_length=255, blank=True, null=True)
    # allows you to group fields together
    grouping = models.CharField(max_length=50, choices=FIELD_GROUPS)
    group_ranking = models.PositiveSmallIntegerField()
    length = models.IntegerField()

class Client(Timestamps):

    slug = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    main_location = models.ForeignKey('Location', null=True, related_name='+')
    customer_fields = models.ManyToManyField(CustomerField)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class CustomerSource(Timestamps):

    client = models.ForeignKey(Client)
    slug = models.CharField(max_length=50)
    url = models.TextField(blank=True, null=True)
    # this may be a reference to a specific web.models.SignupForm model or a
    # mailchimp list or anything else
    ref_id = models.IntegerField()
    ref_source = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('client', 'slug')


class Customer(Timestamps):

    ENRICHMENT_STATUS = (
        ('NE', 'Not Enriched'),
        ('IN', 'In Enrichment'),
        ('EN', 'Enriched'),
    )

    client = models.ForeignKey('Client')
    source = models.ForeignKey(CustomerSource)
    data = hstore.DictionaryField()
    locations = models.ManyToManyField(Location, related_name='customers')
    enrichment_status = models.CharField(
        max_length=3, choices=ENRICHMENT_STATUS)

    objects = hstore.HStoreManager()
