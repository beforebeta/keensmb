from django.db import models
from django_hstore import hstore
from model_utils import Choices
from keen import util
from keen.core.models import Timestamps, Client, CustomerField, Customer, Promotion
from django.db.models import Q

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
    fields = models.ManyToManyField(CustomerField)
    status = models.CharField(max_length=32, choices=STATUS_NAMES,
                              default=STATUS_NAMES.draft)
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()

    class Meta:
        unique_together = ('client', 'slug')

class Dashboard(Timestamps):
    client = models.ForeignKey(Client)

    #analytics
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    promotions_this_month = models.IntegerField(default=0)
    redemptions = models.IntegerField(default=0)

    def refresh(self):
        self.total_customers = Customer.objects.filter(client=self.client).count()
        self.new_customers = Customer.objects.filter(client=self.client, created__gte=util.get_first_day_of_month_as_dt()).count()
        self.promotions_this_month = Promotion.objects.filter(
                                    Q(valid_from__gte=util.get_first_day_of_month_as_dt()) | Q(valid_from__isnull=True),
                                    Q(valid_to__lte=util.get_last_day_of_month_as_dt()) | Q(valid_to__isnull=True),
                                    client=self.client).count()
        self.redemptions = 0
        self.save()