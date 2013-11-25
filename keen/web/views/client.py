import logging

from django.shortcuts import render, get_object_or_404

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

    client = get_object_or_404(Client, slug='mdo')

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


def profile(request):
    return render(request, 'client/profile.html')


def customer_form(request, customer_id=None):
    client = get_object_or_404(Client, slug='mdo')
    if customer_id:
        customer = get_object_or_404(Customer, client=client, id=customer_id)
        form = CustomerForm(client, initial=customer.data)
    else:
        form = CustomerForm(client)
    return render(request, 'client/customer_form.html', {'form': form})
