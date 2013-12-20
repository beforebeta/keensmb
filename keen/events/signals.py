from keen.core.models import *
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from keen.events.models import *

@receiver(post_save, sender=Customer, weak=False)
def customer_created(sender, instance, created, **kwargs):
    if created:
        Event.objects.record_event(client=instance.client, event_type=Event.EVENT_TYPES.cust_new, subject=instance,
                                   occurrence_datetime=instance.created, source=instance.source)

@receiver(post_save, sender=Promotion, weak=False)
def promotion_created(sender, instance, created, **kwargs):
    if created:
        Event.objects.record_event(client=instance.client, event_type=Event.EVENT_TYPES.promo_new, subject=instance,
                                   occurrence_datetime=instance.created)

