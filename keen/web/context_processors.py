def add_client(request):
    context = {}
    try:
        # `keen.core.models.Client` instance is injected by
        # `keen.web.views.client.client_view` decorator
        context["client"] = request.client
    except AttributeError:
        pass
    return context
