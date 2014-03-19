from django.db.models import Sum
from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework.serializers import (
    Field,
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
        fields = ('name', 'title', 'type', 'required', 'choices', 'group',
                  'width', 'created', 'modified')


class CustomerFieldGroupSerializer(DynamicSerializer):

    class Meta:
        model = CustomerFieldGroup
        fields = ('name', 'title', 'created', 'modified')


class ClientSerializer(DynamicSerializer):

    locations = LocationSerializer(many=True)
    main_location = SlugRelatedField(slug_field='name', required=False)
    customer_fields = SerializerMethodField('get_customer_fields')

    class Meta:
        model = Client
        fields = ('slug', 'name', 'locations',
                  'main_location', 'customer_fields', 'created', 'modified')

    def get_customer_fields(self, client):
        return CustomerFieldSerializer(client.customer_fields.select_related('group').all(), many=True).data


class CustomerSerializer(DynamicSerializer):

    client = SlugRelatedField(slug_field='slug')

    class Meta:
        model = Customer
        fields = ('id', 'client', 'data', 'created', 'modified',
                  'enrichment_status', 'enrichment_date')


class ImageSerializer(DynamicSerializer):

    url = SerializerMethodField('get_url')

    def get_url(self, image):
        return image.file.url

    class Meta:
        model = Image
        fields = ('id', 'target', 'content_type', 'url', 'created',
                  'modified')


class SignupFormSerializer(DynamicSerializer):

    url = Field()
    edit_url = SerializerMethodField('get_edit_url')
    total_signups = SerializerMethodField('get_total_signups')
    unique_visits = SerializerMethodField('get_unique_visits')
    thumb_url = SerializerMethodField('get_thumb_url')

    class Meta:
        model = SignupForm
        fields = ('slug', 'status', 'data', 'created', 'modified',
                  'url', 'edit_url', 'total_signups', 'visits',
                  'unique_visits', 'thumb_url',
                  )

    def get_edit_url(self, form):
        return reverse('client_signup_form_edit', kwargs=dict(slug=form.slug))

    def get_total_signups(self, form):
        return Customer.objects.filter(
            source__ref_source='signup', source__ref_id=form.id).count()

    def get_total_visits(self, form):
        return Customer.objects.filter(
            source__ref_source='signup', source__ref_id=form.id).aggregate(
                Sum('visitor__visits'))['visitor__visits__sum'] or 0

    def get_unique_visits(self, form):
        return form.visitors.count()

    def get_thumb_url(self, form):
        return '%s/signup-form-thumbnails/%s' % (
            settings.MEDIA_URL, form.data.get('thumbnail', 'default.png'))
