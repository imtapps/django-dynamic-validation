from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django_fields import fields as helper_fields

from dynamic_validation import site

__all__ = ('Violation', 'Rule', )

class RuleManager(models.Manager):

    def get_by_group_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, group_object_id=obj.pk)

class Rule(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType')
    group_object_id = models.PositiveIntegerField(db_index=True)
    group_object = generic.GenericForeignKey(fk_field='group_object_id')

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    dynamic_fields = helper_fields.PickleField()

    objects = RuleManager()

    def __unicode__(self):
        return self.name

    def run_action(self, validation_object, *args, **kwargs):
        rule_class = site.get_rule_class(self.key)
        rule_class(self, validation_object).run(*args, **kwargs)


class ViolationManager(models.Manager):

    def get_by_validation_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, validation_object_id=obj.pk)

    def get_violations_for_rule(self, rule, validation_object):
        base_query = self.get_by_validation_object(validation_object)
        return base_query.filter(rule=rule)

class ViolationStatus(object):
    unreviewed = None
    accepted = True
    rejected = False

class Violation(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType')
    validation_object_id = models.PositiveIntegerField(db_index=True)
    validation_object = generic.GenericForeignKey(fk_field='validation_object_id')

    rule = models.ForeignKey(Rule)
    key = models.CharField(max_length=30, help_text="A unique key to make this violation object unique with the rule.")
    message = models.CharField(max_length=100)
    acceptable = models.NullBooleanField()
    violated_fields = helper_fields.PickleField()

    objects = ViolationManager()

    def __unicode__(self):
        return self.message

    class Meta(object):
        unique_together = ('validation_object_id', 'content_type', 'rule', 'key')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return all([
            self.validation_object_id == other.validation_object_id,
            self.content_type == other.content_type,
            self.rule == other.rule,
            self.key == other.key,
            self.violated_fields == other.violated_fields,
        ])