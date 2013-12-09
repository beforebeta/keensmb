from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

from .views.api.client import ClientProfile, CustomerList, CustomerProfile


api_urls = patterns(
    'keen.web.views.api',
    url(r'^client/current$', 'client.current_client_view',
        name='current_client'),
    url(r'^client/(?P<client_slug>[\w-]+)$', ClientProfile.as_view(),
        name='client_profile'),
    url(r'^client/(?P<client_slug>[\w-]+)/(?P<part>summary|customer_fields)$',
        ClientProfile.as_view(), name='client_profile'),
    url(r'^client/(?P<client_slug>[\w-]+)/customers$', CustomerList.as_view(),
        name='api_customer_list'),
    url(r'^client/(?P<client_slug>[\w-]+)/customer/(?P<customer_id>\d+)$',
        CustomerProfile.as_view(), name='api_customer_profile'),
    url(r'^login$', 'user.login_view', name='login'),
    url(r'^logout$', 'user.logout_view', name='logout'),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^$', TemplateView.as_view(template_name='front-page/index.html'), name='home'),
    url(r'^legal$', TemplateView.as_view(template_name='front-page/legal.html'), name='legal'),
    url(r'^dashboard$', 'client.dashboard', name='client_dashboard'),
    url(r'^promotions$', 'client.promotions', name='client_promotions'),
    url(r'^customers$', 'client.customers', name='client_customers'),
    url(r'^customer_profile/(?P<customer_id>[\d]+)', 'client.profile', name='client_profile'),
    url(r'^business_profile', 'client.business_profile', name='business_profile'),
    url(r'^signup-form/create$', 'client.signup_form_create', name='signup_form_create'),
    url(r'^api/', include(api_urls)),
    url(r'^(?P<client_slug>[\w-]+)/signup$', 'customer.signup_view', name='customer_signup'),
)
