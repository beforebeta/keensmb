import logging
import datetime
import json

from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from django_hstore import hstore
from model_utils import Choices

from keen.core.models import Timestamps, Client, Customer, Promotion
from keen.tasks import send_email


logger = logging.getLogger(__name__)


class EventManager(hstore.HStoreManager):

    def record_event(self, client, event_type, is_aggregate=False, subject=None, subject_list=None, target=None,
                                                            target_list=None, source=None, occurrence_datetime=None):
        if not occurrence_datetime:
            occurrence_datetime = datetime.datetime.now()
        event = self.model(client=client)
        event.occurrence_datetime = occurrence_datetime
        event.is_aggregate = is_aggregate
        event.data = {
            'type': event_type
        }
        if subject:
            event.data['subject_type_id'] = ContentType.objects.get_for_model(subject).id
            event.data['subject_id'] = subject.id
        if subject_list:
            event.data['subject_type_id'] = ContentType.objects.get_for_model(subject_list[0]).id
            event.data['subject_ids'] = [s.id for s in subject_list]
        if target:
            event.data['target_type_id'] = ContentType.objects.get_for_model(target).id
            event.data['target_id'] = target.id
        if target_list:
            event.data['target_type_id'] = ContentType.objects.get_for_model(target_list[0]).id
            event.data['target_ids'] = [s.id for s in target_list]
        if source:
            event.data['source_type_id'] = ContentType.objects.get_for_model(source).id
            event.data['source_id'] = source.id

        event.save()


class Event(Timestamps):
    """
        Events are based on a Subject, Verb, Object and Source

        Subject performed Verb on Object via Source
        e.g. Customer A performed Redemption on Object via Email

        In some cases there are no Objects, i.e. Subject performed Verb
        e.g. Customer A was created

        List of Events:
        1. cust_new - New customer was added
           Subject: Customer Subject ID: Customer.ID
           Verb: Added
           Source: Import form

        2. cust_multi_new - Many New Customers Were Added
           Subject: Customer Subject ID: [Customer.ID, Customer.ID, Customer.ID]
           Verb: Added
           Source: Import form

        3. cust_redemption - Customer Redeemed Promotion
            Subject: Customer Subject ID: Customer.ID
            Verb: Redeemed
            Source: Email
            Object: Promotion Object ID: Promotion.ID

        4. promo_new - New Promotion was created
            ...

        5. promo_expiring - Promotion is expiring
            ...
    """

    EVENT_TYPES = Choices(
        ('cust_new', 'New Customer Created'),
        ('cust_multi_new', 'Many New Customers Created'),
        ('cust_redemption', 'Customer Redeemed Promotion'),
        ('promo_new', 'New Promotion Created'),
        ('promo_expiring', 'Promotion is Expiring'),
        ('promo_active', 'Promotion Activated'),
        ('promo_scheduled', 'Promotion Scheduled'),
    )

    client = models.ForeignKey(Client)
    is_aggregate = models.BooleanField(default=False)
    occurrence_datetime = models.DateTimeField(default=datetime.datetime.now())

    data = hstore.DictionaryField()

    objects = EventManager()

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        try:
            if self.data:
                self.data = dict((name, json.loads(value)) for name, value in self.data.items())
        except:
            logger.exception('Failed to initialize Event instance')

    def save(self, *args, **kwargs):
        if self.data:
            self.data = dict((name, json.dumps(value)) for name, value in self.data.items())
        super(Event, self).save(*args, **kwargs)

    def subject(self):
        return ContentType.objects.get_for_id(self.data['subject_type_id']).get_object_for_this_type(id=self.data['subject_id'])


@receiver(post_save, sender=Customer, weak=False)
def customer_created(sender, instance, created, **kwargs):
    if created:
        Event.objects.record_event(client=instance.client,
                                   event_type=Event.EVENT_TYPES.cust_new,
                                   subject=instance,
                                   occurrence_datetime=instance.created,
                                   source=instance.source)


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
            send_promotion_status_email(instance)
        elif instance.status == Promotion.PROMOTION_STATUS.scheduled:
            Event.objects.record_event(
                client=instance.client,
                event_type=Event.EVENT_TYPES.promo_scheduled,
                subject=instance,
                occurrence_datetime=now(),
            )
            send_promotion_status_email(instance)


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


def send_promotion_status_email(promotion):
    send_email.delay(
        'Promotion status changed to {0.status}'.format(promotion),
        'Promotion {0.name} ({0.id}) status changed to {0.status}'.format(promotion),
        ['workflow@keensmb.com'],
    )
