from django.conf.urls import patterns, url, include

from .views.api.client import ClientProfile, CustomerList, CustomerProfile


api_urls = patterns(
    '',
    url(r'^client/(?P<client_slug>[\w-]+)$', ClientProfile.as_view(),
        name='client_profile'),
    url(r'^client/(?P<client_slug>[\w-]+)/(?P<part>summary)$',
        ClientProfile.as_view(), name='client_profile'),
    url(r'^client/(?P<client_slug>[\w-]+)/customers$', CustomerList.as_view(),
        name='api_customer_list'),
    url(r'^client/(?P<client_slug>[\w-]+)/customer/(?P<customer_id>\d+)$',
        CustomerProfile.as_view(), name='api_customer_profile'),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^client/$', 'client.dashboard', name='client_dashboard'),
    url(r'^client/promotions$', 'client.promotions', name='client_promotions'),
    url(r'^client/customers$', 'client.customers', name='client_customers'),
    url(r'^client/profile$', 'client.profile', name='client_profile'),
    url(r'^client/customer_form$', 'client.customer_form', name='customer_form'),
    url(r'^client/signup-form/create$', 'client.signup_form_create', name='signup_form_create'),
    url(r'^api/', include(api_urls)),
)
