import mock
from django.utils import unittest

from dynamic_validation import models
from dynamic_validation.dynamic_actions import BaseDynamicAction

__all__ = (
    'BaseDynamicActionTests',
)

class BaseDynamicActionTests(unittest.TestCase):

    def setUp(self):
        self.rule_model = models.Rule(pk=1)
        self.action = BaseDynamicAction(self.rule_model)

    def test_saves_rule_model_on_instance(self):
        self.assertEqual(self.rule_model, self.action.rule_model)

    @mock.patch.object(BaseDynamicAction, 'get_current_violations')
    def test_run_calls_get_current_violations_with_args_and_kwargs(self, get_current_violations):
        args = [mock.Mock()]
        kwargs = dict(mock=mock.Mock())

        self.action.run(*args, **kwargs)

        get_current_violations.assert_called_once_with(*args, **kwargs)

    @mock.patch.object(BaseDynamicAction, 'get_current_violations')
    @mock.patch.object(BaseDynamicAction, 'get_matching_violations')
    def test_run_calls_gets_matching_violations_with_current_violations(self, get_matching, get_current):
        self.action.run()
        get_matching.assert_called_once_with(get_current.return_value)

    @mock.patch.object(BaseDynamicAction, 'get_current_violations')
    @mock.patch.object(BaseDynamicAction, 'get_matching_violations')
    @mock.patch.object(BaseDynamicAction, 'save_violations')
    def test_run_calls_save_violations_with_matching_and_current_violations(self, *args):
        save, get_matching, get_current = args
        self.action.run()
        save.assert_called_once_with(get_matching.return_value, get_current.return_value)

    def test_get_current_violations_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.action.get_current_violations()