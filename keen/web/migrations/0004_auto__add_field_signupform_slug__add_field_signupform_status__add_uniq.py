# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SignupForm.slug'
        db.add_column(u'web_signupform', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default=None, max_length=50),
                      keep_default=False)

        # Adding field 'SignupForm.status'
        db.add_column(u'web_signupform', 'status',
                      self.gf('django.db.models.fields.CharField')(default='draft', max_length=32),
                      keep_default=False)

        # Adding M2M table for field fields on 'SignupForm'
        m2m_table_name = db.shorten_name(u'web_signupform_fields')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('signupform', models.ForeignKey(orm[u'web.signupform'], null=False)),
            ('customerfield', models.ForeignKey(orm[u'core.customerfield'], null=False))
        ))
        db.create_unique(m2m_table_name, ['signupform_id', 'customerfield_id'])

        # Adding unique constraint on 'SignupForm', fields ['client', 'slug']
        db.create_unique(u'web_signupform', ['client_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'SignupForm', fields ['client', 'slug']
        db.delete_unique(u'web_signupform', ['client_id', 'slug'])

        # Deleting field 'SignupForm.slug'
        db.delete_column(u'web_signupform', 'slug')

        # Deleting field 'SignupForm.status'
        db.delete_column(u'web_signupform', 'status')

        # Removing M2M table for field fields on 'SignupForm'
        db.delete_table(db.shorten_name(u'web_signupform_fields'))


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
            'main_location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['core.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'core.customerfield': {
            'Meta': {'object_name': 'CustomerField'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['core.CustomerFieldGroup']"}),
            'group_ranking': ('django.db.models.fields.IntegerField', [], {'default': '99999999'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.customerfieldgroup': {
            'Meta': {'object_name': 'CustomerFieldGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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
            'fields': ('django.db.models.fields.CharField', [], {'default': "'first_name,last_name,email'", 'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'web.signupform': {
            'Meta': {'unique_together': "(('client', 'slug'),)", 'object_name': 'SignupForm'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.CustomerField']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '32'})
        }
    }

    complete_apps = ['web']