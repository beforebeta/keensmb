import csv
from functools import wraps

from django.db import DatabaseError
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response

from keen.core.models import Client
from keen.web.models import ImportRequest
from keen.web.serializers import CustomerFieldSerializer
from keen.web.views.api.client import IsClientUser


def client_api_meth(meth):
    @wraps(meth)
    @method_decorator(ensure_csrf_cookie)
    def wrapper(self, request, client_slug, *args, **kw):
        try:
            client = Client.objects.get(slug=client_slug)
        except Client.DoesNotExist:
            del request.session['client_slug']
            raise HttpResponseNotFound()

        return meth(self, request, client, *args, **kw)

    return wrapper


class ImportAPI(APIView):

    permission_classes = (IsClientUser,)

    @client_api_meth
    def get(self, request, client, import_id):
        imp = get_object_or_404(ImportRequest, client=client, id=import_id)

        response = {
            'status': imp.status,
        }
        if imp.status == ImportRequest.STATUS.in_process:
            # TODO: add progress status here
            pass
        elif imp.status == ImportRequest.STATUS.complete:
            # TODO: provide detailed result of import here
            pass

        return Response(response)


    @client_api_meth
    def post(self, request, client):
        try:
            imp = ImportRequest.create(client=client, file=request.FILES['file'])
        except DatabaseError:
            logger.exception('Failed to create ImportRequest')
            raise

        all_fields = list(client.customer_fields.select_related('group'))
        imp.params['available_fields'] = CustomerFieldSerializer(all_fields, many=True).data
        with imp.file.open() as f:
            imp.params['import_fields'] = guess_field_map(f, all_fields)

        return Response({
            'import_requiest_id': imp.id,
            'available_fields': imp.params['available_fields'],
            'import_fields': imp.params['import_fields'],
        })


def guess_field_map(import_file, available_fields):
    reader = csv.reader(import_file)
    return [(name.strip(), '') for name in reader.next()]
