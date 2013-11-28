from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='nonempty')
def nonempty(value):
    if not value:
        return mark_safe("&nbsp;")
    else:
        return mark_safe(value)