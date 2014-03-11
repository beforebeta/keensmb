import logging

from django.db import DatabaseError
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from keen.core.models import Client, Customer, CustomerSource
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm
from keen.tasks import mailchimp_subscribe, send_email

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
        form = CustomerForm(client, request.POST)
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
                if value is not None:
                    customer.data[name] = str(value)

            try:
                customer.save()
            except DatabaseError:
                logger.exception('Failed to save new customer')
            else:
                mailchimp_new_customer(signup_form, customer)
                new_customer_notification(signup_form, customer)
                new_customer_confirmation(signup_form, customer)
                context['success'] = 'You have successfully signed up!'
                redirect_url = signup_form.data.get('redirectUrl')
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
        else:
            logger.debug('Signup form validation error(s): %r' % form.errors)
    else:
        form = CustomerForm(client)

    context['form'] = form

    return render(request,
                  signup_form.data.get('template', 'customer/signup.html'),
                  context)


def mailchimp_new_customer(signup_form, customer):
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

        merge_vars['SIGNUPNAME'] = signup_form.data.get('pageTitle', '')
        merge_vars['SIGNUPID'] = signup_form.id

        mailchimp_subscribe.delay(list_id, email, merge_vars,
                                  double_optin=False, update_existing=True,
                                  send_welcome=True)


NOTIFICATION_BODY = '''
A new customer signed up using the signup form you created on Keen.
Here is the information they provided:

'''

def new_customer_notification(signup_form, customer):
    if signup_form.submission_notification:
        recipients = filter(None, (email.strip() for email in signup_form.submission_notification.split(',')))
        if recipients:
            subject = 'Keen - new signup from {0}'.format(signup_form.data['pageTitle'])
            body = NOTIFICATION_BODY + (
                '\n'.join('{0}: {1}'.format(name, value) for name, value in
                        customer.data.items() if name and value))
            send_email.delay(subject, body, recipients)


def new_customer_confirmation(signup_form, customer):
    if (customer.data['email'] and signup_form.submission_confirmation_html and
        signup_form.signup_confirmation_subject):
        recipients = [customer.data['email']]
        subject = signup_form.signup_confirmation_subject
        body = signup_form.submission_confirmation_html
        send_email.delay(subject, body, recipients)
