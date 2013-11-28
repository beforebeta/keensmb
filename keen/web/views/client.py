import logging

from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext

from keen.core.models import Client, Customer
from keen.web.views.forms import CustomerForm


logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'client/dashboard.html')


def promotions(request):
    render(request, 'client/promotions.html')


def customers(request):
    page = 1
    page_size = 37
    offset = (page - 1) * page_size

    #client = get_object_or_404(Client, slug='mdo')
    client,created = Client.objects.get_or_create(slug='mdo',name='mdo')
    q = Customer.objects.filter(client=client)

    context = {}
    context['client'] = client
    context['summary'] = {
        'total_customers': q.count(),
        'redeemers': 0,
        'new_signups': 0,
    }
    context['customers'] = q[offset:offset + page_size]

    return render(request, 'client/customers.html', context)

def profile(request, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = Customer.objects.get(id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    print customer.get_email()
    return render_to_response('client/customers/customer_profile_view.html', context, context_instance=RequestContext(request))

def business_profile(request):
    return None

def customer_form(request, customer_id=None):
    client = get_object_or_404(Client, slug='default_client')
    if customer_id:
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        form = CustomerForm(client, initial=customer.data)
    else:
        form = CustomerForm(client)
    return render(request, 'client/customer_form.html', {'form': form})
