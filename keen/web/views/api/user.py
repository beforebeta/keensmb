import logging

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response

from keen.core.models import ClientUser
from keen.web.models import TrialRequest
from keen.web.forms import TrialRequestForm
from keen.web.serializers import ClientSerializer

from tracking.models import Visitor

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@api_view(['POST'])
def login_view(request):
    try:
        email = request.DATA['email']
        password = request.DATA['password']
    except KeyError:
        logger.warn('Request is missing email and/or password parameters: %r' % request.DATA)
        return HttpResponseBadRequest('Missing authentication information')

    user = authenticate(username=email, password=password)
    logger.debug('Authenticate %r' % locals())

    if user:
        login(request, user)
        try:
            request.session['client_slug'] = ClientUser.objects.get(
                user=user).client.slug
        except ClientUser.DoesNotExist:
            request.session['client_slug'] = None
            request.session.save()
        else:
            request.session.save()
            return Response({'success': 'Thank you for signing-in!'})

    return Response({'error': 'Invalid e-mail/pasword combination'})


@ensure_csrf_cookie
@api_view(['GET'])
def logout_view(request):
    request.session.pop('client_slug', None)
    logout(request)

    return HttpResponseRedirect(reverse('home'))


@ensure_csrf_cookie
@api_view(['POST'])
def request_free_trial(request):
    form = TrialRequestForm(request.DATA)
    if form.is_valid():
        trial_request = TrialRequest(**form.cleaned_data)
        trial_request.source = request.session.get('landing_page')
        if 'visitor' in request.session:
            try:
                trial_request.visitor = Visitor.objects.get(
                    pk=request.session['visitor'])
            except Visitor.DoesNotExist:
                logger.error('Visitor does not exist')

        try:
            trial_request.save()
        except DatabaseError:
            logger.exception('Failed to save free trial request')
            # FIXME: should we return an error?
            # for now lets pretend all went well

        result = {
            'success': 'We will be in touch shortly',
        }
    else:
        result = {
            'errors': form.errors,
        }

    return Response(result)
