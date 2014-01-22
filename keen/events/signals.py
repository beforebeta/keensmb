import logging

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now

from keen.core.models import *
from keen.events.models import *


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Customer, weak=False)
def customer_created(sender, instance, created, **kwargs):
    if created:
        Event.objects.record_event(client=instance.client, event_type=Event.EVENT_TYPES.cust_new, subject=instance,
                                   occurrence_datetime=instance.created, source=instance.source)


@receiver(pre_save, sender=Promotion, weak=False)
def promotion_status_changed(sender, instance, **kw):
    if instance.id:
        try:
            old_status = Promotion.objects.select_for_update().get(
                id=instance.id).status
        except Promotion.DoesNotExist:
            logger.warn('Failed to find supposedly existing Promotion'
                        ' with id=%s. Assuming promotion''s status was changed'
                        % instance.id)
            old_status = None
    else:
        old_status = None

    logger.debug('Checking if ptomotion status was changed from %r to %r'
                 % (old_status, instance.status))

    if instance.status != old_status:
        if instance.status == Promotion.PROMOTION_STATUS.active:
            Event.objects.record_event(
                client=instance.client,
                event_type=Event.EVENT_TYPES.promo_active,
                subject=instance,
                occurrence_datetime=now(),
            )
        elif instance.status == Promotion.PROMOTION_STATUS.scheduled:
            Event.objects.record_event(
                client=instance.client,
                event_type=Event.EVENT_TYPES.promo_scheduled,
                subject=instance,
                occurrence_datetime=now(),
            )


@receiver(post_save, sender=Promotion, weak=False)
def promotion_created(sender, instance, created, **kwargs):
    if created:
        Event.objects.record_event(client=instance.client, event_type=Event.EVENT_TYPES.promo_new, subject=instance,
                                   occurrence_datetime=instance.created)


@receiver(post_delete, sender=Promotion, weak=False)
def promotion_deleted(sender, instance, **kwargs):
    Event.objects.filter(
        data__contains={'subject_type_id': str(ContentType.objects.get_for_model(instance).id),
                        'subject_id': str(instance.id)}
    ).delete()
