import logging

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from keen.core.models import ClientUser
from keen.core.serializers import ClientSerializer


logger = logging.getLogger(__name__)


@api_view(['POST'])
def login_view(request):
    try:
        email = request.POST['email']
        password = request.POST['password']
    except KeyError:
        logger.warn('Request is missing email and/or password parameters: %r' % request.POST.copy())
        return HttpResponseBadRequest('Missing authentication information')

    user = authenticate(username=email, password=password)

    if user and user.is_active:
        login(request, user)
        try:
            request.session['client'] = ClientSerializer(
                ClientUser.objects.get(user=user).client).data
        except ClientUser.DoesNotExist:
            request.session['client'] = None
            request.session.save()
        else:
            request.session.save()
            return HttpResponseRedirect(reverse('client_customers'))
    else:
        response = Response({'error': 'Authentication failed'})

    return HttpResponseRedirect('/#signin')


@api_view(['GET'])
def logout_view(request):
    del request.session['client']
    logout(request)

    return HttpResponseRedirect(reverse('home'))
