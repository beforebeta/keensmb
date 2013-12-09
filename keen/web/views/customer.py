from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def signup_view(request, client_slug):
    client = get_object_or_404(Client, slug=client_slug)
    context = {
        'client': client,
    }

    if request.method == 'POST':
        form = SignupForm(request.POST)
    else:
        form = SignupForm()

    context['form'] = form

    return render(request, client.signup_form_template, context)
