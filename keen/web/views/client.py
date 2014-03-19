import json
import logging
from functools import wraps
from operator import itemgetter
from dateutil.relativedelta import relativedelta

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse

from keen.util import get_first_day_of_month_as_dt, get_last_day_of_month_as_dt
from keen.core.models import (
    Client,
    Customer,
    Location,
    Promotion,
    CUSTOMER_FIELD_NAMES,
    CUSTOMER_FIELD_NAMES_DICT,
)
from keen.web.models import SignupForm
from keen.web.forms import CustomerForm, PromotionForm
from keen.web.serializers import SignupFormSerializer
from keen.events.models import Event
from keen import InvalidOperationException


logger = logging.getLogger(__name__)


def client_view(func):
    """Prevent unauthorized access to and provide client argument to a view
    """
    @wraps(func)
    @ensure_csrf_cookie
    def wrapper(request, *args, **kw):
        if not request.is_secure():
            url = request.build_absolute_uri()
            url = 'https' + url[4:]
            return redirect(url)

        if request.user.is_authenticated() and 'client_slug' in request.session:
            try:
                client = Client.objects.get(slug=request.session['client_slug'])
            except Client.DoesNotExist:
                logger.error('Failed to locate client with slug %s' %
                             request.session['client_slug'])
                del request.session['client_slug']
            else:
                request.client = client
                return func(request, client, *args, **kw)
        return redirect('/#' + request.path)
    return wrapper


####################################################################################################################
# Dashboard
####################################################################################################################

@client_view
def dashboard(request, client):
    context = {
        'client': client,
        'updates': Event.objects.filter(client=client).order_by('-occurrence_datetime')[:14],
    }
    return render(request, 'client/dashboard.html', context)

####################################################################################################################
# Promotions
####################################################################################################################

@client_view
def promotions(request, client, tab='active'):
    context = {'breadcrumbs': [{"link": "/promotions", "text": 'Promotions'},
                               {"link": "/promotions/%s" % tab, "text": '%s Promotions' % tab.title()}],
               'tab': tab}
    promotions = list(Promotion.objects.get_promotions_for_status(tab, client))
    if tab.lower() == 'awaiting':
        #include promotions in draft status along with promotions awaiting approval
        promotions.extend(list(Promotion.objects.get_promotions_for_status(Promotion.PROMOTION_STATUS.draft, client)))
    context["promotions"] = promotions
    return render(request, 'client/promotions.html', context)

@client_view
def create_edit_promotion(request, client, promotion_id=None):
    context = {'breadcrumbs': [
        {"link": "/promotions", "text": 'Promotions'},
    ]}

    if promotion_id:
        promotion_instance = get_object_or_404(Promotion, id=promotion_id, client=client)
        context['breadcrumbs'].append(
            {"link": "/promotions/%s/edit" % promotion_id,
             "text": 'Edit Promotion: %s' % promotion_instance.name})
        context["mode"] = "edit"
        assert promotion_instance.status != Promotion.PROMOTION_STATUS.active and promotion_instance.status != Promotion.PROMOTION_STATUS.expired, "cannot edit Active or Expired promotions"
    else:
        promotion_instance = None
        context['breadcrumbs'].append(
            {"link": "/promotions/create",
             "text": 'Create New Promotion'})
        context["mode"] = "create"

    if request.method == 'POST': # If the form has been submitted...
        if promotion_id:
            form = PromotionForm(request.POST, request.FILES, instance=promotion_instance)
        else:
            form = PromotionForm(request.POST, request.FILES)

        if form.is_valid():
            logger.debug('Promotion form data: {0!r}\n\n{1!r}'.format(form.data, form.cleaned_data))
            promotion_instance = form.save(commit=False)
            promotion_instance.target_audience = form.cleaned_data.get('target_audience')
            promotion_instance.client = client
            preview_promotion = False
            if "save_draft" in request.POST or 'send' in request.POST:
                promotion_instance.status = Promotion.PROMOTION_STATUS.draft
            elif "preview_promotion" in request.POST:
                preview_promotion = True

            promotion_instance.save()
            url = reverse('client_edit_promotion', args=[promotion_instance.id])
            if preview_promotion:
                url += '#preview'

            return redirect(url)
    else:
        if promotion_id:
            form = PromotionForm(instance=promotion_instance)
        else:
            form = PromotionForm()

    context['form'] = form
    context['target_audience_filters'] = [
            {
                'name': field.name,
                'title': field.title,
                'choices': field.choices,
                'values': get_field_value(field.name, form),
            }
            for field in client.customer_fields.order_by('title')
        ]
    return render(request, 'client/promotions-create-edit.html', context)


def get_field_value(name, form):
    if 'target_audience' in form.cleaned_data:
        target_audience = form.cleaned_data.get('target_audience')
    elif form.instance:
        target_audience = form.instance.target_audience
    else:
        target_audience = None

    if not target_audience:
        return []

    return target_audience.get(name, [])


@client_view
def preview_promotion(request, client, promotion_id):
    context = {}
    context["promotion"] = get_object_or_404(Promotion, id=promotion_id, client=client)
    return render('client/promotions/preview_promotion.html', context)

@client_view
def delete_promotion(request, client):
    promotion_id = int(request.POST.get("obj_id"))
    promotion = get_object_or_404(Promotion, id=promotion_id, client=client)
    try:
        if promotion.status in [Promotion.PROMOTION_STATUS.active, Promotion.PROMOTION_STATUS.expired]:
            return HttpResponse(json.dumps({"success" : "0", "msg" : "Cannot delete an active or expired promotion"}), content_type="application/json")
        else:
            promotion.delete()
        return HttpResponse(json.dumps({"success" : "1", "msg" : "Success"}), content_type="application/json")
    except:
        logger.exception('Failed to delete promotion')
        return HttpResponse(json.dumps({"success" : "0", "msg" : "An error occurred while deleting the object."}),
                                                                    content_type="application/json")

@client_view
def approve_promotion(request, client):
    promotion_id = int(request.POST.get("obj_id"))
    promotion = get_object_or_404(Promotion, id=promotion_id, client=client)
    try:
        if promotion.status not in [Promotion.PROMOTION_STATUS.draft, Promotion.PROMOTION_STATUS.inapproval]:
            return HttpResponse(json.dumps({"success" : "0", "msg" : "You can only approve promotions that haven't been scheduled or activated yet."}), content_type="application/json")
        else:
            try:
                promotion.approve()
                return HttpResponse(json.dumps({"success" : "1", "msg" : "Success"}), content_type="application/json")
            except InvalidOperationException, e:
                return HttpResponse(json.dumps({"success" : "0", "msg" : str(e)}), content_type="application/json")
    except:
        logger.exception('Failed to approve promotion')
        return HttpResponse(json.dumps({"success" : "0", "msg" : "An error occurred while deleting the object."}),
                                                                    content_type="application/json")

@client_view
def email_template(request, client):
    return render('email-template/index.html')

####################################################################################################################
# Customers
####################################################################################################################

def _get_formatted_name(dt):
    return "%s %s" % (dt.strftime("%B"), dt.year)

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

    first_day_of_month = get_first_day_of_month_as_dt()
    last_day_of_month = get_last_day_of_month_as_dt()
    first_days = [first_day_of_month+relativedelta(months=i) for i in [-4,-3,-2,-1,0]]
    last_days = [last_day_of_month+relativedelta(months=i) for i in [-4,-3,-2,-1,0]]
    context["chartData"] = json.dumps([{
            "month": _get_formatted_name(first_days[i]),
            "visits": client.customers.filter(created__gte=first_days[i], created__lte=last_days[i]).count()} for i in range(5)]);
    return render(request, 'client/customers/customer_profile_list.html', context)

@client_view
def profile(request, client, customer_id=None):
    context = {'breadcrumbs': [{"link": "/customers","text": 'Customers'}, {"link": "/customer","text": 'Customer'}]}
    customer = get_object_or_404(Customer, client=client, id=customer_id)
    context["customer"] = customer
    context["client"] = customer.client
    return render('client/customers/customer_profile_view.html', context)

####################################################################################################################
# Signup Forms
####################################################################################################################

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
