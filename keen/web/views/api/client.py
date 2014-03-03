import os
import re
import logging
from hashlib import sha256
from base64 import b64decode
from uuid import uuid4
import functools

from django.conf import settings
from django.http import QueryDict, Http404, HttpResponseNotAllowed
from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template import Context, Template
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser

from keen.core.models import Client, Customer, Image, CustomerSource
from keen.web.models import PageCustomerField, SignupForm
from keen.web.serializers import (
    ClientSerializer,
    CustomerSerializer,
    CustomerFieldSerializer,
    ImageSerializer,
    SignupFormSerializer,
)
from keen.web.forms import CustomerForm
from keen.tasks import take_screenshot, send_email


logger = logging.getLogger(__name__)

field_name_re = re.compile(r'^[a-z_][a-z0-9_#]*$')


class IsClientUser(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user and
            request.session and
            'client_slug' in request.session and
            request.session['client_slug'] == view.kwargs.get('client_slug')
        )


def schedule_screenshot(request, form):
    url = request.build_absolute_uri(
        reverse('customer_signup', kwargs={
            'client_slug': form.client.slug,
            'form_slug': form.slug,
        })
    )
    take_screenshot.delay(
        url,
        os.path.join(
            settings.MEDIA_ROOT, 'signup-form-thumbnails', form.data['thumbnail']),
        (142, 116),
    )


def client_api(func):
    """
    Decorate client API callable.
    Replaces client_slug positional argument with Client instance.
    Ensures user has permission to access that client
    """
    @functools.wraps(func)
    @ensure_csrf_cookie
    def wrapper(request, client_slug, *args, **kw):
        try:
            assert client_slug == request.session['client_slug']
        except (AssertionError, AttributeError, KeyError):
            # No request.session or no request.session['client_slug'] or it's
            # not the same as client_slug parameter
            return Response(status=HTTP_403_FORBIDDEN)
        client = get_object_or_404(Client, slug=client_slug)
        # Call original with client_slug replaced with client object
        return func(request, client, *args, **kw)

    return wrapper


class ClientAPIView(APIView):
    """Base class that used client_api to decorate its methods
    """
    permission_classes = ()

    def __init__(self, *args, **kw):
        super(ClientAPIView, self).__init__(*args, **kw)
        for name in self.http_method_names:
            meth = getattr(self, name, None)
            if callable(meth):
                setattr(self, name, client_api(meth))


class ClientProfile(ClientAPIView):

    def get(self, request, client, part=None):
        if part is None:
            data = ClientSerializer(client).data
        elif part == 'summary':
            data = {
                'total_customers': client.customers.count(),
                'redeemers': 0,
                'new_signups': 0,
            }
        elif part == 'customer_fields':
            available_fields = list(client.customer_fields.select_related('group')
                                    .order_by('group_ranking'))

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

    def put(self, request, client, part=None):

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


class CustomerList(ClientAPIView):

    def get(self, request, client):
        """Return one page of Customer objects
        """
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

    def post(self, request, client):
        """Create new customer
        """
        form = CustomerForm(client, request.POST)

        if form.is_valid():
            try:
                customer = Customer(**customer)
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
                return Response(status=HTTTP_500_INTERNAL_SERVER_ERROR)

        return Response(CustomerSerializer(customer).data, status=HTTP_201_CREATED)


class CustomerProfile(ClientAPIView):

    def get(self, request, client, customer_id):
        """Retrieve customer profile
        """
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        return Response(CustomerSerializer(customer).data)

    def delete(self, request, client, customer_id):
        customer = get_object_or_404(Customer, client=client, id=customer_id)

        customer.delete()

        return Response('Deleted')

    def post(self, request, client, customer_id):
        """Update customer profile
        """
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
                                status=HTTP_400_BAD_REQUEST)

        return Response(CustomerSerializer(customer).data)


@ensure_csrf_cookie
@api_view(['GET'])
def current_client_view(request):
    try:
        client_slug = request.session['client_slug']
    except KeyError:
        return Response(status=403)
    client = get_object_or_404(Client, slug=client_slug)
    return Response(ClientSerializer(client).data)


@ensure_csrf_cookie
@api_view(['GET'])
def num_customers(request):
    try:
        client_slug = request.session['client_slug']
    except KeyError:
        return Response(status=403)
    client = get_object_or_404(Client, slug=client_slug)
    data = ((name, request.GET.getlist(name)) for name in request.GET.keys())
    data = dict((name, value) for name, value in data if name and value)
    result = client.customers_by_data(data).count()
    return Response(result)


class SignupFormList(ClientAPIView):

    def get(self, request, client):
        forms = SignupForm.objects.filter(client=client)\
                .exclude(slug__startswith='preview-')\
                .order_by('-status', 'slug')

        return Response(SignupFormSerializer(forms, many=True).data)

    def post(self, request, client):
        try:
            slug = request.DATA['slug']
            data = request.DATA['data']
        except KeyError:
            logger.exception('Missing mandatory field %r' % request.DATA)
            return Response(status=HTTP_400_BAD_REQUEST)

        status = request.DATA.get('status', 'draft')
        if status not in ('draft', 'published'):
            logger.error('Illegal signup form status %s' % status)
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                data['thumbnail'] = '%s.png' % uuid4().hex
                form = SignupForm.objects.create(client=client, slug=slug,
                                                 status=status, data=data)

                CustomerSource.objects.create(
                    client=client, slug='signup:%s' % slug,
                    ref_source='signup', ref_id=form.id).save()
        except DatabaseError:
            logger.exception('Failed to create signup form')
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            schedule_screenshot(request, form)

        return Response(status=HTTP_201_CREATED)


class SignupFormView(ClientAPIView):

    def get(self, request, client, form_slug):
        """Retrieve form information
        """
        form = get_object_or_404(SignupForm, client=client, slug=form_slug)

        return Response(SignupFormSerializer(form).data)

    def put(self, request, client, form_slug):
        """Update form information
        """
        form = get_object_or_404(SignupForm, client=client, slug=form_slug)

        if 'status' in request.DATA:
            status = request.DATA['status']
            if status in ('draft', 'published'):
                form.status = status
            else:
                logger.error('Illegal signup form status %s' % status)
                return Response(status=HTTP_400_BAD_REQUEST)

        if 'data' in request.DATA:
            form.data.update(request.DATA['data'])

        # FIXME: remove previous thumbail
        form.data['thumbnail'] = '%s.png' % uuid4().hex

        try:
            form.save()
        except DatabaseError:
            logger.exception('Failed to save signup form')
            raise
        else:
            schedule_screenshot(request, form)

        return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, client, form_slg):
        form = get_object_or_404(SignupForm, clinet=client, slug=form_slug)
        try:
            with transaction.atomic():
                CustomerSource.objects.filter(ref_source='signup',
                                              ref_id=form.id).delete()
                form.delete()
        except DatabaseError:
            logger.exception('Failed to delete signup form')
            raise
        return Response(status=HTTP_204_NO_CONTENT)


class ImageList(ClientAPIView):

    def get(self, request, client):
        """Retrieve list of images
        """
        return Response(ImageSerializer(client.images.all(), many=True).data)

    def post(self, request, client):
        """Upload new image
        """
        try:
            content_type = request.DATA['type']
            content = request.DATA['data']
            target = request.DATA['target']
        except KeyError:
            logger.exception('Failed to get expected request data: %r' % request.DATA.keys())
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            content = b64decode(content)
        except TypeError:
            logger.exception('Failed to decode image content using BASE64')
            return Response(status=HTTP_400_BAD_REQUEST)

        name = '.'.join((sha256(content).hexdigest(),
                         content_type.split('/', 1)[1]))
        name = os.path.join('client', client.slug, 'images', name)
        content = default_storage.save(name, ContentFile(content))

        image = Image()
        image.client = client
        image.file = content
        image.content_type = content_type
        image.target = target

        try:
            image.save()
        except DatabaseError:
            logger.exception('Failed to save image')
            raise

        return Response(ImageSerializer(image).data, status=HTTP_201_CREATED)

    def delete(self, client, image_id):
        """Delete image
        """
        try:
            Image.objects.get(client=client, id=int(image_id)).delete()
        except Image.DoesNotExist:
            logger.error('Attempt to delete non-existing image')
            status = HTTP_404_NOT_FOUND
        except DatabaseError:
            logger.exception('Failed to delete image')
            status = HTTP_500_INTERNAL_SERVICE_ERROR
        else:
            status = HTTP_204_NO_CONTENT

        return Response(status=status)
