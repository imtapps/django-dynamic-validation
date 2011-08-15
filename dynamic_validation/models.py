from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django_fields import fields as helper_fields

__all__ = ('Violation', )


class ViolationsWrapper(object):
    """
    Wraps a violation queryset and provides an easy way to get
    violations by status, the count of each, and the max level.
    """

    def __init__(self, violations):
        self.violations = violations

    def __iter__(self):
        return iter(self.violations)

    def __len__(self):
        return len(self.violations)

    def _get_by_status(self, status):
        return [v for v in self.violations if v.acceptable == status]

    @property
    def count(self):
        return len(self)

    @property
    def unreviewed(self):
        return self._get_by_status(ViolationStatus.unreviewed)

    @property
    def accepted(self):
        return self._get_by_status(ViolationStatus.accepted)

    @property
    def rejected(self):
        return self._get_by_status(ViolationStatus.rejected)

    @property
    def unreviewed_count(self):
        return len(self.unreviewed)

    @property
    def accepted_count(self):
        return len(self.accepted)

    @property
    def rejected_count(self):
        return len(self.rejected)

    @property
    def max_level(self):
        if self.rejected_count:
            return "error"
        elif self.unreviewed_count:
            return "warn"
        else:
            return "ok"

    
class ViolationManager(models.Manager):

    def get_by_validation_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, validation_object_id=obj.pk)

    def get_violations_for_rule(self, rule, validation_object):
        base_query = self.get_by_validation_object(validation_object)
        return base_query.filter(rule=rule)

    def get_unacceptable_violations_for_object(self, obj):
        return self.get_by_validation_object(obj).exclude(acceptable=ViolationStatus.accepted)

class ViolationStatus(object):
    unreviewed = None
    accepted = True
    rejected = False

class Violation(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType')
    validation_object_id = models.PositiveIntegerField(db_index=True)
    validation_object = generic.GenericForeignKey(fk_field='validation_object_id')

    rule = models.ForeignKey('dynamic_rules.Rule')
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