from rest_framework.serializers import (
    ModelSerializer,
    RelatedField,
    PrimaryKeyRelatedField,
    SlugRelatedField,
    )

from keen.core.models import (
    Address,
    Location,
    Client,
    Customer,
    CustomerFieldGroup,
    CustomerField,
    )


class DynamicSerializer(ModelSerializer):

    def __init__(self, *args, **kw):
        exclude_fields = kw.pop('exclude_fields', None)
        super(DynamicSerializer, self).__init__(*args, **kw)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field, None)


class AddressSerializer(DynamicSerializer):

    class Meta:
        model = Address
        fields = ('created', 'modified', 'street', 'city', 'postal_code',
                  'state_province', 'country')


class LocationSerializer(DynamicSerializer):

    address = AddressSerializer()

    class Meta:
        model = Location
        fields = ('created', 'modified', 'name', 'address')


class CustomerFieldSerializer(DynamicSerializer):

    class Meta:
        model = CustomerField
        fields = ('created', 'modified', 'name', 'title', 'type', 'required')


class CustomerFieldGroupSerializer(DynamicSerializer):

    class Meta:
        model = CustomerFieldGroup
        fields = ('created', 'modified', 'name', 'title')


class ClientSerializer(DynamicSerializer):

    locations = LocationSerializer(many=True)
    main_location = SlugRelatedField(slug_field='name', required=False)
    customer_fields = CustomerFieldSerializer(many=True)

    class Meta:
        model = Client
        fields = ('created', 'modified', 'slug', 'name', 'locations',
                  'main_location', 'customer_fields')


class CustomerSerializer(DynamicSerializer):

    client = SlugRelatedField(slug_field='slug')

    class Meta:
        model = Customer
        fields = ('id','created', 'modified',  'client', 'data')
