import logging

from django.db import DatabaseError
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from keen.core.models import Client, Customer, CustomerSource
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm
from keen.tasks import mailchimp_subscribe

from tracking.models import Visitor


logger = logging.getLogger(__name__)


def signup_view(request, client_slug, form_slug):
    client = get_object_or_404(Client, slug=client_slug)
    signup_form = get_object_or_404(SignupForm, client=client, slug=form_slug)
    try:
        visitor = Visitor.objects.get(pk=request.session.get('visitor'))
    except Visitor.DoesNotExist:
        logger.warn('Visitor does not exist')
    else:
        try:
            signup_form.visits = F('visits') + 1
            signup_form.visitors.add(visitor)
            signup_form.save()
        except DatabaseError:
            logger.exception('Failed to update SignupForm visitor')

    context = {
        'client': client,
        'form_data': signup_form.data,
    }

    if request.method == 'POST':
        form = CustomerForm(signup_form, request.POST)
        if form.is_valid():
            customer = Customer()
            customer.client = client
            if 'visitor' in request.session:
                try:
                    customer.visitor = Visitor.objects.get(
                        pk=request.session['visitor'])
                except Visitor.DoesNotExist:
                    logger.warn('Failed to locate Visitor')

            customer.source = CustomerSource.objects.filter(
                ref_source='signup', ref_id=signup_form.id).first()

            for name, value in form.cleaned_data.items():
                customer.data[name] = str(value)

            try:
                customer.save()
                mailchimp_new_customer(customer)
            except DatabaseError:
                logger.exception('Failed to save new customer')
            else:
                context['success'] = 'You have successfully signed up!'
                redirect_url = signup_form.data.get('redirectUrl')
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
        else:
            logger.debug('Signup form validation error(s): %r' % form.errors)
    else:
        form = CustomerForm(signup_form)

    context['form'] = form

    return render(request,
                  signup_form.data.get('template', 'customer/signup.html'),
                  context)


def mailchimp_new_customer(customer):
    if customer.client.ref_id_type != 'mailchimp':
        logger.warn('Client %s has no Mailchimp list ID' % customer.client.name)
    else:
        list_id = customer.client.ref_id
        email = customer.data['email']

        merge_vars = {
            'CUSTOMERID': customer.id,
            'FNAME': customer.data.get('first_name', ''),
            'LNAME': customer.data.get('last_name', ''),
            'FULLNAME': customer.data.get('full_name', ''),
            'NUMBER': customer.data.get('phone', ''),
            'ZIPCODE': customer.data.get('address__ipcode', ''),
            'BIRTHDAY': customer.data.get('dob', ''),
            'GENDER': customer.data.get('gender', ''),
            'SIGNUPNAME': '',
            'SIGNUPID': '',
        }

        if customer.source and customer.source.ref_source == 'signup':
            try:
                form = SignupForm.objects.get(id=customer.source.ref_id)
            except SignupForm.DoesNotExist:
                logger.warn('Customer signup form with id %s not found' %
                            customer.source.ref_id)
            else:
                merge_vars['SIGNUPNAME'] = form.data.get('pageTitle', '')
                merge_vars['SIGNUPID'] = form.id

        mailchimp_subscribe.delay(list_id, email, merge_vars,
                                  double_optin=False, update_existing=True,
                                  send_welcome=True)
