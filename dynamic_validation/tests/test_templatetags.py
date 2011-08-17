import mock
from django.utils import unittest

from django.template import Context, Template, TemplateSyntaxError

__all__ = ('DynamicViolationTagTests', )

class DynamicViolationTagTests(unittest.TestCase):

    @mock.patch('dynamic_validation.models.Violation.objects.get_by_trigger_model')
    def test_violations_for_adds_violation_to_context(self, get_by_trigger_model):
        template = Template("""
            {% load dynamic_validation_tags %}

            {% violations_for validation_object as violations %}
            {% for violation in violations %}
                {{ violation }}
            {% endfor %}
        """)
        validation_object = mock.sentinel.validation_object
        get_by_trigger_model.return_value = ['one', 'two', 'three']

        result = template.render(Context(dict(validation_object=validation_object)))
        get_by_trigger_model.assert_called_once_with(validation_object)
        self.assertTrue("one" in result)
        self.assertTrue("two" in result)
        self.assertTrue("three" in result)

    @mock.patch('dynamic_validation.models.ViolationsWrapper')
    @mock.patch('dynamic_validation.models.Violation.objects.get_by_trigger_model')
    def test_violation_tag_wraps_query_results_in_violations_wrapper(self, get_by_object, wrapper_class):
        validation_object = mock.sentinel.validation_object
        template = Template("""
            {% load dynamic_validation_tags %}
            {% violations_for validation_object as violations %}
        """)
        context = dict(validation_object=validation_object)
        template.render(Context(context))
        wrapper_class.assert_called_once_with(get_by_object.return_value)
        self.assertEqual(context['violations'], wrapper_class.return_value)

    @mock.patch('dynamic_validation.models.Violation.objects.get_by_trigger_model')
    def test_violations_for_tag_can_resolve_callable_variable_for_violation_object(self, get_by_trigger_model):
        template = Template("""
            {% load dynamic_validation_tags %}

            {% violations_for get_validation_obj as violations %}
            {% for violation in violations %}
                {{ violation }}
            {% endfor %}
        """)
        validation_object = mock.sentinel.validation_object
        def get_validation_object():
            return validation_object
        get_by_trigger_model.return_value = ['one', 'two', 'three']

        result = template.render(Context(dict(get_validation_obj=get_validation_object)))
        get_by_trigger_model.assert_called_once_with(validation_object)
        self.assertTrue("one" in result)
        self.assertTrue("two" in result)
        self.assertTrue("three" in result)

    def test_calling_template_tag_without_var_name_raises_template_syntax_error(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("""
                {% load dynamic_validation_tags %}

                {% violations_for validation_object %}
            """)

    def test_calling_template_tag_without_validation_object_raises_template_syntax_error(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("""
                {% load dynamic_validation_tags %}

                {% violations_for as validation_object %}
            """)

    @mock.patch('dynamic_validation.models.Violation.objects.get_by_trigger_model', mock.MagicMock())
    def test_returns_empty_string_when_template_variable_does_not_exist(self):
        template = Template("""
            {% load dynamic_validation_tags %}
            {% violations_for get_validation_obj as violations %}
        """)
        result = template.render(Context({}))
        self.assertEqual('', result.strip())