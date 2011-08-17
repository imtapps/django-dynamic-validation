# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for violation in orm.Violation.objects.all():
            violation.trigger_content_type = violation.content_type
            violation.trigger_model_id = violation.validation_object_id
            violation.save()

    def backwards(self, orm):
        for violation in orm.Violation.objects.all():
            violation.content_type = violation.trigger_content_type
            violation.validation_object_id = violation.trigger_model_id
            violation.save()

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
            'Meta': {'unique_together': "(('validation_object_id', 'content_type', 'rule', 'key'),)", 'object_name': 'Violation'},
            'acceptable': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_rules.Rule']"}),
            'trigger_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'violations'", 'to': "orm['contenttypes.ContentType']"}),
            'trigger_model_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'validation_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'violated_fields': ('django_fields.fields.PickleField', [], {})
        }
    }

    complete_apps = ['dynamic_validation']
