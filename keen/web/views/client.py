import logging

from django.http import Http404
from django.shortcuts import render

from keen.core.models import Client, Customer


logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'client/dashboard.html')


def promotions(request):
    render(request, 'client/promotions.html')


def customers(request):
    page = 1
    page_size = 37
    offset = (page - 1) * page_size

    try:
        client = Client.objects.get(slug='mdo')
    except Client.DoesNotExist:
        logger.error('Client not found')
        raise Http404

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
