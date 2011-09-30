# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Violation', fields ['key', 'trigger_model_id', 'trigger_content_type', 'rule']
        db.delete_unique('dynamic_validation_violation', ['key', 'trigger_model_id', 'trigger_content_type_id', 'rule_id'])

        # Deleting field 'Violation.key'
        db.delete_column('dynamic_validation_violation', 'key')

        # Changing field 'Violation._key to be non nullable'
        db.alter_column('dynamic_validation_violation', '_key', self.gf('django.db.models.fields.CharField')(default='', max_length=30))

        # Adding unique constraint on 'Violation', fields ['_key', 'trigger_model_id', 'trigger_content_type', 'rule']
        db.create_unique('dynamic_validation_violation', ['_key', 'trigger_model_id', 'trigger_content_type_id', 'rule_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Violation', fields ['_key', 'trigger_model_id', 'trigger_content_type', 'rule']
        db.delete_unique('dynamic_validation_violation', ['_key', 'trigger_model_id', 'trigger_content_type_id', 'rule_id'])

        # Adding field 'Violation.key'
        db.add_column('dynamic_validation_violation', 'key', self.gf('django.db.models.fields.CharField')(max_length=30, null=True), keep_default=False)


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dynamic_rules.rule': {
            'Meta': {'object_name': 'Rule'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'dynamic_fields': ('django_fields.fields.PickleField', [], {}),
            'group_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dynamic_validation.violation': {
            'Meta': {'ordering': "('acceptable',)", 'unique_together': "(('trigger_model_id', 'trigger_content_type', 'rule', '_key'),)", 'object_name': 'Violation'},
            '_key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'acceptable': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_rules.Rule']"}),
            'trigger_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'violations'", 'to': "orm['contenttypes.ContentType']"}),
            'trigger_model_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'violated_fields': ('django_fields.fields.PickleField', [], {})
        }
    }

    complete_apps = ['dynamic_validation']
