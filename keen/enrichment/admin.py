from django.contrib import admin

from keen.enrichment.models import EnrichmentRequest


class EnrichmentRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'client', 'customer_list')
    exclude = ('modified', 'customers')

    def customer_list(self, req):
        return '\n'.join(', '.join(filter(None, (
            (c.data['email'],
             c.data['full_name'],
             c.data['dob'],
             c.data['phone'],
             c.data['address__zipcode'],
             )))) for c in req.customers.all())


admin.site.register(EnrichmentRequest, EnrichmentRequestAdmin)
