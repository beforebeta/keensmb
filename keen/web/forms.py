import datetime

from django import forms
from django.forms import DateField
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.utils.html import format_html

from localflavor.us.forms import USPhoneNumberField

from keen.core.models import CustomerField, Promotion


class CustomDateInput(forms.DateInput):

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {'class': 'form-control datepicker'}
        else:
            attrs['class'] = ' '.join((attrs.get('class', ''), 'form-control datepicker'))

        return format_html('''
            <div class="input-group">
                {0}
                <span class="input-group-btn">
                    <button class="btn btn-calendar" type="button">
                        <span class="fui-calendar"></span>
                    </button>
                </span>
            </div>
            ''', super(CustomDateInput, self).render(name, value, attrs))


class CustomSelect(forms.Select):

    def render_options(self, choices, selected_choices):
        options = super(CustomSelect, self).render_options( choices, selected_choices)
        return format_html('''
            <option value="" {0} disabled>{1}</option>
            {2}
            ''', ('' if selected_choices else 'selected'), self.label_tag, options)


def form_field_builder(field_class, widget_class):
    def builder(field, properties):
        attrs = {
            'id': field.name,
            'name': field.name,
            'placeholder': field.title + ('', ' *')[field.required],
            'class': 'form-control',
        }
        if field.required:
            attrs['required'] = field.required
        widget = widget_class(attrs=attrs)
        form_field = field_class(required=field.required, label=field.alt_title or field.title, widget=widget)
        form_field.choices = field.choices
        form_field.properties = properties
        return form_field

    return builder


FIELD_TYPE_MAP = dict(
    (data_type, form_field_builder(field_class, widget_class))
    for data_type, field_class, widget_class in (
        (CustomerField.FIELD_TYPES.string, forms.CharField, forms.TextInput),
        (CustomerField.FIELD_TYPES.date, forms.DateField, CustomDateInput),
        (CustomerField.FIELD_TYPES.int, forms.IntegerField, forms.TextInput),
        (CustomerField.FIELD_TYPES.email, forms.EmailField, forms.EmailInput),
        (CustomerField.FIELD_TYPES.url, forms.URLField, forms.URLInput),
        (CustomerField.FIELD_TYPES.float, forms.FloatField, forms.TextInput),
        (CustomerField.FIELD_TYPES.location, forms.CharField, forms.TextInput),
        (CustomerField.FIELD_TYPES.bool, forms.CharField, forms.TextInput),
    )
)


class CustomerForm(forms.Form):
    """Dynamically built customer form
    """
    FIXED_FIELDS = ('full_name', 'email')

    def __init__(self, signup_form, *args, **kw):
        super(CustomerForm, self).__init__(*args, **kw)

        client = signup_form.client

        extra_fields = signup_form.data.get('extra_fields', [])
        extra_fields_map = dict(
            (field['name'], field) for field in extra_fields
        )
        # ordered list of all field names
        field_names = self.FIXED_FIELDS + tuple(field['name'] for field in extra_fields)

        field_cache = dict(
            (field.name, field) for field in CustomerField.objects.filter(
                client=client, name__in=field_names)
        )
        # ordered list of CustomerField objects
        fields = (field_cache[name] for name in field_names)

        self.fields = SortedDict(
            (field.name, FIELD_TYPE_MAP[field.type](field, extra_fields_map.get(field.name)))
            for field in fields)


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

    #def clean(self):
    #    cleaned_data = super(PromotionForm, self).clean()
    #    valid_to = self.cleaned_data.get('valid_to', None)
    #    valid_from = self.cleaned_data.get('valid_from', None)
    #    if valid_to:
    #        if valid_from:
    #            if valid_to < valid_from:
    #                #self._errors["valid_to"] = ErrorList(["This date should be on or after the valid from date"])
    #                raise forms.ValidationError({"valid_to": "This date should be on or after the valid from date"})
    #        else:
    #            raise forms.ValidationError({"valid_from": "Please provide the date the promotion is valid from"})
    #    return cleaned_data

    def clean_valid_to(self):
        valid_to = self.cleaned_data.get('valid_to', None)
        valid_from = self.cleaned_data.get('valid_from', None)
        if valid_to:
            if valid_from and valid_to < valid_from:
                raise forms.ValidationError("This date should be on or after the valid from date")
            if not valid_from and valid_to < datetime.date.today():
                raise forms.ValidationError("This date cannot be in the past")
        return valid_to
