# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SignupForm.created'
        db.alter_column(u'web_signupform', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'SignupForm.modified'
        db.alter_column(u'web_signupform', 'modified', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Dashboard.created'
        db.alter_column(u'web_dashboard', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Dashboard.modified'
        db.alter_column(u'web_dashboard', 'modified', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'PageCustomerField.created'
        db.alter_column(u'web_pagecustomerfield', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'PageCustomerField.modified'
        db.alter_column(u'web_pagecustomerfield', 'modified', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'TrialRequest.created'
        db.alter_column(u'web_trialrequest', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'TrialRequest.modified'
        db.alter_column(u'web_trialrequest', 'modified', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):

        # Changing field 'SignupForm.created'
        db.alter_column(u'web_signupform', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'SignupForm.modified'
        db.alter_column(u'web_signupform', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'Dashboard.created'
        db.alter_column(u'web_dashboard', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'Dashboard.modified'
        db.alter_column(u'web_dashboard', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'PageCustomerField.created'
        db.alter_column(u'web_pagecustomerfield', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'PageCustomerField.modified'
        db.alter_column(u'web_pagecustomerfield', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'TrialRequest.created'
        db.alter_column(u'web_trialrequest', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'TrialRequest.modified'
        db.alter_column(u'web_trialrequest', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

    models = {
        u'core.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_image_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.client': {
            'Meta': {'object_name': 'Client'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'customer_fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.CustomerField']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ref_id_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'web_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.customerfield': {
            'Meta': {'object_name': 'CustomerField'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['core.CustomerFieldGroup']"}),
            'group_ranking': ('django.db.models.fields.IntegerField', [], {'default': '99999999'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.customerfieldgroup': {
            'Meta': {'object_name': 'CustomerFieldGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.location': {
            'Meta': {'unique_together': "(('name', 'client'),)", 'object_name': 'Location'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Address']"}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
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
            'visits': ('django.db.models.fields.IntegerField', [], {})
        },
        u'web.dashboard': {
            'Meta': {'object_name': 'Dashboard'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'new_customers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'promotions_this_month': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'redemptions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_customers': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'web.pagecustomerfield': {
            'Meta': {'object_name': 'PageCustomerField'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'fields': ('django.db.models.fields.CharField', [], {'default': "'first_name,last_name,email'", 'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'web.signupform': {
            'Meta': {'unique_together': "(('client', 'slug'),)", 'object_name': 'SignupForm'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'signup_forms'", 'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '32'}),
            'visitors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'signup_forms'", 'symmetrical': 'False', 'to': u"orm['tracking.Visitor']"}),
            'visits': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'web.trialrequest': {
            'Meta': {'object_name': 'TrialRequest'},
            'business': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracking.Visitor']", 'null': 'True'})
        }
    }

    complete_apps = ['web']