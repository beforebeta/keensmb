import logging
import hmac
import hashlib
import base64

from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from keen.core.models import Client, Promotion


logger = logging.getLogger(__name__)


class SignatureError(Exception):
    pass


@csrf_exempt
def unsubscribe_view(request):
    try:
        md_id = request.GET['md_id']
        md_email = request.GET['md_email']
    except KeyError:
        logger.exception('Unsubscribe request is missing required parameter in query string')
        return redirect('/')

    return HttpResponse('{0} has been unsubscribed'.format(md_email))


@csrf_exempt
def webhook_view(request):
    try:
        verify_signature(request, settings.MANDRILL_WEBHOOK_KEY,
                         settings.MANDRILL_WEBHOOK_URL)
    except SignatureError as e:
        logger.error('Signature verification failed: %s', e)
        return HttpResponse('Signature verification error', status=409)

    process_events(request.POST.get('mandrill_events', []))

    return HttpResponse()


def verify_signature(request, key, url):
    sig = request.META.get('HTTP_X_MANDRILL_SIGNATURE')
    if not sig:
        raise SignatureError('No signature found')

    h = hmac.new(key, url, hashlib.sha1)
    for key in sorted(request.POST.keys()):
        h.update(key)
        h.update(request.POST[key])

    expected_sig = base64.b64encode(h.digest())
    if sig != expected_sig:
        raise SignatureError('Expected %r signature but found %r',
                             expected_sig, sig)


def process_events(events):
    for event in events:
        try:
            meta = event['msg']['metadata']
            client_slug = meta['client']
            promotion_id = meta['promotion']
        except KeyError as e:
            logger.error('Required part of event is missing: %r in %r',
                         e.args[0], event)
            continue

        try:
            promotion = Promotion.objects.get(client__slug=client_slug,
                                              id=promotion_id)
        except Promotion.DoesNotExist:
            logger.error('Received event for non-existent promotion %r/%r',
                         client_slug, promotion_id)
            continue

        event_type = event['event']
        if event_type not in promotion.analytics:
            promotion.analytics[event_type] = 1
        else:
            promotion.analytics[event_type] += 1
        promotion.save()
