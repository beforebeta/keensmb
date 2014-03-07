from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

from .views.api.client import (ClientProfile, CustomerList, CustomerProfile,
                               SignupFormList, SignupFormView, ImageList)
from .views.api.import_export import ImportAPI
from keen.enrichment.views import enrich_customers_data_view


client_api_urls = patterns(
    'keen.web.views.api.client',
    url(r'^current$', 'current_client_view',
        name='current_client'),
    url(r'^num_customers$', 'num_customers'),
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
        url(r'^customers/import$', ImportAPI.as_view()),
        url(r'^customers/import/(?P<import_id>\d+)$', ImportAPI.as_view()),
    ))),
)

api_urls = patterns(
    'keen.web.views.api',
    url(r'^login$', 'user.login_view', name='login'),
    url(r'^logout$', 'user.logout_view', name='logout'),
    url(r'^client/', include(client_api_urls)),
    url(r'^request-free-trial$', 'user.request_free_trial', name='request-free-trial'),
)


urlpatterns = patterns(
    'keen.web.views',
    url(r'^$', 'landing.landing_view', name='home'),
    url(r'^legal$', TemplateView.as_view(template_name='front-page/legal.html'), name='legal'),
    url(r'^dashboard$', 'client.dashboard', name='client_dashboard'),

    url(r'^promotions$', 'client.promotions', name='client_promotions'),
    url(r'^promotions/create$', 'client.create_edit_promotion', name='client_create_promotion'),
    url(r'^promotions/(?P<promotion_id>\d+)/edit$', 'client.create_edit_promotion', name='client_edit_promotion'),
    url(r'^promotions/(?P<promotion_id>\d+)/preview', 'client.preview_promotion', name='client_preview_promotion'),
    url(r'^promotions/delete', 'client.delete_promotion', name='client_delete_promotion'),
    url(r'^promotions/approve', 'client.approve_promotion', name='client_approve_promotion'),
    url(r'^promotions/(?P<tab>[\w-]+)$', 'client.promotions', name='client_promotions_tab'),

    url(r'^customers$', 'client.customers', name='client_customers'),
    url(r'^customer_profile/(?P<customer_id>[\d]+)', 'client.profile', name='customer_profile'),
    url(r'^business_profile', 'client.business_profile', name='business_profile'),

    url(r'^signup-form/create$', 'client.signup_form_create', name='signup_form_create'),
    url(r'^signup-form/list$', 'client.signup_form_list', name='client_signup_form_list'),
    url(r'^signup-form/(?P<slug>[\w-]+)/edit$', 'client.signup_form_edit', name='client_signup_form_edit'),
    url(r'^signup-form/(?P<slug>[\w-]+)/preview$', 'client.signup_form_preview', name='client_signup_form_preview'),

    url(r'^api/client/(?P<client_slug>[\w-]+)/enrich$', enrich_customers_data_view, name='api_enrich'),

    url(r'^api/', include(api_urls)),

    url(r'^(?P<client_slug>[\w-]+)/(?P<form_slug>[\w-]+)/$', 'customer.signup_view', name='customer_signup'),

    url(r'^enrichment-confirm-customer$', TemplateView.as_view(template_name='client/enrichment/enrichment-confirm-customer.html'), name='enrichment-confirm-customer'),
    url(r'^enrichment-choose-fields$', TemplateView.as_view(template_name='client/enrichment/enrichment-choose-fields.html'), name='enrichment-choose-fiels'),
    url(r'^enrichment-confirm-purchase$', TemplateView.as_view(template_name='client/enrichment/enrichment-confirm-purchase.html'), name='enrichment-confirm-purchase'),

    url(r'^landing3$', TemplateView.as_view(template_name='front-page/landing3.html'), name='landing3.html'),
    url(r'^landing4$', TemplateView.as_view(template_name='front-page/landing4.html'), name='landing4.html'),
    url(r'^email_template$', 'client.email_template')
)
