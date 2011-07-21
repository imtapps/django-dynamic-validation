import mock
from django.utils import unittest

from django.template import Context, Template, TemplateSyntaxError

__all__ = ('DynamicViolationTagTests', )

class DynamicViolationTagTests(unittest.TestCase):

    @mock.patch('dynamic_validation.models.Violation.objects.get_by_validation_object')
    def test_violations_for_adds_violation_to_context(self, get_by_validation_object):
        template = Template("""
            {% load dynamic_validation_tags %}

            {% violations_for validation_object as violations %}
            {% for violation in violations %}
                {{ violation }}
            {% endfor %}
        """)
        validation_object = mock.Mock()
        get_by_validation_object.return_value = ['one', 'two', 'three']

        result = template.render(Context(dict(validation_object=validation_object)))
        get_by_validation_object.assert_called_once_with(validation_object)
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