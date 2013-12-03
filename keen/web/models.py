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
    fields = models.ManyToManyField(CustomerField)


class SignupForm(Timestamps):

    client = models.ForeignKey(Client)
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()
