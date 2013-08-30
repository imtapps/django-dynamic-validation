
from dynamic_rules.ext import RuleExtensionManager

from django.db import models
from django.contrib.contenttypes import generic
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


class ViolationManager(RuleExtensionManager):

    def get_unacceptable_violations_for_object(self, trigger_model, silent=None):
        return self.get_by_trigger_model(trigger_model).exclude(acceptable=ViolationStatus.accepted)


class ViolationStatus(object):
    unreviewed = None
    accepted = True
    rejected = False


class Violation(models.Model):
    """
    They '_key' field should be something that uniquely identifies the
    violation within the trigger model and rule. You can use the 'key'
    property to set the '_key' field forcing the value to a string.
    """
    trigger_content_type = models.ForeignKey('contenttypes.ContentType', related_name='violations')
    trigger_model_id = models.PositiveIntegerField(db_index=True)
    trigger_model = generic.GenericForeignKey(fk_field='trigger_model_id', ct_field='trigger_content_type')

    rule = models.ForeignKey('dynamic_rules.Rule')
    _key = models.CharField(max_length=30, help_text="A unique key to make this violation object unique with the rule.")
    message = models.CharField(max_length=300)
    acceptable = models.NullBooleanField()
    violated_fields = helper_fields.PickleField()

    objects = ViolationManager()

    def __unicode__(self):
        return self.message

    class Meta(object):
        unique_together = ('trigger_model_id', 'trigger_content_type', 'rule', '_key')
        ordering = ('acceptable',)

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, val):
        self._key = str(val)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return all([
            self.trigger_model_id == other.trigger_model_id,
            self.trigger_content_type == other.trigger_content_type,
            self.rule == other.rule,
            self.key == other.key,
            self.violated_fields == other.violated_fields,
        ])
