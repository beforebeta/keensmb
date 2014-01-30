import logging

from django.shortcuts import render, get_object_or_404
from django.template import Context, Template
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import DatabaseError

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from keen.core.models import Client, Customer
from keen.enrichment.models import EnrichmentRequest
from keen.tasks import send_email


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@api_view(['POST'])
def enrich_customers_data_view(request, client_slug):
    try:
        if client_slug != request.session['client_slug']:
            return Response(status=HTTP_404_NOT_FOUND)
        client = get_object_or_404(Client, slug=client_slug)
        customers = map(int, request.DATA['customers'])
    except (KeyError, ValueError, TypeError):
        return Response(status=HTTP_400_BAD_REQUEST)

    try:
        req = EnrichmentRequest.objects.create(client=client)
        req.customers = Customer.objects.filter(client=client, id__in=customers)
        req.save()
    except DatabaseError:
        logger.exception('Failed to save Enrichment Request')
        return Response(status=500)

    send_enrichment_request_email(req)

    return Response()


enrichment_request_template = Template('''

    Client {{ client.name }} wants to enrich data of the following customers:

    {% for customer in customers %}
    {{ customer.data.email }}, {{ customer.data.full_name }}, {{ customer.id }}
    {% endfor %}

''')


def send_enrichment_request_email(request):
    msg = enrichment_request_template.render(Context({
        'client': request.client,
        'customers': request.customers.all(),
    }))

    send_email.delay('New Enrichment Request', msg, ['workflow@keensmb.com'])
