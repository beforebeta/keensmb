import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie

from keen.core.models import Client, Customer, Location, Promotion
from keen.core.models import Client, Customer, Location
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm, PromotionForm
from keen.web.serializers import SignupFormSerializer
from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


####################################################################################################################
# Dashboard
####################################################################################################################

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def dashboard(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    context = {
        'client': client,
        'dashboard': client.get_dashboard()
    }
    return render(request, 'client/dashboard.html', context)

####################################################################################################################
# Promotions
####################################################################################################################

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def promotions(request, tab='active'):
    context = {'breadcrumbs': [{"link": "/promotions", "text": 'Promotions'},
                               {"link": "/promotions/%s" % tab, "text": '%s Promotions' % tab.title()}],
               'tab': tab}
    promotions = list(Promotion.objects.get_promotions_for_status(tab))
    if tab.lower() == 'awaiting':
        #include promotions in draft status along with promotions awaiting approval
        promotions.extend(list(Promotion.objects.get_promotions_for_status(Promotion.PROMOTION_STATUS.draft)))
    context["promotions"] = promotions
    return render_to_response('client/promotions.html', context, context_instance=RequestContext(request))
    #return render(request, 'client/promotions.html')

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def create_edit_promotion(request, promotion_id=None):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    context = {'breadcrumbs': [{"link": "/promotions", "text": 'Promotions'}]}
    promotion_instance = None
    if promotion_id:
        promotion_instance = get_object_or_404(Promotion, id=promotion_id)
        context['breadcrumbs'].append({"link": "/promotions/%s/edit" % promotion_id, "text": 'Edit Promotion: %s' % promotion_instance.name})
        context["mode"] = "edit"
    else:
        context['breadcrumbs'].append({"link": "/promotions/create", "text": 'Create New Promotion'})
        context["mode"] = "create"
    form = None
    if request.method == 'POST': # If the form has been submitted...
        if promotion_id:
            form = PromotionForm(request.POST, request.FILES, instance=promotion_instance)
        else:
            form = PromotionForm(request.POST, request.FILES)
        if form.is_valid():
            if "save_draft" in request.POST:
                promotion_instance = form.save(commit=False)
                promotion_instance.client = client
                promotion_instance.save()
                return HttpResponseRedirect(reverse('client_edit_promotion', args=[promotion_instance.id]))
    else:
        if promotion_id:
            form = PromotionForm(instance=promotion_instance)
        else:
            form = PromotionForm()
    context['form'] = form
    return render_to_response('client/promotions-create-edit.html', context, context_instance=RequestContext(request))

def email_template(request):
    context={}
    return render_to_response('email-template/index.html', context, context_instance=RequestContext(request))

####################################################################################################################
# Customers
####################################################################################################################

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

    return render(request, 'client/customers/customer_profile_list.html', context)

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def profile(request, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = Customer.objects.get(id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    return render_to_response('client/customers/customer_profile_view.html', context, context_instance=RequestContext(request))

####################################################################################################################
# Signup Forms
####################################################################################################################

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_list(request):
    client = get_object_or_404(Client, slug=request.session['client_slug'])
    forms = SignupForm.objects.filter(client=client)\
            .exclude(slug__startswith='preview-')\
            .order_by('-status', 'slug')
    context = {
        'client': client,
        'forms': SignupFormSerializer(forms, many=True).data,
    }

    return render(request, 'client/signup_form/signup_form_list.html', context)

@ensure_csrf_cookie
@login_required(login_url='/#signin')
def signup_form_create(request):
    client = get_object_or_404(
        Client.objects.prefetch_related('customer_fields'),
        slug=request.session['client_slug'])
    context = {
        'client': client,
    }
    return render(request, 'client/signup_form/signup_form_create.html', context)


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
    return render(request, 'client/signup_form/signup_form_create.html', context)


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
