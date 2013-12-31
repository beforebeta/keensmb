from itertools import cycle

from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie


rotate_templates = cycle((
    'front-page/index.html',
    'front-page/landing2.html',
    'front-page/landing3.html',
))


@ensure_csrf_cookie
def landing_view(request):
    user = request.user
    if user and user.is_authenticated() and not user.is_superuser:
        return redirect(reverse('client_dashboard'))

    template = request.session.get('landing_page')
    if template is None:
        template = rotate_templates.next()
        request.session['landing_page'] = template

    return render(request, template)
