from django.db import models

from keen.core.models import Timestamps, Client, Customer


class EnrichmentRequest(Timestamps):
    client = models.ForeignKey(Client, related_name='enrichment_requests')
    customers = models.ManyToManyField(Customer, related_name='enrichment_requests')
