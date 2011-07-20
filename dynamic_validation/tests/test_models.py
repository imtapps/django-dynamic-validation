import mock

from django.contrib.contenttypes.models import ContentType
from django.utils import unittest

from dynamic_validation import models, site

class RuleManagerTests(unittest.TestCase):

    def setUp(self):
        self.model_one = mock.Mock()
        self.model_two = mock.Mock()

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_content_type_for_model_in_get_by_related_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.RuleManager)
        models.RuleManager.get_by_group_object(manager, self.model_one)
        get_for_model.assert_called_once_with(self.model_one)

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_by_related_object_returns_rules_for_related_object(self, get_for_model):
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

class ViolationModelTests(unittest.TestCase):

    def test_validation_object_rule_and_key_are_unique(self):
        self.assertItemsEqual(
            [('validation_object_id', 'content_type', 'rule', 'key')],
            models.Violation._meta.unique_together)

    def get_violation(self, **kwargs):
        return models.Violation(
            pk=kwargs.get('pk'),
            key=kwargs.get('key', "abc"),
            rule=kwargs.get("rule", models.Rule(pk=100)),
            violated_fields=kwargs.get("violated_fields", {'field': 'one'}),
            content_type=kwargs.get("content_type", ContentType(pk=10)),
            validation_object_id=kwargs.get("validation_object_id", 1),
            )

    def test_violations_are_equal_when_validation_object_rule_key_and_fields_match(self):
        violation_one = self.get_violation(pk=1)
        violation_two = self.get_violation()
        self.assertEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_key_doesnt_match(self):
        violation_one = self.get_violation(key="123")
        violation_two = self.get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_rule_doesnt_match(self):
        violation_one = self.get_violation(rule=models.Rule(pk=99))
        violation_two = self.get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_content_type_doesnt_match(self):
        violation_one = self.get_violation(content_type=ContentType(pk=99))
        violation_two = self.get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_validation_object_id_doesnt_match(self):
        violation_one = self.get_violation(validation_object_id=99)
        violation_two = self.get_violation()
        self.assertNotEqual(violation_two, violation_one)

    def test_violations_are_not_equal_when_violated_fields_doesnt_match(self):
        violation_one = self.get_violation(violated_fields={'a_value': 99})
        violation_two = self.get_violation()
        self.assertNotEqual(violation_two, violation_one)
