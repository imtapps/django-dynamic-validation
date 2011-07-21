import mock

from django.contrib.contenttypes.models import ContentType
from django.utils import unittest

from dynamic_validation import models, site
from dynamic_validation.tests.utils import get_violation

__all__ = (
    'RuleManagerTests', 'RuleModelTests',
    'ViolationManagerTests', 'ViolationModelTests',

)

class RuleManagerTests(unittest.TestCase):

    def setUp(self):
        self.model_one = mock.Mock()

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_content_type_for_model_in_get_by_group_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.RuleManager)
        models.RuleManager.get_by_group_object(manager, self.model_one)
        get_for_model.assert_called_once_with(self.model_one)

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_by_group_object_returns_rules_for_related_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.RuleManager)
        rules = models.RuleManager.get_by_group_object(manager, self.model_one)

        manager.filter.assert_called_once_with(
            content_type=get_for_model.return_value,
            group_object_id=self.model_one.pk,
        )
        self.assertEqual(manager.filter.return_value, rules)

class RuleModelTests(unittest.TestCase):

    def test_uses_rule_manager(self):
        self.assertIsInstance(models.Rule.objects, models.RuleManager)

    def test_run_action_runs_action_for_rule_class(self):
        rule_class = mock.Mock()
        site.register(rule_class)
        args = [mock.Mock()]
        kwargs = {'my_mock': mock.Mock()}
        validation_object = mock.Mock()
        try:
            rule = models.Rule(key=rule_class.key)
            rule.run_action(validation_object, *args, **kwargs)
            rule_class.assert_called_once_with(rule, validation_object)
            rule_class.return_value.run.assert_called_once_with(*args, **kwargs)
        finally:
            site.unregister(rule_class)

class ViolationManagerTests(unittest.TestCase):

    def setUp(self):
        self.model = mock.Mock()

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_content_type_for_model_in_get_by_validation_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.ViolationManager)
        models.ViolationManager.get_by_validation_object(manager, self.model)
        get_for_model.assert_called_once_with(self.model)

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_by_validation_object_returns_rules_for_related_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.ViolationManager)
        violations = models.ViolationManager.get_by_validation_object(manager, self.model)

        manager.filter.assert_called_once_with(
            content_type=get_for_model.return_value,
            validation_object_id=self.model.pk,
        )
        self.assertEqual(manager.filter.return_value, violations)

    def test_violations_queries_on_validation_object_and_rule_model(self):
        rule = models.Rule(pk=1)
        manager = mock.Mock(spec_set=models.ViolationManager)

        violations = models.ViolationManager.get_violations_for_rule(manager, rule, self.model)
        manager.get_by_validation_object.assert_called_once_with(self.model)
        base_query = manager.get_by_validation_object.return_value
        base_query.filter.assert_called_once_with(rule=rule)
        self.assertEqual(base_query.filter.return_value, violations)

class ViolationModelTests(unittest.TestCase):

    def test_validation_object_rule_and_key_are_unique(self):
        self.assertItemsEqual(
            [('validation_object_id', 'content_type', 'rule', 'key')],
            models.Violation._meta.unique_together)

    def test_violations_are_equal_when_validation_object_rule_key_and_fields_match(self):
        violation_one = get_violation(pk=1)
        violation_two = get_violation()
        self.assertEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_key_doesnt_match(self):
        violation_one = get_violation(key="123")
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_rule_doesnt_match(self):
        violation_one = get_violation(rule=models.Rule(pk=99))
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_content_type_doesnt_match(self):
        violation_one = get_violation(content_type=ContentType(pk=99))
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_validation_object_id_doesnt_match(self):
        violation_one = get_violation(validation_object_id=99)
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_violated_fields_doesnt_match(self):
        violation_one = get_violation(violated_fields={'a_value': 99})
        violation_two = get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_other_object_is_not_violation_model(self):
        violation = get_violation()
        self.assertNotEqual(violation, models.Rule())

