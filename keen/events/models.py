from django.contrib.contenttypes.models import ContentType
from keen.core.models import *
from django.db import models
from django_hstore import hstore
import datetime
import json
from keen import print_stack_trace


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
            print_stack_trace()

    def save(self, *args, **kwargs):
        if self.data:
            self.data = dict((name, json.dumps(value)) for name, value in self.data.items())
        super(Event, self).save(*args, **kwargs)

    def subject(self):
        return ContentType.objects.get_for_id(self.data['subject_type_id']).get_object_for_this_type(
                                                                                            id=self.data['subject_id'])
