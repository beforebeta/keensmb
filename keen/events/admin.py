from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from keen.events.models import (
    Event
)

class EventAdmin(admin.ModelAdmin):
    list_display = ('client', 'is_aggregate','occurrence_datetime')

admin.site.register(Event, EventAdmin)