# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field fields on 'PageCustomerField'
        m2m_table_name = db.shorten_name(u'web_pagecustomerfield_fields')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pagecustomerfield', models.ForeignKey(orm[u'web.pagecustomerfield'], null=False)),
            ('customerfield', models.ForeignKey(orm[u'core.customerfield'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pagecustomerfield_id', 'customerfield_id'])


    def backwards(self, orm):
        # Removing M2M table for field fields on 'PageCustomerField'
        db.delete_table(db.shorten_name(u'web_pagecustomerfield_fields'))


    models = {
        u'core.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.client': {
            'Meta': {'object_name': 'Client'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer_fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.CustomerField']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'core.customerfield': {
            'Meta': {'object_name': 'CustomerField'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'group_ranking': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'grouping': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'core.location': {
            'Meta': {'unique_together': "(('name', 'client'),)", 'object_name': 'Location'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Address']"}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'web.pagecustomerfield': {
            'Meta': {'object_name': 'PageCustomerField'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.CustomerField']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'web.signupform': {
            'Meta': {'object_name': 'SignupForm'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['web']