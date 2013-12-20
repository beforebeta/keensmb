from django.db.models import Sum
from django.core.urlresolvers import reverse

from rest_framework.serializers import (
    DateTimeField,
    ModelSerializer,
    RelatedField,
    PrimaryKeyRelatedField,
    SlugRelatedField,
    SerializerMethodField,
    )

from keen.core.models import (
    Address,
    Location,
    Client,
    Customer,
    CustomerFieldGroup,
    CustomerField,
    Image,
    )
from keen.web.models import SignupForm


class DynamicSerializer(ModelSerializer):

    def __init__(self, *args, **kw):
        fields = kw.pop('fields', None)
        super(DynamicSerializer, self).__init__(*args, **kw)
        if fields:
            for field in set(self.fields.keys()) - set(fields):
                self.fields.pop(field)


class AddressSerializer(DynamicSerializer):

    class Meta:
        model = Address
        fields = ('street', 'city', 'postal_code',
                  'state_province', 'country', 'created', 'modified')


class LocationSerializer(DynamicSerializer):

    address = AddressSerializer()

    class Meta:
        model = Location
        fields = ('name', 'address', 'created', 'modified')


class CustomerFieldSerializer(DynamicSerializer):

    group = SlugRelatedField(slug_field='name')

    class Meta:
        model = CustomerField
        fields = ('name', 'title', 'type', 'required',
                  'group', 'width', 'created', 'modified')


class CustomerFieldGroupSerializer(DynamicSerializer):

    class Meta:
        model = CustomerFieldGroup
        fields = ('name', 'title', 'created', 'modified')


class ClientSerializer(DynamicSerializer):

    locations = LocationSerializer(many=True)
    main_location = SlugRelatedField(slug_field='name', required=False)
    customer_fields = CustomerFieldSerializer(many=True)

    class Meta:
        model = Client
        fields = ('slug', 'name', 'locations',
                  'main_location', 'customer_fields', 'created', 'modified')


class CustomerSerializer(DynamicSerializer):

    client = SlugRelatedField(slug_field='slug')

    class Meta:
        model = Customer
        fields = ('id', 'client', 'data', 'created', 'modified')


class ImageSerializer(DynamicSerializer):

    url = SerializerMethodField('get_url')

    def get_url(self, image):
        return image.file.url

    class Meta:
        model = Image
        fields = ('id', 'target', 'content_type', 'url', 'created',
                  'modified')


class SignupFormSerializer(DynamicSerializer):

    url = SerializerMethodField('get_url')
    edit_url = SerializerMethodField('get_edit_url')
    total_signups = SerializerMethodField('get_total_signups')
    total_visits = SerializerMethodField('get_total_visits')

    class Meta:
        model = SignupForm
        fields = ('slug', 'status', 'data', 'created', 'modified',
                  'url', 'edit_url', 'total_signups', 'total_visits')

    def get_url(self, form):
        return reverse('customer_signup', kwargs=dict(
            client_slug=form.client.slug, form_slug=form.slug))

    def get_edit_url(self, form):
        return reverse('client_signup_form_edit', kwargs=dict(slug=form.slug))

    def get_total_signups(self, form):
        return Customer.objects.filter(
            source__ref_source='signup', source__ref_id=form.id).count()

    def get_total_visits(self, form):
        return Customer.objects.filter(
            source__ref_source='signup', source__ref_id=form.id).aggregate(
                Sum('visitor__visits'))['visitor__visits__sum']
