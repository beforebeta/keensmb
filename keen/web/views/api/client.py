from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from keen.core.models import Client, Customer


class CustomerList(APIView):
    """Customer list API
    """
    def get(self, request, offset=None):
        """Return one page of Customer objects
        """
        # FIXME: should be taken from user instead
        client = get_object_or_404(Client, slug='default_client')

        # FIXME: this should be configurabe
        page_size = 1000

        if offset:
            try:
                offset = int(offset)
                if offset < 0:
                    offset = 0
            except ValueError:
                offset = 0
        else:
            offset = 0

        ctx = {
            'customer_fields': list(client.customer_fields.all()),
            'customers': client.customer_page(offset, page_size=page_size),
            # This might be beyond the end but that's fine
            'offset': offset + page_size,
        }

        return render(request, 'client/api/customer_list.html', ctx)

    def post(self, request):
        client = Client.objects.get(slug=client_slug)
        form = CustomerForm(client, request.POST)

        if form.is_valid():
            try:
                customer = Customer(**customer)
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
                return Result(status=status.HTTTP_500_SERVER_ERROR)

        return response({'id': customer.id}, status=status.HTTP_201_CREATED)


class CustomerProfile(APIView):
    """Customer API
    """
    def get(self, customer_id):
        client = get_object_or_404(Client, slug='mdo')
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        return Response(customer)

    def post(self, customer_id):
        client = get_object_or_404(Client, slug='mdo')
        customer = get_object_or_404(Customer, client=client, id=customer_id)

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

        return response(customer)
