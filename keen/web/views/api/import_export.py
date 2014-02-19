import logging
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


logger = logging.getLogger(__name__)


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

        imp.file.open()
        reader = csv_reader(imp.file.file)
        columns = reader.next()
        while not all(columns):
            row = reader.next()
            for i, value in enumerate(columns):
                if not value and row[i]:
                    columns[i] = row[i]

        return Response({
            'import_requiest_id': imp.id,
            'columns': columns,
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

        logger.debug('Received import request: {0!r}'.format(request.DATA))

        try:
            import_fields = request.DATA['import_fields']
            skip_first_row = request.DATA['skip_first_row']
        except KeyError, exc:
            return Response({
                'error': 'Missing {0} parameter'.format(exc.args[0]),
            })

        imp.data['import_fields'] = import_fields
        imp.data['skip_first_row'] = skip_first_row == 'yes'
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


def csv_reader(f):
    """Generate sequence of rows from CSV file striping whitespace from each value
    """
    reader = csv.reader(f)
    for row in reader:
        yield map(str.strip, row)
