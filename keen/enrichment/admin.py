from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import escape

from keen.enrichment.models import EnrichmentRequest


class EnrichmentRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'client', 'customer_list')
    exclude = ('modified', 'customers')

    def customer_list(self, req):
        return mark_safe('\n'.join(self._customer_link(c) for c in req.customers.all()))

    def _customer_link(self, cust):
        return mark_safe('<a href="{url}">{label}</a>'.format(
            url='/admin/core/customer/{customer_id}/'.format(customer_id=cust.id),
            label=escape(', '.join(
                filter(None, (
                    cust.data['email'],
                    cust.data['full_name'],
                )))),
        ))


admin.site.register(EnrichmentRequest, EnrichmentRequestAdmin)
