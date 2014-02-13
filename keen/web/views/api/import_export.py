import csv
from functools import wraps

from django.db import DatabaseError
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from fuzzywuzzy import process

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
            'imported': imp.data.get('imported', 0),
            'failed': imp.data.get('failed', 0),
            'errors': imp.data.get('errors', []),
        }
        return Response(response)


    @client_api_meth
    def post(self, request, client):

        try:
            imp = ImportRequest.objects.create(client=client, file=request.FILES['file'])
        except DatabaseError:
            logger.exception('Failed to create import request')
            raise

        all_fields = list(client.customer_fields.select_related('group'))
        import_field_names = csv.reader(imp.file.file).next()

        return Response({
            'import_requiest_id': imp.id,
            'available_fields': CustomerFieldSerializer(all_fields, many=True).data,
            'import_fields': [
                map_field(name, all_fields) for name in import_field_names],
        })


def map_field(name, fields):
    field, score = process.extractOne(name, fields, processor=lambda field: field.title)
    field2, score2 = process.extractOne(name, fields, processor=lambda field: field.title)
    if score2 > score:
        score = score2
        field = field2
    if score < 80:
        return (name, '')
    return (name, field.name)
