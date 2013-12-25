from django.contrib import admin

from keen.web.models import (
    Dashboard,
    PageCustomerField,
    SignupForm,
    TrialRequest,
)


class DashboardAdmin(admin.ModelAdmin):
    list_display = ('total_customers', 'new_customers','promotions_this_month', 'redemptions')


class PageCustomerFieldAdmin(admin.ModelAdmin):
    pass


class SignupFormAdmin(admin.ModelAdmin):
    pass


class TrialRequestAdmin(admin.ModelAdmin):
    list_display = ('name_and_business', 'phone', 'email')

    def name_and_business(self, obj):
        return '/'.join((obj.name, obj.business))

    name_and_business.short_description = 'Name/Business'


admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(PageCustomerField, PageCustomerFieldAdmin)
admin.site.register(SignupForm, SignupFormAdmin)
admin.site.register(TrialRequest, TrialRequestAdmin)
