import mock

from django.contrib.contenttypes.models import ContentType
from django.utils import unittest

from dynamic_rules import models as rule_models
from dynamic_validation import models
from dynamic_validation.tests.utils import get_violation


__all__ = (
    'ViolationManagerTests',
    'ViolationModelTests',
    'ViolationWrapperTests',
)


class ViolationManagerTests(unittest.TestCase):

    def setUp(self):
        self.trigger_model = mock.Mock()

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_content_type_for_model_in_get_by_trigger_model(self, get_for_model):
        manager = mock.Mock(spec_set=models.ViolationManager)
        models.ViolationManager.get_by_trigger_model(manager, self.trigger_model)
        get_for_model.assert_called_once_with(self.trigger_model)

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_by_trigger_model_returns_rules_for_related_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.ViolationManager)
        violations = models.ViolationManager.get_by_trigger_model(manager, self.trigger_model)

        manager.filter.assert_called_once_with(
            trigger_content_type=get_for_model.return_value,
            trigger_model_id=self.trigger_model.pk,
        )
        self.assertEqual(manager.filter.return_value, violations)

    def test_violations_queries_on_validation_object_and_rule_model(self):
        rule = rule_models.Rule(pk=1)
        manager = mock.Mock(spec_set=models.ViolationManager)

        violations = models.ViolationManager.get_by_rule(manager, rule, self.trigger_model)
        manager.get_by_trigger_model.assert_called_once_with(self.trigger_model)
        base_query = manager.get_by_trigger_model.return_value
        base_query.filter.assert_called_once_with(rule=rule)
        self.assertEqual(base_query.filter.return_value, violations)

    def test_violations_queries_on_validation_object_and_rule_model(self):
        rule = rule_models.Rule(pk=1)
        manager = mock.Mock(spec_set=models.ViolationManager)

        violations = models.ViolationManager.get_by_rule(manager, rule, self.trigger_model)
        manager.get_by_trigger_model.assert_called_once_with(self.trigger_model)
        base_query = manager.get_by_trigger_model.return_value
        base_query.filter.assert_called_once_with(rule=rule)
        self.assertEqual(base_query.filter.return_value, violations)

    def test_unacceptable_violations_for_object_filters(self):
        manager = mock.Mock(spec_set=models.ViolationManager)
        violations = models.ViolationManager.get_unacceptable_violations_for_object(manager, self.trigger_model)

        manager.get_by_trigger_model.assert_called_once_with(self.trigger_model)
        exclude = manager.get_by_trigger_model.return_value.exclude
        exclude.assert_called_once_with(acceptable=models.ViolationStatus.accepted)
        self.assertEqual(exclude.return_value, violations)


class ViolationModelTests(unittest.TestCase):

    def test_validation_object_rule_and_key_are_unique(self):
        self.assertItemsEqual(
            [('trigger_model_id', 'trigger_content_type', 'rule', '_key')],
            models.Violation()._meta.unique_together)

    def test_orders_by_acceptable_status_by_default(self):
        self.assertEqual(('acceptable',), models.Violation()._meta.ordering)

    def test_violations_are_equal_when_validation_object_rule_key_and_fields_match(self):
        violation_one = get_violation(pk=1)
        violation_two = get_violation()
        self.assertEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_key_doesnt_match(self):
        violation_one = get_violation(key="123")
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_rule_doesnt_match(self):
        violation_one = get_violation(rule=rule_models.Rule(pk=99))
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_content_type_doesnt_match(self):
        violation_one = get_violation(trigger_content_type=ContentType(pk=99))
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_validation_object_id_doesnt_match(self):
        violation_one = get_violation(trigger_model_id=99)
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_violated_fields_doesnt_match(self):
        violation_one = get_violation(violated_fields={'a_value': 99})
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_other_object_is_not_violation_model(self):
        violation = get_violation()
        self.assertNotEqual(violation, rule_models.Rule())

    def test_setting_key_property_sets_key_field_value_as_string(self):
        violation = models.Violation(key=1)
        self.assertEqual('1', violation._key)

    def test_getting_key_gives_key_value(self):
        violation = models.Violation(_key="A Key")
        self.assertEqual("A Key", violation.key)


class ViolationWrapperTests(unittest.TestCase):

    def test_iterating_over_wrapper_iterates_over_queryset(self):
        violation_one = get_violation(key="123")
        violation_two = get_violation(key="ABC")
        violation_queryset = [violation_one, violation_two]
        violations_wrapper = models.ViolationsWrapper(violation_queryset)
        for qs, violations in zip(violation_queryset, violations_wrapper):
            self.assertEqual(qs, violations)

    def test_len_on_wrapper_returns_len_of_queryset(self):
        violation_queryset = ["one", "two"]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual(2, len(violations))

    def test_count_property_returns_len_of_queryset(self):
        violation_queryset = ["one", "two"]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual(2, violations.count)

    def test_unreviewed_property_returns_unreviewed_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.unreviewed)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.unreviewed)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.rejected)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual([violation_one, violation_two], violations.unreviewed)

    def test_accepted_property_returns_accepted_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.accepted)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.accepted)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.rejected)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual([violation_one, violation_two], violations.accepted)

    def test_rejected_property_returns_rejected_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.rejected)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.rejected)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.accepted)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual([violation_one, violation_two], violations.rejected)

    def test_unreviewed_count_returns_number_of_unreviewed_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.unreviewed)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.unreviewed)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.rejected)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual(2, violations.unreviewed_count)

    def test_accepted_count_returns_number_of_accepted_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.accepted)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.accepted)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.rejected)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual(2, violations.accepted_count)

    def test_accepted_count_returns_number_of_accepted_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.rejected)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.rejected)
        violation_three = get_violation(key="XYZ", acceptable=models.ViolationStatus.accepted)
        violation_queryset = [violation_one, violation_two, violation_three]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual(2, violations.rejected_count)

    def test_max_level_is_error_when_has_rejected_violations(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.rejected)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.unreviewed)
        violation_queryset = [violation_one, violation_two]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual("error", violations.max_level)

    def test_max_level_is_warn_when_no_rejected_but_has_unreviewed(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.unreviewed)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.accepted)
        violation_queryset = [violation_one, violation_two]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual("warn", violations.max_level)

    def test_max_level_is_ok_when_only_accepted(self):
        violation_one = get_violation(key="123", acceptable=models.ViolationStatus.accepted)
        violation_two = get_violation(key="ABC", acceptable=models.ViolationStatus.accepted)
        violation_queryset = [violation_one, violation_two]
        violations = models.ViolationsWrapper(violation_queryset)
        self.assertEqual("ok", violations.max_level)
