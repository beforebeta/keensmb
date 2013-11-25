from django.conf import settings
from django.http import Http404
from django.core.serializers import serialize

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import deform

from keen.core.models import Client, Customer
from keen.web.views.api.schema import NewCustomerSchema, CustomerSchema


def response(content, content_type='application/json', **kw):
    if not isinstance(content, basestring):
        content = serialize('json', content)
    return Response(serialize('json', content), content_type=content_type, **kw)


class CusomerList(APIView):
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
        form = deform.Form(NewCustomerSchema().bind(client=client))

        try:
            customer = form.validate(request.POST.items())
        except deform.ValidationFailure, e:
            return Response(e.render(), status=status.HTTP_400_BAD_REQUEST)

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
    def get(self, id):
        customer = Customer.objects.get(id=id)
        return Response(customer)

    @transaction.commit_on_success
    def post(self, id):
        customer = Customer.objects.get(id=id)

        try:
            # Always clone() if sub-nodes are going to be modified
            schema = CustomerSchema().clone()
            schema.bind(client=client)
            form = deformForm(schema)
            data = form.validate(request.POST.items())
        except deform.ValidationError, e:
            return response(e.render())

        try:
            customer.data.update(form)
            customer.save()
        except DatabaseError:
            logger.exception('Failed to update customer')
            return response({'error': 'Failed to save customer profile',
                             status=status.HTTP_400_BAD_REQUEST)

        return response(customer)
