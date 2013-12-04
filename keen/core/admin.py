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
    list_display = ('client', 'source', 'get_name', 'get_email', 'enrichment_status','data')

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
    list_display = ('group', 'group_ranking', 'name','title')

admin.site.register(CustomerField, CustomerFieldAdmin)
