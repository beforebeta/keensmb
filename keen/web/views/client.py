import logging

from django.shortcuts import render, get_object_or_404

from keen.core.models import Client, Customer, Location
from keen.web.views.forms import CustomerForm


logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'client/dashboard.html')


def promotions(request):
    render(request, 'client/promotions.html')


def customers(request):
    client = get_object_or_404(Client.objects.prefetch_related('customer_fields'), slug='default_client')
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


def profile(request):
    return render(request, 'client/profile.html')

def signup_form_create(request):
    return render(request, 'client/signup-form-create.html')


def customer_form(request, customer_id=None):
    client = get_object_or_404(Client, slug='mdo')
    if customer_id:
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        form = CustomerForm(client, initial=customer.data)
    else:
        form = CustomerForm(client)
    return render(request, 'client/customer_form.html', {'form': form})
