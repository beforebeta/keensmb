from django.db import models


class Visitor(models.Model):

    ip_address = models.IPAddressField()
    referrer = models.CharField(max_length=255, null=True)
    user_agent = models.CharField(max_length=255)
    first_visit = models.DateTimeField()
    visits = models.IntegerField()
    last_visit = models.DateTimeField()
    source = models.CharField(max_length=255, null=True)
    medium = models.CharField(max_length=255, null=True)
    campaign = models.CharField(max_length=255, null=True)
    keywords = models.CharField(max_length=255, null=True)
    term = models.CharField(max_length=255, null=True)
    content = models.CharField(max_length=255, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
