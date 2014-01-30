from django.contrib import admin

from keen.enrichment.models import EnrichmentRequest


class EnrichmentRequestAdmin(admin.ModelAdmin):
    pass

admin.site.register(EnrichmentRequest, EnrichmentRequestAdmin)
