from django.db import models
from django.contrib.auth.models import *
from django_hstore import hstore


class Timestamps(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HStoreFieldCatalog(Timestamps):

    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50)
    # allows you to group fields together
    grouping = models.CharField(max_length=50)
    group_ranking = models.PositiveSmallIntegerField()
    length = models.IntegerField()


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
    client = models.ForeignKey('Client')
    address = models.ForeignKey('Address')
    is_main = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'client')


class Client(Timestamps):

    slug = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    customer_fields = models.ManyToManyField(HStoreFieldCatalog)
    groups = models.ManyToManyField(Group)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.slug


class CustomerSource(Timestamps):

    client = models.ForeignKey(Client)
    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    url = models.TextField(blank=True, null=True)
    # this may be a reference to a specific web.models.SignupForm model or a
    # mailchimp list or anything else
    ref_id = models.IntegerField()
    ref_source = models.CharField(max_length=50)

    class Meta:
        unique_together = ('client', 'name')


class Customer(Timestamps):

    ENRICHMENT_STATUS = (
        ('NE', 'Not Enriched'),
        ('IN', 'In Enrichment'),
        ('EN', 'Enriched'),
    )

    client = models.ForeignKey('Client')
    source = models.ForeignKey(CustomerSource)
    data = hstore.DictionaryField(db_index=True)
    locations = models.ManyToManyField(Location)
    enrichment_status = models.CharField(max_length=3,
                                         choices=ENRICHMENT_STATUS)

    objects = hstore.HStoreManager()
