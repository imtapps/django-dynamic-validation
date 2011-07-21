
from django.template import Library, Node
from django.template.base import TemplateSyntaxError

from dynamic_validation.models import Violation
register = Library()

__all__ = ('violations_for', )

@register.tag
def violations_for(parser, token):
    """
    usage:
    {% violations_for validation_object as var_name %}
    """
    bits = token.split_contents()
    if len(bits) != 4 or bits[2] != 'as':
        raise TemplateSyntaxError("Must pass 'validation_object as var_name' to %s tag" % bits[0])
    return ViolationsForNode(bits[1], bits[3])

class ViolationsForNode(Node):
    def __init__(self, obj, var_name):
        self.obj = obj
        self.var_name = var_name

    def render(self, context):
        violations = Violation.objects.get_by_validation_object(context[self.obj])
        context[self.var_name] = violations
        return ''