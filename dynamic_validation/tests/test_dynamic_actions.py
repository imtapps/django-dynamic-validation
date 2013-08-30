import mock

from django import test as unittest
from django.contrib.auth.models import User

from dynamic_rules import models as rule_models
from dynamic_validation import models
from dynamic_validation.dynamic_actions import BaseDynamicValidation, BadViolationType
from dynamic_validation.tests.utils import get_violation

__all__ = (
    'BaseDynamicActionTests',
)


class BaseDynamicActionTests(unittest.TestCase):

    def setUp(self):
        self.rule_model = rule_models.Rule(pk=1)
        self.trigger_model = User.objects.create(username="test_admin")
        self.action = BaseDynamicValidation(self.rule_model, self.trigger_model)

    def test_accepted_status_is_unreviewed_by_default(self):
        self.assertEqual(models.ViolationStatus.unreviewed, self.action.accepted_status)

    def test_saves_rule_model_on_instance(self):
        self.assertEqual(self.rule_model, self.action.rule_model)

    def test_saves_validation_object_on_instance(self):
        self.assertEqual(self.trigger_model, self.action.trigger_model)

    @mock.patch.object(BaseDynamicValidation, 'get_current_violations')
    def test_run_calls_get_current_violations_with_args_and_kwargs(self, get_current_violations):
        get_current_violations.return_value = []

        args = [mock.Mock()]
        kwargs = dict(mock=mock.Mock())

        self.action.run(*args, **kwargs)

        get_current_violations.assert_called_once_with(*args, **kwargs)

    @mock.patch.object(BaseDynamicValidation, 'get_current_violations')
    @mock.patch.object(BaseDynamicValidation, 'get_matching_violations')
    def test_run_calls_gets_matching_violations_with_current_violations(self, get_matching, get_current):
        get_current.return_value = []
        self.action.run()
        get_matching.assert_called_once_with(get_current.return_value)

    @mock.patch.object(BaseDynamicValidation, 'get_current_violations')
    @mock.patch.object(BaseDynamicValidation, 'get_matching_violations')
    @mock.patch.object(BaseDynamicValidation, 'save_violations')
    def test_run_calls_save_violations_with_matching_and_current_violations(self, *args):
        save, get_matching, get_current = args
        get_current.return_value = []
        self.action.run()
        save.assert_called_once_with(get_matching.return_value, get_current.return_value)

    def test_get_current_violations_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.action.get_current_violations()

    @mock.patch.object(BaseDynamicValidation, 'get_current_violations')
    def test_raises_type_error_when_a_current_violations_not_violation_instance(self, get_violations):
        get_violations.return_value = [models.Violation(), mock.Mock()]

        with self.assertRaises(BadViolationType):
            self.action.run()

    @mock.patch.object(BaseDynamicValidation, 'get_current_violations', mock.Mock(return_value=None))
    def test_clean_violations_returns_empty_list_when_current_violations_is_none(self):
        self.assertEqual([], self.action.get_cleaned_violations())

    def test_wraps_single_violation_in_list_in_get_cleaned_violations(self):
        violation = models.Violation(pk=1)

        with mock.patch.object(BaseDynamicValidation, 'get_current_violations', mock.Mock(return_value=violation)):
            violations = self.action.get_cleaned_violations()
        self.assertEqual([violation], violations)

    def test_create_violation_returns_unsaved_rule_violation(self):
        key = "key"
        message = "message"
        violated_fields = {'my_field': 'value'}
        self.action.accepted_status = models.ViolationStatus.rejected

        violation = self.action.create_violation(
            key=key,
            message=message,
            violated_fields=violated_fields,
        )

        self.assertIsInstance(violation, models.Violation)
        self.assertEqual(None, violation.pk)
        self.assertEqual(key, violation.key)
        self.assertEqual(message, violation.message)
        self.assertEqual(violated_fields, violation.violated_fields)
        self.assertEqual(self.rule_model, violation.rule)
        self.assertEqual(self.trigger_model, violation.trigger_model)
        self.assertEqual(models.ViolationStatus.rejected, violation.acceptable)

    def test_create_violation_returns_unsaved_rule_violation_with_silent_indicator_sets_to_value_of_indicator(self):
        key = "key"
        message = "message"
        violated_fields = {'my_field': 'value'}
        self.action.accepted_status = models.ViolationStatus.rejected

        violation = self.action.create_violation(
            key=key,
            message=message,
            violated_fields=violated_fields
        )

        self.assertIsInstance(violation, models.Violation)
        self.assertEqual(None, violation.pk)
        self.assertEqual(key, violation.key)
        self.assertEqual(message, violation.message)
        self.assertEqual(violated_fields, violation.violated_fields)
        self.assertEqual(self.rule_model, violation.rule)
        self.assertEqual(self.trigger_model, violation.trigger_model)
        self.assertEqual(models.ViolationStatus.rejected, violation.acceptable)

    @mock.patch.object(models.Violation.objects, 'get_by_rule')
    def test_get_matching_violations_gets_existing_violations(self, get_violations):
        get_violations.return_value = []

        self.action.get_matching_violations([])
        get_violations.assert_called_once_with(self.rule_model, self.trigger_model)

    @mock.patch.object(models.Violation.objects, 'get_by_rule')
    def test_get_matching_violations_returns_list_violations_that_are_existing_and_current(self, get_violations):
        violation = mock.Mock(spec_set=models.Violation)
        violation2 = mock.Mock(spec_set=models.Violation)
        get_violations.return_value = [violation, violation2]

        matched_violations = self.action.get_matching_violations([violation])
        self.assertEqual([violation], matched_violations)

    @mock.patch.object(models.Violation.objects, 'get_by_rule')
    def test_get_matching_violations_deletes_existing_violations_that_are_not_current(self, get_violations):
        violation = mock.Mock(spec_set=models.Violation)
        violation2 = mock.Mock(spec_set=models.Violation)
        get_violations.return_value = [violation, violation2]

        self.action.get_matching_violations([violation])
        self.assertFalse(violation.delete.called)
        violation2.delete.assert_called_once_with()

    def test_save_violations_saves_current_violations_not_matched(self):
        violation = mock.Mock(spec_set=models.Violation)
        violation2 = mock.Mock(spec_set=models.Violation)
        violation3 = mock.Mock(spec_set=models.Violation)

        self.action.save_violations([violation3], [violation, violation2])
        violation.save.assert_called_once_with()
        violation2.save.assert_called_once_with()
        self.assertFalse(violation3.save.called)

    @mock.patch('dynamic_validation.models.Violation.save', mock.Mock())
    def test_save_violation_updates_message_when_violation_already_exists(self):
        violation = get_violation(message="A new message")
        existing_violation = get_violation(message="An old message")
        violation2 = mock.Mock(spec_set=models.Violation())

        self.action.save_violations([existing_violation], [violation, violation2])

        self.assertEqual(violation.message, existing_violation.message)
        existing_violation.save.assert_called_once_with()
