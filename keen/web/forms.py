from django import forms

from keen.core.models import CustomerField


def form_field_builder(field_type, widget_type):
    def builder(field):
        return field_type(
            required=field.required,
            label=field.title,
            widget=widget_type(attrs={
                'id': field.name,
                'name': field.name,
                'required': field.required,
                'placeholder': field.title + ('', ' *')[field.required],
            }),
        )

    return builder


FIELD_TYPE_MAP = dict(
    (name, form_field_builder(field, widget))
    for name, field, widget in (
        (CustomerField.FIELD_TYPES.string, forms.CharField, forms.TextInput),
        (CustomerField.FIELD_TYPES.date, forms.DateField, forms.TextInput),
        (CustomerField.FIELD_TYPES.int, forms.IntegerField, forms.TextInput),
        (CustomerField.FIELD_TYPES.email, forms.EmailField, forms.TextInput),
        (CustomerField.FIELD_TYPES.url, forms.URLField, forms.TextInput),
        (CustomerField.FIELD_TYPES.float, forms.FloatField, forms.TextInput),
        (CustomerField.FIELD_TYPES.location, forms.CharField, forms.TextInput),
        (CustomerField.FIELD_TYPES.bool, forms.BooleanField,
         forms.CheckboxInput),
    )
)


class FieldSet(object):

    def __init__(self, title):
        self.title = title
        self.fields = []


class CustomerForm(forms.Form):
    """Dynamically built customer form
    """
    DEFAULT_FIELDS = ('full_name', 'email', 'dob', 'address__zipcode',
                      'phone', 'gender')

    def __init__(self, client, *args, **kw):
        super(CustomerForm, self).__init__(*args, **kw)

        # We will use fieldsets to group fields on form
        # self.fieldsets = {}

        # Add fields to form. Pointless for now since set of signup form fields
        # is hardcoded but it should come from SignupForm model in the future
        self.fields = dict((field.name, FIELD_TYPE_MAP[field.type](field))
                           for field in CustomerField.objects.filter(
                               client=client,
                               name__in=self.DEFAULT_FIELDS).order_by('group'))
