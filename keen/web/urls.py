from django.conf.urls import patterns, url

from .views import client
from .views.api.client import CustomerList, CustomerProfile


api_urls = patterns(
    'keen.web.views.api',
    url(r'^customers/', CustomerList.as_view()),
    url(r'^customers/{?P<customer_id>\d+)$', CustomerProfile.as_view()),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^client/$', 'client.dashboard', name='client_dashboard'),
    url(r'^client/promotions$', 'client.promotions', name='client_promotions'),
    url(r'^client/customers$', 'client.customers', name='client_customers'),
    url(r'^client/profile$', 'client.profile', name='client_profile'),
    url(r'^client/customer_form$', 'client.customer_form', name='customer_form'),
    url(r'^client/api/', include(api_urls)),
)
