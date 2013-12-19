import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie

from keen.core.models import Client, Customer, Location, Promotion
from keen.core.models import Client, Customer, Location
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm
from keen.web.serializers import SignupFormSerializer


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def dashboard(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    context = {
        'client': client,
        'dashboard': client.get_dashboard()
    }
    return render(request, 'client/dashboard.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def promotions(request, tab='active'):
    context = {'breadcrumbs': [{"link": "/promotions", "text": 'Promotions'},
                               {"link": "/promotions/%s" % tab, "text": '%s Promotions' % tab.title()}],
               'tab': tab}
    promotions = Promotion.objects.get_promotions_for_status(tab)
    context["promotions"] = promotions
    return render_to_response('client/promotions.html', context, context_instance=RequestContext(request))
    #return render(request, 'client/promotions.html')

def create_promotion(request):
    context={}
    return render_to_response('client/promotions-create.html', context, context_instance=RequestContext(request))

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def customers(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    q = Customer.objects.filter(client=client)

    context = {}
    context['client'] = client
    context['locations'] = list(client.locations.all())
    context['customer_fields'] = list(client.customer_fields.all())
    context['summary'] = {
        'total_customers': q.count(),
        'redeemers': 0,
        'new_signups': 0,
    }

    return render(request, 'client/customers.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def profile(request, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = Customer.objects.get(id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    return render_to_response('client/customers/customer_profile_view.html', context, context_instance=RequestContext(request))


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_list(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    forms = SignupForm.objects.filter(client=client).order_by('-status', 'slug')
    context = {
        'client': client,
        'forms': SignupFormSerializer(forms, many=True).data,
    }

    return render(request, 'client/signup-form-list.html', context)

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_create(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    context = {
        'client': client,
    }
    return render(request, 'client/signup-form-create.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_edit(request, slug):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    form = get_object_or_404(SignupForm, client=client, slug=slug)
    context = {
        'client': client,
        'form': form,
    }
    return render(request, 'client/signup-form-edit.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_preview(request, slug):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    signup_form = get_object_or_404(SignupForm, client=client, slug=slug)
    form = CustomerForm(client)
    context = {
        'client': client,
        'form_data': signup_form.data,
        'form': form,
    }
    return render(request, 'customer/signup.html', context)


@ensure_csrf_cookie
@login_required(login_url='/#signin')
def business_profile(request):
    return None
