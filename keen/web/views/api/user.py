import logging

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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
        email = request.POST['email']
        password = request.POST['password']
    except KeyError:
        messages.error(request, 'Please provide e-mail and password')
        logger.warn('Request is missing email and/or password parameters: %r' % request.POST.copy())
        return HttpResponseBadRequest('Missing authentication information')

    user = authenticate(username=email, password=password)
    logger.debug('Authenticate %r' % locals())

    if user and user.is_active:
        login(request, user)
        try:
            request.session['client_slug'] = ClientUser.objects.get(
                user=user).client.slug
        except ClientUser.DoesNotExist:
            messages.error(request, 'Failed to associate your account with any client')
            request.session['client_slug'] = None
            request.session.save()
        else:
            request.session.save()
            redirect_url = request.GET.get('next', reverse('client_dashboard'))
            return HttpResponseRedirect(redirect_url)
    else:
        messages.error(request, 'Authentication failed')
        response = Response({'error': 'Authentication failed'})

    return HttpResponseRedirect('/#signin')


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
        if 'visitor' in request.session:
            try:
                trial_request.visitor = Visitor.objects.get(
                    request.session['visitor'])
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
