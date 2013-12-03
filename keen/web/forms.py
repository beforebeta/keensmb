from django import forms
from django.forms.forms import BoundField
from keen.core.models import *

FIELD_TYPE_MAP = {
    CustomerField.FIELD_TYPES.string: forms.CharField,
    CustomerField.FIELD_TYPES.date: forms.DateField,
    CustomerField.FIELD_TYPES.int: forms.IntegerField,
    CustomerField.FIELD_TYPES.email: forms.EmailField,
    CustomerField.FIELD_TYPES.url: forms.URLField,
    CustomerField.FIELD_TYPES.float: forms.FloatField,
    CustomerField.FIELD_TYPES.location: forms.CharField,
    CustomerField.FIELD_TYPES.bool: forms.BooleanField,
}

class FieldSet(object):

    def __init__(self, title):
        self.title = title
        self.fields = []


class CustomerForm(forms.Form):
    """Dynamically built customer form
    """
    def __init__(self, client, *args, **kw):
        super(CustomerForm, self).__init__(*args, **kw)
        self.fieldsets = {}
        for field in client.customer_fields.order_by('group'):
            self.fields[field.name] = form_field = FIELD_TYPE_MAP[field.type](
                required=field.required,
                label=field.title,
            )
            # Form is flat so we add fieldsets attribute to allow for grouping
            # imput elements
            group = field.group
            if group.name not in self.fieldsets:
                self.fieldsets[group.name] = FieldSet(group.title)
            self.fieldsets[group.name].fields.append(
                BoundField(self, form_field, 'data_{0}'.format(field.name)))
