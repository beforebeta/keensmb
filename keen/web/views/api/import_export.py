import logging
import re

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
from keen.web.utils import csv_reader
from keen.tasks import import_customers


logger = logging.getLogger(__name__)

header_re = re.compile(r'\b(e-?mail|google|twitter|facebook|(first|last|full)\s+name)\b', re.I)


class ImportAPI(ClientAPI):

    def get(self, request, client, import_id):
        """Retrieve information about import request
        """
        imp = get_object_or_404(ImportRequest, client=client, id=import_id)
        response = {
            'status': imp.status,
            'imported': imp.data.get('imported', 0),
            'updated': imp.data.get('imported', 0),
            'failed': imp.data.get('failed', 0),
            'duplicates': imp.data.get('duplicates', 0),
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

        f = open(imp.file.path, 'rU')
        reader = csv_reader(f)

        # first row might be a list of column names instead of data
        columns = reader.next()
        # header with empty column names is acceptible
        skip_first_row = any(map(header_re.search, columns))

        # collect some non-empty data for each column starting from second row
        sample_data = reader.next()
        while not all(sample_data):
            row = reader.next()
            for i, value in enumerate(sample_data):
                if not value and row[i]:
                    sample_data[i] = row[i]

        return Response({
            'import_requiest_id': imp.id,
            'columns': columns,
            'skip_first_row': skip_first_row,
            'sample_data': sample_data,
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
        imp.data['skip_first_row'] = skip_first_row in ('true', 'yes')
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
