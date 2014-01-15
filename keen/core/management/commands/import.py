from optparse import make_option
from json import load

from django.db import DatabaseError
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from keen.core.models import Client, CustomerField, CustomerSource, Customer, ClientUser
from keen.web.models import Dashboard
from tracking.models import Visitor


class Command(BaseCommand):
    """Iport Client, CustomerSource, Customer and Visitor from legacy
    database."""
    option_list = BaseCommand.option_list + (
        make_option('--clear', dest='clear', default=False,
                    action='store_true',
                    help='Delete all clients, customer sources, customers and visitorspriors'),
    )
    help = 'Specify one or more file created by dumpdata command on legacy database'

    def handle(self, *args, **options):
        if options['clear']:
            Client.objects.all().delete()
            Customer.objects.all().delete()
            Visitor.objects.all().delete()
            ClientUser.objects.all().delete()

        if args:
            self.phone_numbers = {}
            for filename in args:
                self._import(filename)
            for dashboard in Dashboard.objects.all():
                dashboard.refresh()

        self._fix_sequences()

    def _import(self, filename):
        with file(filename) as fd:
            for obj in load(fd):
                fields = obj['fields']
                for name in fields.keys():
                    if isinstance(fields[name], basestring):
                        fields[name] = fields[name].replace('"', '')
                fields['created'] = fields.pop('date_added', None)
                fields['modified'] = fields.pop('last_modified', None)

                if obj['model'] == 'main.visitor':
                    fields.pop('uuid')
                    for field, default in (
                        ('ip_address', '0.0.0.0'),
                        ('user_agent', ''),
                    ):
                        if fields.get(field) is None:
                            fields[field] = default
                    Visitor.objects.create(pk=obj['pk'], **fields)
                elif obj['model'] == 'main.client':
                    fields['slug'] = fields.pop('unique_id')
                    client = Client.objects.create(pk=obj['pk'], **fields)
                    email = '%s@keensmb.com' % client.slug
                    user, created = User.objects.get_or_create(username=email, email=email)
                    if created:
                        user.set_password(client.slug)
                        user.save()
                    ClientUser.objects.create(user=user, client=client)
                    client.customer_fields = list(CustomerField.objects.all())
                    client.save()
                    dashboard = Dashboard.objects.create(client=client)
                elif obj['model'] == 'main.customersource':
                    fields['client_id'] = fields.pop('client')
                    fields['slug'] = fields.pop('name')
                    CustomerSource.objects.create(pk=obj['pk'], **fields)
                elif obj['model'] == 'main.phonenumber':
                    self.phone_numbers[obj['pk']] = obj['fields']['number']
                elif obj['model'] == 'main.customer':
                    customer = Customer()
                    customer.pk = obj['pk']
                    customer.visitor_id = fields['visitor']
                    source = CustomerSource.objects.get(pk=fields['source'])
                    customer.source_id = source.id
                    customer.client_id = source.client_id
                    customer.created = fields['created']
                    customer.modified = fields['modified']
                    customer.data['full_name'] = fields.get('full_name', ' '.join(
                        filter(None, (fields.get(f) for f in
                                      ('first_name', 'middle_name', 'last_name')))))
                    if fields.get('zip'):
                        customer.data['address__zipcode'] = fields['zip']
                    customer.data['dob'] = fields['dob'] or ''
                    if fields['phone'] and fields['phone'][0] in self.phone_numbers:
                        customer.data['phone'] = self.phone_numbers[fields['phone'][0]]
                    customer.data['email'] = fields['email'] or ''
                    try:
                        customer.save()
                    except DatabaseError:
                        print >> self.stderr, 'Failed to save customer model %r' % customer
                        raise

    def _fix_sequences(self):
        from django.db import connection
        from django.db.models import Max

        c = connection.cursor()
        for model, name_prefix in (
            (Client, 'core_client'),
            (CustomerSource, 'core_customersource'),
            (Customer, 'core_customer'),
            (Visitor, 'tracking_visitor'),
        ):
            max_id = model.objects.aggregate(Max('id'))['id__max']
            c.execute('alter sequence %s_id_seq restart with %d' % (name_prefix, max_id + 1))
