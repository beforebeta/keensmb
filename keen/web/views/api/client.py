import re
from django.conf import settings
from django.http import QueryDict, Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser

from keen.core.models import Client, Customer
from keen.web.models import PageCustomerField
from keen.core.serializers import (
    ClientSerializer,
    CustomerSerializer,
    CustomerFieldSerializer,
)
from keen.web.forms import CustomerForm


field_name_re = re.compile(r'^[a-z_][a-z0-9_#]*$')


class IsClientUser(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.client_slug == view.kwargs.get('client_slug'))


class ClientProfile(APIView):

    # permission_classes = (IsAdminUser, IsClientUser)

    def get(self, request, client_slug, part=None):
        client = get_object_or_404(Client, slug=client_slug)

        if part is None:
            data = ClientSerializer(client).data
        elif part == 'summary':
            data = {
                'total_customers': client.customers.count(),
                'redeemers': 0,
                'new_signups': 0,
            }
        elif part == 'customer_fields':
            available_fields = list(client.customer_fields.all())
            display_fields = list(
                client.customer_fields.filter(
                    id__in=PageCustomerField.objects.filter(
                        client=client, page='db').values('fields__id')))

            if not display_fields:
                display_fields = available_fields
            data = {
                'available_customer_fields': CustomerFieldSerializer(
                    available_fields, many=True).data,
                'display_customer_fields': [field.name for field in display_fields],
            }
        else:
            return Http404()

        return Response(data)

    def put(self, request, client_slug, part=None):
        client = get_object_or_404(Client, slug=client_slug)

        if part == 'customer_fields':
            params = QueryDict(request.body, request.encoding)
            params = QueryDict(params['_content'], params['_content_type'])
            fields = params.get('display_customer_fields', '').split(',')
            page, created = PageCustomerField.objects.get_or_create(page='db', client=client)
            page.fields = list(client.customer_fields.filter(name__in=fields))
            page.save()
            data = {'success': 'Saved'}
        else:
            return HttpResponseNotAllowed()

        return Response(data)


class CustomerList(APIView):

    # permission_classes = (IsAdminUser, IsClientUser)

    def get(self, request, client_slug):
        """Return one page of Customer objects
        """
        client = get_object_or_404(Client, slug=client_slug)

        try:
            limit = int(request.GET['limit'])
        except (KeyError, ValueError):
            limit = 50

        try:
            offset = int(request.GET['offset'])
        except (KeyError, ValueError):
            offset = 0

        customers = client.customers.all()

        if 'fields' in request.GET:
            fields = [field for field in request.GET['fields'].split(',')
                      if field_name_re.match(field)]
            customers = customers.extra(
                select={'data': 'slice(data, array[%s])' % (
                    ','.join(("'%s'" % field) for field in fields))},
            )

        if 'search' in request.GET:
            # full-text search
            customers = customers.extra(
                where=['cast(avals(data) as text) @@ %s'],
                params=[request.GET['search']])

        if 'order' in request.GET:
            order_by = request.GET['order'].split(',')
            fields = [field.lstrip('-') for field in order_by]
            # TODO: Use client.customer_fields to match field names AND
            # to add CAST to database query so it matches index that was
            # created by setup management command
            customers = customers.extra(
                select=dict(
                    (field, "core_customer.data -> '%s'" % field)
                    for field in fields if field not in [
                    'id', 'created', 'modified', 'client_id'])).order_by(
                        *order_by)

        customers = customers[offset:offset + limit]
        customers = CustomerSerializer(customers, many=True).data

        return Response({
            'offset': offset,
            'limit': limit,
            'customers': customers,
        })

    def post(self, request, client_slug):
        """Create new customer
        """
        client = get_object_or_404(Client, slug=client_slug)
        form = CustomerForm(client, request.POST)

        if form.is_valid():
            try:
                customer = Customer(**customer)
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
                return Result(status=status.HTTTP_500_SERVER_ERROR)

        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


class CustomerProfile(APIView):

    # permission_classes = (IsAdminUser, IsClientUser)

    def get(self, request, client_slug, customer_id):
        """Retrieve customer profile
        """
        customer = get_object_or_404(Customer, client__slug=client_slug, id=customer_id)
        return Response(CustomerSerializer(customer).data)

    def post(self, request, client_slug, customer_id):
        """Update customer profile
        """
        customer = get_object_or_404(Customer, client__slug=client_slug, id=customer_id)

        form = CustomerForm(client, request.POST)

        if form.is_valid():
            for field in form:
                if field.name.startswith('data_'):
                    name = field.name[5:]
                    # FIXME: should check if this field is actually in
                    # customer_fields of that client
                    customer[name] = field.value

            try:
                customer.save()
            except DatabaseError:
                logger.exception('Failed to update customer')
                return response('Failed to save customer profile',
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(CustomerSerializer(customer).data)
