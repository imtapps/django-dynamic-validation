from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django_fields import fields as helper_fields

from dynamic_validation import site

class RuleManager(models.Manager):

    def get_by_related_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, related_object_id=obj.pk)

class Rule(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType')
    related_object_id = models.PositiveIntegerField(db_index=True)
    related_object = generic.GenericForeignKey(fk_field='related_object_id')

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    dynamic_fields = helper_fields.PickleField()

    objects = RuleManager()

    def __unicode__(self):
        return self.name

    @property
    def action_class(self):
        return site.get_rule_class(self.key)
