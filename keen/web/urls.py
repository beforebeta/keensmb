from django.conf.urls import patterns, url

from .views import client


urlpatterns = patterns(
    'keen.web.views',
    url(r'^client/$', client.dashboard, name='client_dashboard'),
    url(r'^client/promotions/$', client.promotions, name='client_promotions'),
    url(r'^client/customers/$', client.customers, name='client_customers'),
    url(r'^client/profile/$', client.profile, name='client_profile'),
)
