from django import template


register = template.Library()


@register.filter
def hstore(value, key, default=''):
    return value.get(key, default)
