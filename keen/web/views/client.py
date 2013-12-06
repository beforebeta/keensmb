import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext

from keen.core.models import Client, Customer, Location
from keen.web.forms import CustomerForm


logger = logging.getLogger(__name__)


@login_required(login_url='/#signin')
def dashboard(request):
    return render(request, 'client/dashboard.html')


@login_required(login_url='/#signin')
def promotions(request):
    render(request, 'client/promotions.html')


@login_required(login_url='/#signin')
def customers(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client']['slug'])
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


@login_required(login_url='/#signin')
def profile(request, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = Customer.objects.get(id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    print customer.get_email()
    return render_to_response('client/customers/customer_profile_view.html', context, context_instance=RequestContext(request))


@login_required(login_url='/#signin')
def signup_form_create(request):
    return render(request, 'client/signup-form-create.html')


@login_required(login_url='/#signin')
def business_profile(request):
    return None


@login_required(login_url='/#signin')
def customer_form(request, customer_id=None):
    client = get_object_or_404(Client, slug=request.session['client']['slug'])
    if customer_id:
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        form = CustomerForm(client, initial=customer.data)
    else:
        form = CustomerForm(client)
    return render(request, 'client/customer_form.html', {'form': form})
