# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Visitor.campaign'
        db.alter_column(u'tracking_visitor', 'campaign', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.medium'
        db.alter_column(u'tracking_visitor', 'medium', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.referrer'
        db.alter_column(u'tracking_visitor', 'referrer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.term'
        db.alter_column(u'tracking_visitor', 'term', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.content'
        db.alter_column(u'tracking_visitor', 'content', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.source'
        db.alter_column(u'tracking_visitor', 'source', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Visitor.keywords'
        db.alter_column(u'tracking_visitor', 'keywords', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Visitor.campaign'
        db.alter_column(u'tracking_visitor', 'campaign', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.medium'
        db.alter_column(u'tracking_visitor', 'medium', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.referrer'
        db.alter_column(u'tracking_visitor', 'referrer', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.term'
        db.alter_column(u'tracking_visitor', 'term', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.content'
        db.alter_column(u'tracking_visitor', 'content', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.source'
        db.alter_column(u'tracking_visitor', 'source', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Visitor.keywords'
        db.alter_column(u'tracking_visitor', 'keywords', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    models = {
        u'tracking.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'first_visit': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'last_visit': ('django.db.models.fields.DateTimeField', [], {}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'db_index': 'True'}),
            'visits': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['tracking']