from json import load

from django.db import DatabaseError
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from keen.core.models import Client, CustomerField, CustomerSource, Customer, ClientUser
from keen.web.models import Dashboard
from tracking.models import Visitor


class Command(BaseCommand):

    def handle(self, *args, **options):
        Client.objects.all().delete()
        Customer.objects.all().delete()
        Visitor.objects.all().delete()
        ClientUser.objects.all().delete()
        self.phone_numbers = {}
        for filename in args:
            print 'Importing data from %s' % filename
            self._import(filename)

    def _import(self, filename):
        with file(filename) as fd:
            for obj in load(fd):
                fields = obj['fields']
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
                    dashboard.refresh()
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
                    customer.data['dob'] = fields['dob']
                    if fields['phone'] and fields['phone'][0] in self.phone_numbers:
                        customer.data['phone'] = self.phone_numbers[fields['phone'][0]]
                    customer.data['email'] = fields['email']
                    try:
                        customer.save()
                    except DatabaseError:
                        print customer
                        raise
