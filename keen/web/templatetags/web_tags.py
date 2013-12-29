from django import template
from django.utils.safestring import mark_safe
from keen.core.models import *
from keen.web.models import HelpText

register = template.Library()

@register.filter(name='nonempty')
def nonempty(value):
    if not value:
        return mark_safe("&nbsp;")
    else:
        return mark_safe(value)

@register.filter
def filter_none(val):
    return val if val else ""

@register.filter(name='cf_display_name')
def cf_display_name(value):
    try:
        return mark_safe(CustomerField.objects.get(name=value).title)
    except:
        return value


@register.filter
def promotion_help_text(name):
    try:
        return Promotion._meta.get_field_by_name(name)[0].help_text
    except:
        return ""

# From http://djangosnippets.org/snippets/1259/
@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split(' ')[:-1]

    # Join the words and return
    return ' '.join(words) + '...'

@register.filter
def get_template_for_event(event):
    return "client/events/%s.html" % event.data['type']

@register.filter
def text_launched(tab):
    _tab = tab.lower()
    if _tab == 'upcoming':
        return 'Launching'
    else:
        return 'Launched'