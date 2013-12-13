from rest_framework.serializers import (
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
                  'state_province', 'country')


class LocationSerializer(DynamicSerializer):

    address = AddressSerializer()

    class Meta:
        model = Location
        fields = ('name', 'address')


class CustomerFieldSerializer(DynamicSerializer):

    group = SlugRelatedField(slug_field='name')

    class Meta:
        model = CustomerField
        fields = ('name', 'title', 'type', 'required',
                  'group', 'width')


class CustomerFieldGroupSerializer(DynamicSerializer):

    class Meta:
        model = CustomerFieldGroup
        fields = ('name', 'title')


class ClientSerializer(DynamicSerializer):

    locations = LocationSerializer(many=True)
    main_location = SlugRelatedField(slug_field='name', required=False)
    customer_fields = CustomerFieldSerializer(many=True)

    class Meta:
        model = Client
        fields = ('slug', 'name', 'locations',
                  'main_location', 'customer_fields')


class CustomerSerializer(DynamicSerializer):

    client = SlugRelatedField(slug_field='slug')

    class Meta:
        model = Customer
        fields = ('id', 'client', 'data')


class ImageSerializer(DynamicSerializer):

    url = SerializerMethodField('get_url')

    def get_url(self, image):
        return image.file.url

    class Meta:
        model = Image
        fields = ('id', 'type', 'content_type', 'url')


class SignupFormSerializer(DynamicSerializer):

    fields = CustomerFieldSerializer(many=True)

    class Meta:
        model = SignupForm
        fields = ('slug', 'fields', 'status', 'data')
