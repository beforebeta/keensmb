from django.db import models
from django_hstore import hstore

from keen.core.models import *


class PageCustomerField(Timestamps):

    PAGE_NAMES = (
        ('DB', 'Customer Database View'),
        ('SC', 'Single Customer View'),
    )

    page = models.CharField(max_length=3, choices=PAGE_NAMES)
    client = models.ForeignKey(Client)
    fields = models.ManyToManyField(CustomerField)


class SignupForm(Timestamps):

    client = models.ForeignKey(Client)
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()
