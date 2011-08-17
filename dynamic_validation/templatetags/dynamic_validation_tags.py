
from django.template import Library, Node, Variable
from django.template.base import TemplateSyntaxError, VariableDoesNotExist

from dynamic_validation import models
register = Library()

__all__ = ('violations_for', )

@register.tag
def violations_for(parser, token):
    """
    usage:
    {% violations_for trigger_model as var_name %}
    """
    bits = token.split_contents()
    if len(bits) != 4 or bits[2] != 'as':
        raise TemplateSyntaxError("Must pass 'trigger_model as var_name' to %s tag" % bits[0])
    return ViolationsForNode(bits[1], bits[3])

class ViolationsForNode(Node):
    def __init__(self, trigger_model, var_name):
        self.trigger_model = Variable(trigger_model)
        self.var_name = var_name

    def render(self, context):
        try:
            trigger_model = self.trigger_model.resolve(context)
            violations = models.Violation.objects.get_by_trigger_model(trigger_model)
            context[self.var_name] = models.ViolationsWrapper(violations)
        except VariableDoesNotExist: pass
        return ''