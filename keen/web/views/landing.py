from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def landing_view(request):
    user = request.user
    if user and user.is_authenticated() and not user.is_superuser:
        return redirect(reverse('client_dashboard'))
    return render(request, 'front-page/index.html')
