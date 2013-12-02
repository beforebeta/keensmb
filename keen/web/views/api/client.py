from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser

from keen.core.models import Client, Customer
from keen.core.serializers import (
    ClientSerializer,
    CustomerSerializer,
)


class IsClientUser(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.client_slug == view.kwargs.get('client_slug'))


class ClientProfile(APIView):

    # permission_classes = (IsAdminUser, IsClientUser)

    def get(self, request, client_slug, part=None):
        client = get_object_or_404(Client, slug=client_slug)
        data = ClientSerializer(client).data

        if part == 'summary':
            data['total_customers'] = client.customers.count()
            data['redeemers'] = 0
            data['new_signups'] = 0

        return Response(data)


class CustomerList(APIView):

    # permission_classes = (IsAdminUser, IsClientUser)

    def get(self, request, client_slug):
        """Return one page of Customer objects
        """
        client = get_object_or_404(Client, slug=client_slug)

        # FIXME: this should be configurabe
        page_size = int(getattr(settings, 'CUSTOMER_LIST_PAGE_SIZE', 50))

        if 'offset' in request.GET:
            try:
                offset = int(request.GET['offset'])
                if offset < 0:
                    offset = 0
            except ValueError:
                offset = 0
        else:
            offset = 0

        customers = client.customer_page(offset, page_size=page_size)
        loaded = len(customers)

        data = {
            'customers': CustomerSerializer(customers,
                exclude_fields=('created', 'modified', 'client'),
                many=True).data,
        }
        if loaded == page_size:
            data['next_page'] = reverse(
                'api_customer_list', kwargs={'client_slug': client_slug}) + '?offset=%d' % (offset + page_size)
        return Response(data)

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
