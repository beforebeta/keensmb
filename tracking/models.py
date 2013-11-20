from uuid import uuid4
from django.db import models


class Visitor(models.Model):

    uuid = models.CharField(max_length=36, unique=True, db_index=True)
    ip_address = models.IPAddressField()
    referrer = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    first_visit = models.DateTimeField()
    visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField()
    source = models.CharField(max_length=255)
    medium = models.CharField(max_length=255)
    campaign = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    term = models.CharField(max_length=255)
    content = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kw):
        if not self.uuid:
            self.uuid = uuid4()
        super(models.Model, self).save(*args, **kw)
