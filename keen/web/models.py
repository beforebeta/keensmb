from django.db import models
from django_hstore import hstore
from model_utils import Choices
from keen.core.models import Timestamps, Client, CustomerField


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

    client = models.ForeignKey(Client)
    slug = models.SlugField()
    fields = models.ManyToManyField(CustomerField)
    status = models.CharField(max_length=32, choices=STATUS_NAMES,
                              default=STATUS_NAMES.draft)
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()

    class Meta:
        unique_together = ('client', 'slug')
