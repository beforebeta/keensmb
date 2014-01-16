from keen.core.models import Client

def add_client(request):
    try:
        return {"client":Client.objects.get(slug=request.session['client_slug'])}
    except:
        return {}