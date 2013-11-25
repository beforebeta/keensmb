from django.contrib import admin

from keen.core.models import (
    Client,
    Customer,
    CustomerSource,
    Location,
    Address,
    CustomerFieldGroup,
    CustomerField,
)


class ClientAdmin(admin.ModelAdmin):
    pass

admin.site.register(Client, ClientAdmin)


class CustomerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Customer, CustomerAdmin)


class LocationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Location, LocationAdmin)


class AddressAdmin(admin.ModelAdmin):
    pass

admin.site.register(Address, AddressAdmin)


class CustomerFieldGroupAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomerFieldGroup, CustomerFieldGroupAdmin)


class CustomerFieldAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomerField, CustomerFieldAdmin)
