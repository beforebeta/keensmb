from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404

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
from keen.events import Event

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

    def get_updates(self):
        return Event.objects.filter(client=self.client).order_by('-occurrence_datetime')[:14]

    def get_top_customers(self):
        return self.client.get_top_customers()[:5]

    def get_top_promotions(self):
        return self.client.get_top_promotions()[:4]

    def get_active_promotions(self):
        return self.client.get_active_promotions()[:3]

    def get_active_promotions_count(self):
        return self.client.get_active_promotions_count()


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
