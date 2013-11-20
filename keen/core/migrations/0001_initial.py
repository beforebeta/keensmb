# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Create HSTORE extension first
        db.execute('create extension if not exists hstore')

        # Adding model 'HStoreFieldCatalog'
        db.create_table(u'core_hstorefieldcatalog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('grouping', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('group_ranking', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['HStoreFieldCatalog'])

        # Adding model 'Image'
        db.create_table(u'core_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Client'])),
        ))
        db.send_create_signal(u'core', ['Image'])

        # Adding model 'Address'
        db.create_table(u'core_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state_province', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'core', ['Address'])

        # Adding model 'Location'
        db.create_table(u'core_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Client'])),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Address'])),
            ('is_main', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['Location'])

        # Adding unique constraint on 'Location', fields ['name', 'client']
        db.create_unique(u'core_location', ['name', 'client_id'])

        # Adding model 'Client'
        db.create_table(u'core_client', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'core', ['Client'])

        # Adding M2M table for field customer_fields on 'Client'
        m2m_table_name = db.shorten_name(u'core_client_customer_fields')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('client', models.ForeignKey(orm[u'core.client'], null=False)),
            ('hstorefieldcatalog', models.ForeignKey(orm[u'core.hstorefieldcatalog'], null=False))
        ))
        db.create_unique(m2m_table_name, ['client_id', 'hstorefieldcatalog_id'])

        # Adding M2M table for field groups on 'Client'
        m2m_table_name = db.shorten_name(u'core_client_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('client', models.ForeignKey(orm[u'core.client'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['client_id', 'group_id'])

        # Adding model 'CustomerSource'
        db.create_table(u'core_customersource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Client'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ref_id', self.gf('django.db.models.fields.IntegerField')()),
            ('ref_source', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'core', ['CustomerSource'])

        # Adding unique constraint on 'CustomerSource', fields ['client', 'name']
        db.create_unique(u'core_customersource', ['client_id', 'name'])

        # Adding model 'Customer'
        db.create_table(u'core_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Client'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.CustomerSource'])),
            ('data', self.gf('django_hstore.fields.DictionaryField')(db_index=True)),
            ('enrichment_status', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal(u'core', ['Customer'])

        # Adding M2M table for field locations on 'Customer'
        m2m_table_name = db.shorten_name(u'core_customer_locations')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customer', models.ForeignKey(orm[u'core.customer'], null=False)),
            ('location', models.ForeignKey(orm[u'core.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['customer_id', 'location_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CustomerSource', fields ['client', 'name']
        db.delete_unique(u'core_customersource', ['client_id', 'name'])

        # Removing unique constraint on 'Location', fields ['name', 'client']
        db.delete_unique(u'core_location', ['name', 'client_id'])

        # Deleting model 'HStoreFieldCatalog'
        db.delete_table(u'core_hstorefieldcatalog')

        # Deleting model 'Image'
        db.delete_table(u'core_image')

        # Deleting model 'Address'
        db.delete_table(u'core_address')

        # Deleting model 'Location'
        db.delete_table(u'core_location')

        # Deleting model 'Client'
        db.delete_table(u'core_client')

        # Removing M2M table for field customer_fields on 'Client'
        db.delete_table(db.shorten_name(u'core_client_customer_fields'))

        # Removing M2M table for field groups on 'Client'
        db.delete_table(db.shorten_name(u'core_client_groups'))

        # Deleting model 'CustomerSource'
        db.delete_table(u'core_customersource')

        # Deleting model 'Customer'
        db.delete_table(u'core_customer')

        # Removing M2M table for field locations on 'Customer'
        db.delete_table(db.shorten_name(u'core_customer_locations'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'customer_fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.HStoreFieldCatalog']", 'symmetrical': 'False'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'core.customer': {
            'Meta': {'object_name': 'Customer'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'enrichment_status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Location']", 'symmetrical': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.CustomerSource']"})
        },
        u'core.customersource': {
            'Meta': {'unique_together': "(('client', 'name'),)", 'object_name': 'CustomerSource'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ref_id': ('django.db.models.fields.IntegerField', [], {}),
            'ref_source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.hstorefieldcatalog': {
            'Meta': {'object_name': 'HStoreFieldCatalog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group_ranking': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'grouping': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'core.image': {
            'Meta': {'object_name': 'Image'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.location': {
            'Meta': {'unique_together': "(('name', 'client'),)", 'object_name': 'Location'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Address']"}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Client']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['core']
