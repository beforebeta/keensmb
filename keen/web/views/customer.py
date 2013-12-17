import logging

from django.db import DatabaseError
from django.shortcuts import render, get_object_or_404

from keen.core.models import Client, Customer, CustomerSource
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm

from tracking.models import Visitor


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
            if 'visitor' in request.session:
                try:
                    customer.visitor = Visitor.objects.get(uuid=request.session['visitor'])
                except Visitor.DoesNotExist:
                    logger.warn('Failed to locate Visitor wirh UUID=%s' % request.session['visitor'])

            customer.source, created = CustomerSource.objects.get_or_create(
                client=client, slug=form_slug)

            for name, value in form.cleaned_data.items():
                customer.data[name] = str(value)

            try:
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
            else:
                return render(request, 'customer/signup_success.html')
        else:
            logger.debug('Signup form validation error(s): %r' % form.errors)
    else:
        form = CustomerForm(client)

    context['form'] = form

    return render(request, 'customer/signup.html', context)
