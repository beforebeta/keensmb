from django.conf.urls import patterns, url, include

from .views import client
from .views.api.client import CustomerList, CustomerProfile


api_urls = patterns(
    'keen.web.views.api',
    url(r'^customers/(?P<offset>\d+)$', CustomerList.as_view(), name='api_customer_list'),
    url(r'^customers/(?P<customer_id>\d+)$', CustomerProfile.as_view()),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^client/$', 'client.dashboard', name='client_dashboard'),
    url(r'^client/promotions$', 'client.promotions', name='client_promotions'),
    url(r'^client/customers$', 'client.customers', name='client_customers'),
    url(r'^client/profile$', 'client.profile', name='client_profile'),
    url(r'^client/customer_form$', 'client.customer_form', name='customer_form'),
    url(r'^client/signup-form/create$', 'client.signup_form_create', name='signup_form_create'),
    url(r'^client/api/', include(api_urls)),
)
