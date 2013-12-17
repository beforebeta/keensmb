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
        fields = ('id', 'target', 'content_type', 'url', 'created', 'modified')


class SignupFormSerializer(DynamicSerializer):

    class Meta:
        model = SignupForm
        fields = ('slug', 'status', 'data', 'created', 'modified')
