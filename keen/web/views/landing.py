import logging
from itertools import cycle
import random

from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie


logger = logging.getLogger(__name__)


rotate_templates = cycle((
    'front-page/index.html',
    'front-page/landing2.html',
    'front-page/landing3.html',
))


@ensure_csrf_cookie
def landing_view(request):
    images = range(4)
    random.shuffle(images)
    user = request.user
    if user and user.is_authenticated() and 'client_slug' in request.session:
        return redirect(reverse('client_dashboard'))

    template = request.session.get('landing_page')
    if template is None:
        template = rotate_templates.next()
        logger.debug('New landing page selected {0}'.format(template))
        request.session['landing_page'] = template

    context = dict(images=images)
    return render(request, template, context)
