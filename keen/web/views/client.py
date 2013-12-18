import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie

from keen.core.models import Client, Customer, Location
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm
from keen.web.serializers import SignupFormSerializer


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def dashboard(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    context = {
        'client': client,
        'dashboard': client.get_dashboard()
    }
    return render(request, 'client/dashboard.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def promotions(request):
    render(request, 'client/promotions.html')


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def customers(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    q = Customer.objects.filter(client=client)

    context = {}
    context['client'] = client
    context['locations'] = list(client.locations.all())
    context['customer_fields'] = list(client.customer_fields.all())
    context['summary'] = {
        'total_customers': q.count(),
        'redeemers': 0,
        'new_signups': 0,
    }

    return render(request, 'client/customers.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def profile(request, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = Customer.objects.get(id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client

    return render(request, 'client/customers/customer_profile_view.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_list(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    forms = SignupForm.objects.filter(client=client).order_by('-status', 'slug')
    context = {
        'client': client,
        'forms': SignupFormSerializer(forms, many=True).data,
    }

    return render(request, 'client/signup-form-list.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_create(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    context = {
        'client': client,
    }
    return render(request, 'client/signup-form-create.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def business_profile(request):
    return None


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def customer_form(request, customer_id=None):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    if customer_id:
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        form = CustomerForm(client, initial=customer.data)
    else:
        form = CustomerForm(client)

    return render(request, 'client/customer_form.html', {'form': form})
