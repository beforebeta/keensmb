import datetime
import logging

from django import forms
from django.forms import DateField
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from localflavor.us.forms import USPhoneNumberField

from keen.core.models import CustomerField, Promotion


logger = logging.getLogger(__name__)


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
                      'phone', 'gender', 'program_of_interest')

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


class TrialRequestForm(forms.Form):

    name = forms.CharField(max_length=255, required=False)
    business = forms.CharField(max_length=255, required=False)
    phone = USPhoneNumberField(required=False)
    email = forms.EmailField(required=False)
    question = forms.CharField(max_length=255, required=False)
    comments = forms.CharField(max_length=255, required=False)

    def clean(self):
        data = super(TrialRequestForm, self).clean()

        name = data.get('name')
        business = data.get('business')
        if not (name or business):
            raise forms.ValidationError(
                _('Please provide your name and/or business name'))

        phone = data.get('phone')
        email = data.get('email')
        if not (phone or email):
            raise forms.ValidationError(
                _('Please provide either an email address or a phone number'))

        return data


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ('name', 'description', 'short_code', 'valid_from', 'valid_to', 'restrictions',
                  'additional_information', 'redemption_instructions', 'cta_text', 'image_url', 'banner_url', 'mediums', 'send_later', 'send_schedule')
        help_texts = {
            'valid_to': 'Provide the start date and expiry date for this promotion. Otherwise, it will continue indefinitely.',
        }
        widgets = {
            'send_later': forms.RadioSelect
        }

    valid_from = DateField(required=False, input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b. %d, %Y', '%b %d, %Y', '%B. %d, %Y', '%B %d, %Y'])
    valid_to = DateField(required=False, input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b. %d, %Y', '%b %d, %Y', '%B. %d, %Y', '%B %d, %Y'])
    send_schedule = DateField(required=False, input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b. %d, %Y', '%b %d, %Y', '%B. %d, %Y', '%B %d, %Y'])

    def clean_valid_from(self):
        valid_from = self.cleaned_data.get('valid_from', None)
        valid_to = self.cleaned_data.get('valid_to', None)
        if valid_from:
            if valid_from < datetime.date.today():
                raise forms.ValidationError("This date cannot be in the past")
        elif valid_to:
            raise forms.ValidationError("When does the promotion start?")
        return valid_from

    def clean_send_schedule(self):
        valid_to = self.cleaned_data.get('valid_to', None)
        send_schedule = self.cleaned_data.get('send_schedule', None)
        if send_schedule:
            if send_schedule < datetime.date.today():
                raise forms.ValidationError("This date cannot be in the past")
        return send_schedule

    def clean(self):
        logger.debug('Promotion form submitted: {0!r}'.format(self.data))
        cleaned_data = super(PromotionForm, self).clean()
        data = ((name[7:], self.data.getlist(name))
                 for name in self.data.keys()
                 if name.startswith('target_'))
        data = ((name, value if (len(value) != 1
                                 and '^^' not in value[0])
                 else value[0].split('^^')) for name, value in data)
        cleaned_data['target_audience'] = dict((name, value) for name, value
                                               in data if (
                                                   name and value and (
                                                       (len(value) > 1) or value[0])))
        return cleaned_data

    def clean_valid_to(self):
        valid_to = self.cleaned_data.get('valid_to', None)
        valid_from = self.cleaned_data.get('valid_from', None)
        if valid_to:
            if valid_from and valid_to < valid_from:
                raise forms.ValidationError("This date should be on or after the valid from date")
            if not valid_from and valid_to < datetime.date.today():
                raise forms.ValidationError("This date cannot be in the past")
        return valid_to
