import logging
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie

from keen.util import get_first_day_of_month_as_dt
from keen.core.models import Client, Customer, Location, Promotion
from keen.core.models import Client, Customer, Location
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm
from keen.web.serializers import SignupFormSerializer


logger = logging.getLogger(__name__)


def client_view(func):
    """Prevent unauthorized access to and provide client argument to a view
    """
    @wraps(func)
    @ensure_csrf_cookie
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated() and 'client_slug' in request.session:
            client = get_object_or_404(
                Client, slug=request.session['client_slug'])
            return func(request, client, *args, **kw)
        return render(request, 'login.html')
    return wrapper


@client_view
def dashboard(request, client):
    context = {
        'client': client,
        'dashboard': client.get_dashboard()
    }
    return render(request, 'client/dashboard.html', context)


@client_view
def promotions(request, client, tab='active'):
    context = {'breadcrumbs': [{"link": "/promotions", "text": 'Promotions'},
                               {"link": "/promotions/%s" % tab, "text": '%s Promotions' % tab.title()}],
               'tab': tab}
    promotions = Promotion.objects.get_promotions_for_status(tab)
    context["promotions"] = promotions
    return render_to_response('client/promotions.html', context, context_instance=RequestContext(request))
    #return render(request, 'client/promotions.html')


@client_view
def create_promotion(request, client):
    context={}
    return render_to_response('client/promotions-create.html', context, context_instance=RequestContext(request))


@client_view
def customers(request, client):
    q = Customer.objects.filter(client=client)

    context = {}
    context['client'] = client
    context['locations'] = list(client.locations.all())
    context['customer_fields'] = list(client.customer_fields.all())
    context['summary'] = {
        'total_customers': q.count(),
        'redeemers': 0,
        'new_signups': q.filter(created__gte=get_first_day_of_month_as_dt()).count(),
    }

    return render(request, 'client/customers/customer_profile_list.html', context)


@client_view
def email_template(request, client):
    context={}
    return render_to_response('email-template/index.html', context, context_instance=RequestContext(request))


@client_view
def profile(request, client, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = get_object_or_404(Customer, client=client, id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    return render_to_response('client/customers/customer_profile_view.html', context, context_instance=RequestContext(request))


@client_view
def signup_form_list(request, client):
    forms = SignupForm.objects.filter(client=client)\
            .exclude(slug__startswith='preview-')\
            .order_by('-status', 'slug')
    context = {
        'client': client,
        'forms': SignupFormSerializer(forms, many=True).data,
    }

    return render(request, 'client/signup_form/signup_form_list.html', context)


@client_view
def signup_form_create(request, client):
    context = {
        'client': client,
    }
    return render(request, 'client/signup_form/signup_form_create.html', context)


@client_view
def signup_form_edit(request, client, slug):
    form = get_object_or_404(SignupForm, client=client, slug=slug)
    context = {
        'client': client,
        'form': form,
    }
    return render(request, 'client/signup_form/signup_form_create.html', context)


@client_view
def signup_form_preview(request, client, slug):
    signup_form = get_object_or_404(SignupForm, client=client, slug=slug)
    form = CustomerForm(client)
    context = {
        'client': client,
        'form_data': signup_form.data,
        'form': form,
    }
    return render(request, 'customer/signup.html', context)


@client_view
def business_profile(request, client):
    return None
