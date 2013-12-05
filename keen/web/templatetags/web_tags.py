from django import template
from django.utils.safestring import mark_safe
from keen.core.models import *

register = template.Library()

@register.filter(name='nonempty')
def nonempty(value):
    if not value:
        return mark_safe("&nbsp;")
    else:
        return mark_safe(value)


@register.filter(name='cf_display_name')
def cf_display_name(value):
    try:
        return mark_safe(CustomerField.objects.get(name=value).title)
    except:
        return value