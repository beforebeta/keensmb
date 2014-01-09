from django.conf import settings
from django.http import Http404
from django.core.serializers import serialize

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from keen.core.models import Client, Customer
from keen.web.views.forms import CustomerForm


def response(content, content_type='application/json', **kw):
    if not isinstance(content, basestring):
        content = serialize('json', content)
    return Response(serialize('json', content), content_type=content_type, **kw)


class CustomerList(APIView):
    """Customer list API
    """
    def get(self, request):
        """Return one page of Customer objects along with some metadata
        """
        page_length = 25
        if 'page' in request.GET:
            try:
                page = int(request.GET['page'])
                if page < 1:
                    page = 1
            except ValueError:
                page = 1
        else:
            page = 1

        offset = (page - 1) * page_length
        client_slug = 'mdo'

        customers = Customer.objects.filter(client__slug=client_slug)[offset:offset + page_length]

        return response(customers)

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
