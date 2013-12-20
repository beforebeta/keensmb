import logging

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response

from keen.core.models import ClientUser
from keen.web.serializers import ClientSerializer


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
            return HttpResponseRedirect(reverse('client_customers'))
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
