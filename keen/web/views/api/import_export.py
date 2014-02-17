import csv

from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from fuzzywuzzy import process

from keen.core.models import Client
from keen.web.models import ImportRequest
from keen.web.serializers import CustomerFieldSerializer
from keen.web.views.api.client import ClientAPI
from keen.tasks import import_customers


class ImportAPI(ClientAPI):

    def get(self, request, client, import_id):
        """Retrieve information about import request
        """
        imp = get_object_or_404(ImportRequest, client=client, id=import_id)
        response = {
            'status': imp.status,
            'imported': imp.data.get('imported', 0),
            'failed': imp.data.get('failed', 0),
            'errors': imp.data.get('errors', []),
        }
        return Response(response)


    def post(self, request, client):
        """Create new import request
        """
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

    @transaction.atomic()
    def put(self, request, client, import_id):
        """Set import request parameters and start import process
        """
        imp = get_object_or_404(ImportRequest.objects.select_for_update(),
                                client=client, id=import_id)

        if imp.status != ImportRequest.STATUS.new:
            return Response({
                'error': 'Cannot process import request in {0} state'.format(imp.state),
            })

        try:
            import_fields = request.DATA['import_fields']
        except KeyError:
            return Response({
            })

        imp.data['import_fields'] = import_fields
        imp.save()

        import_customers.delay(imp.id)

        return Response(status=HTTP_204_NO_CONTENT)

    def delete(self, request, client, import_id):
        """Abort import request
        """
        try:
            ImportRequest.get(client=client, id=import_id).delete()
        except ImportRequest.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        except DatabaseError:
            logger.exception('Failed to delete import request')
            raise
        return Response(status=HTTP_204_NO_CONTENT)


def map_field(name, fields):
    field, score = process.extractOne(name, fields, processor=lambda field: field.title)
    field2, score2 = process.extractOne(name, fields, processor=lambda field: field.title)
    if score2 > score:
        score = score2
        field = field2
    if score < 80:
        return (name, '')
    return (name, field.name)
