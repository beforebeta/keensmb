from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

from .views.api.client import (ClientProfile, CustomerList, CustomerProfile,
                               SignupFormList, SignupFormView, ImageList)


client_api_urls = patterns(
    'keen.web.views.api.client',
    url(r'^current$', 'current_client_view',
        name='current_client'),
    url(r'^(?P<client_slug>[\w-]+)(?:/|$)', include(patterns(
        '',
        url(r'^$', ClientProfile.as_view(),
        name='client_profile'),
        url(r'^(?P<part>summary|customer_fields)$',
            ClientProfile.as_view(), name='client_profile'),
        url(r'^customers$', CustomerList.as_view(),
            name='api_customer_list'),
        url(r'^customer/(?P<customer_id>\d+)$', CustomerProfile.as_view(),
            name='api_customer_profile'),
        url(r'^signup_forms$', SignupFormList.as_view(),
            name='api_signup_forms'),
        url(r'^signup_forms/(?P<form_slug>[\w-]+)$', SignupFormView.as_view(),
            name='api_signup_form'),
        url(r'^images$', ImageList.as_view(), name='api_images'),
    ))),
)

api_urls = patterns(
    'keen.web.views.api',
    url(r'^login$', 'user.login_view', name='login'),
    url(r'^logout$', 'user.logout_view', name='logout'),
    url(r'^client/', include(client_api_urls)),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^$', TemplateView.as_view(template_name='front-page/index.html'), name='home'),
    url(r'^legal$', TemplateView.as_view(template_name='front-page/legal.html'), name='legal'),
    url(r'^landing$', TemplateView.as_view(template_name='front-page/landing2.html'), name='home'),
    url(r'^dashboard$', 'client.dashboard', name='client_dashboard'),
    url(r'^promotions$', 'client.promotions', name='client_promotions'),
    url(r'^promotions/create$', 'client.create_promotion', name='client_create_promotion'),
    url(r'^promotions/(?P<tab>[\w-]+)$', 'client.promotions', name='client_promotions_tab'),
    url(r'^customers$', 'client.customers', name='client_customers'),
    url(r'^customer_profile/(?P<customer_id>[\d]+)', 'client.profile', name='customer_profile'),
    url(r'^business_profile', 'client.business_profile', name='business_profile'),
    url(r'^signup-form/create$', 'client.signup_form_create', name='signup_form_create'),
    url(r'^signup-form/list$', 'client.signup_form_list', name='client_signup_form_list'),
    url(r'^signup-form/(?P<slug>[\w-]+)/edit$', 'client.signup_form_edit', name='client_signup_form_edit'),
    url(r'^signup-form/(?P<slug>[\w-]+)/preview$', 'client.signup_form_preview', name='client_signup_form_preview'),
    url(r'^api/', include(api_urls)),
    url(r'^(?P<client_slug>[\w-]+)/(?P<form_slug>[\w-]+)$', 'customer.signup_view', name='customer_signup'),

    url(r'^enrichment-confirm-customer$', TemplateView.as_view(template_name='client/enrichment/enrichment-confirm-customer.html'), name='enrichment-confirm-customer'),
    url(r'^enrichment-choose-fiels$', TemplateView.as_view(template_name='client/enrichment/enrichment-choose-fiels.html'), name='enrichment-choose-fiels'),
    url(r'^enrichment-confirm-purchase$', TemplateView.as_view(template_name='client/enrichment/enrichment-confirm-purchase.html'), name='enrichment-confirm-purchase'),
)
