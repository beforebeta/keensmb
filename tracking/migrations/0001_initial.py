# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Visitor'
        db.create_table(u'tracking_visitor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, db_index=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('referrer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('first_visit', self.gf('django.db.models.fields.DateTimeField')()),
            ('visits', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_visit', self.gf('django.db.models.fields.DateTimeField')()),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('campaign', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tracking', ['Visitor'])


    def backwards(self, orm):
        # Deleting model 'Visitor'
        db.delete_table(u'tracking_visitor')


    models = {
        u'tracking.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'first_visit': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_visit': ('django.db.models.fields.DateTimeField', [], {}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'db_index': 'True'}),
            'visits': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['tracking']