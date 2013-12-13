import os
import re
import logging
from hashlib import sha256
from base64 import b64decode

from django.conf import settings
from django.http import QueryDict, Http404, HttpResponseNotAllowed
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser

from keen.core.models import Client, Customer, Image
from keen.web.models import PageCustomerField, SignupForm
from keen.web.serializers import (
    ClientSerializer,
    CustomerSerializer,
    CustomerFieldSerializer,
    ImageSerializer,
    SignupFormSerializer,
)
from keen.web.forms import CustomerForm


logger = logging.getLogger(__name__)

field_name_re = re.compile(r'^[a-z_][a-z0-9_#]*$')


class IsClientUser(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user and
            request.session and
            'client' in request.session and
            request.session['client'] and
            request.session['client'].get('slug') == view.kwargs.get('client_slug')
        )


class ClientProfile(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
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
            available_fields = list(client.customer_fields.all().order_by('group_ranking'))

            try:
                page = PageCustomerField.objects.get(page='db', client=client)
            except PageCustomerField.DoesNotExist:
                display_fields = None
            else:
                display_fields = page.fields.split(',')

            if not display_fields:
                display_fields = [field.name for field in available_fields if field.required]

            data = {
                'available_customer_fields': CustomerFieldSerializer(
                    available_fields, many=True).data,
                'display_customer_fields': display_fields,
            }
        else:
            logger.warn('ClientProfile GET request for unknown part %r' % part)
            return Http404()

        return Response(data)

    @method_decorator(ensure_csrf_cookie)
    def put(self, request, client_slug, part=None):
        client = get_object_or_404(Client, slug=client_slug)

        if part == 'customer_fields':
            fields = request.DATA.get('display_customer_fields', [])
            page, created = PageCustomerField.objects.get_or_create(page='db', client=client)
            # ensure that we only save fields that are available for this clint
            client_fields = set(field.name for field in client.customer_fields.filter(name__in=fields))
            fields = [field for field in fields if field in client_fields]
            page.fields = ','.join(fields)
            page.save()
            data = {'display_customer_fields': fields}
        else:
            logger.warn('ClientProfile PUT request for unknown part %r' % part)
            return HttpResponseBadRequest()

        return Response(data)


class CustomerList(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
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
            customers = customers.extra(
                where=['cast(avals(data) as text) ~* %s'],
                params=[request.GET['search']])

        if 'order' in request.GET:
            order_by = request.GET['order'].split(',')
            fields = [field.lstrip('-') for field in order_by]
            # TODO: Use client.customer_fields to match field names AND
            # to add CAST to database query so it matches index that was
            # created by setup management command
            customers = customers.extra(
                select=dict(
                    (field, "upper(core_customer.data -> '%s')" % field)
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

    @method_decorator(ensure_csrf_cookie)
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
                return Response(status=status.HTTTP_500_SERVER_ERROR)

        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


class CustomerProfile(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, client_slug, customer_id):
        """Retrieve customer profile
        """
        customer = get_object_or_404(Customer, client__slug=client_slug, id=customer_id)
        return Response(CustomerSerializer(customer).data)

    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, client_slug, customer_id):
        customer = get_object_or_404(Customer, client__slug=client_slug, id=customer_id)

        customer.delete()

        return Response('Deleted')

    @method_decorator(ensure_csrf_cookie)
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


@ensure_csrf_cookie
@api_view(['GET'])
def current_client_view(request):
    try:
        client_slug = request.session['client']['slug']
    except KeyError:
        return Http404()

    client = get_object_or_404(Client, slug=client_slug)

    return Response(ClientSerializer(client).data)


class SignupFormList(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, client_slug):
        client = get_object_or_404(Client, slug=client_slug)

        if 'check' in request.GET:
            # check if form with this permalink exists
            permalink = request.GET['check'].strip()
            if not permalink:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            found = client.signup_forms.filter(permalink=permalink).exists()
            return Response(('not found', 'found')[found])
        else:
            forms = list(client.signup_forms.all())
            return Response(SignupFormSerializer(forms, many=True).data)

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, client_slug):
        client = get_object_or_404(Client, slug=client_slug)

        try:
            slug = request.DATA['slug']
            data = request.DATA['data']
        except KeyError:
            logger.exception('Missing mandatory field %r' % request.DATA)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        form, created = SignupForm.objects.get_or_create(client=client, slug=slug)
        if not created:
            logger.error('Form with slug %s already exists' % slug)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        form.data = data
        try:
            form.save()
        except DatabaseError:
            logger.exception('Failed to create signup form')
            raise

        return Response('', status=status.HTTP_201_CREATED)


class SignupFormView(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, client_slug, form_slug):
        """Retrieve form information
        """
        client = get_object_or_404(Client, slug=client_slug)
        form = get_object_or_404(SignupForm, client=client, slug=form_slug)

        return Response(SignupFormSerializer(form).data)

    @method_decorator(ensure_csrf_cookie)
    def put(self, request, client_slug, form_slug):
        """Update form information
        """
        client = get_object_or_404(Client, slug=client_slug)
        form = get_object_or_404(SignupForm, client=client, slug=form_slug)

        if 'data' in request.DATA:
            form.data = request.DATA['data']

        try:
            form.save()
        except DatabaseError:
            logger.exception('Failed to save signup form')
            raise

        return Response(status=status.HTTP_204_NO_CONTENT)

    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, client_slug, form_slg):
        client = get_object_or_404(Client, slug=client_slug)
        form = get_object_or_404(SignupForm, clinet=client, slug=form_slug)

        try:
            form.delete()
        except DatabaseError:
            logger.exception('Failed to delete signup form')
            raise

        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageList(APIView):

    permission_classes = (IsClientUser,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, client_slug):
        """Retrieve list of images
        """
        client = get_object_or_404(Client, slug=client_slug)

        return Response(ImageSerializer(client.images.all(), many=True).data)

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, client_slug):
        """Upload new image
        """
        client = get_object_or_404(Client, slug=client_slug)

        try:
            content_type = request.DATA['type']
            content = request.DATA['data']
        except KeyError:
            logger.exception('Failed to get expected request data')
            return Response(status=status.HTTP_BAD_REQUEST)

        try:
            content = b64decode(content)
        except TypeError:
            logger.exception('Failed to decode image content using BASE64')
            return Response(status=status.HTTP_BAD_REQUEST)

        name = '.'.join((sha256(content).hexdigest(),
                         content_type.split('/', 1)[1]))
        name = os.path.join('client', client.slug, 'images', name)
        content = default_storage.save(name, ContentFile(content))

        image = Image()
        image.client = client
        image.file = content
        image.content_type = content_type

        try:
            image.save()
        except DatabaseError:
            logger.exception('Failed to save image')
            raise

        return Response(ImageSerializer(image).data, status=status.HTTP_201_CREATED)

    @method_decorator(ensure_csrf_cookie)
    def delete(self, client_slug, image_id):
        """Delete image
        """
        client = get_object_or_404(Client, slug=client_slug)
        try:
            Image.objects.get(client=client, id=int(image_id)).delete()
        except Image.DoesNotExist:
            logger.error('Attempt to delete non-existing image')
            status = status.HTTP_404_NOT_FOUND
        except DatabaseError:
            logger.exception('Failed to delete image')
            status = status.HTTP_500_INTERNAL_SERVICE_ERROR
        else:
            status = status.HTTP_204_NO_CONTENT

        return Response(status=status)
