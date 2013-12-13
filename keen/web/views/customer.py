import logging

from django.db import DatabaseError
from django.shortcuts import render, get_object_or_404

from keen.core.models import Client, Customer, CustomerSource
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm


logger = logging.getLogger(__name__)


def signup_view(request, client_slug, form_slug):
    client = get_object_or_404(Client, slug=client_slug)
    signup_form = get_object_or_404(SignupForm, client=client, slug=form_slug)
    context = {
        'client': client,
        'form_data': signup_form.data,
    }

    if request.method == 'POST':
        form = CustomerForm(client, request.POST)
        if form.is_valid():
            customer = Customer()
            customer.client = client
            customer.source = CustomerSource.objects.filter(
                slug=form_slug).first()

            for name, value in form.cleaned_data.items():
                customer.data[name] = value

            try:
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
            else:
                return render(request, 'customer/signup_success.html')
    else:
        form = CustomerForm(client)

    context['form'] = form

    return render(request, 'customer/signup.html', context)
