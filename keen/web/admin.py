from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from keen.web.models import (
    Dashboard
)

class DashboardAdmin(admin.ModelAdmin):
    list_display = ('total_customers', 'new_customers','promotions_this_month', 'redemptions')

admin.site.register(Dashboard, DashboardAdmin)