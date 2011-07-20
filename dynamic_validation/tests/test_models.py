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
        models.RuleManager.get_by_related_object(manager, self.model_one)
        get_for_model.assert_called_once_with(self.model_one)

    @mock.patch.object(ContentType.objects, 'get_for_model')
    def test_get_by_related_object_returns_rules_for_related_object(self, get_for_model):
        manager = mock.Mock(spec_set=models.RuleManager)
        rules = models.RuleManager.get_by_related_object(manager, self.model_one)

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
        try:
            rule = models.Rule(key=rule_class.key)
            rule.run_action(*args, **kwargs)
            rule_class.assert_called_once_with(rule)
            rule_class.return_value.run.assert_called_once_with(*args, **kwargs)
        finally:
            site.unregister(rule_class)