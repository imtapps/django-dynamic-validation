
from django.template import Library, Node, Variable
from django.template.base import TemplateSyntaxError, VariableDoesNotExist

from dynamic_validation import models


register = Library()

__all__ = ('violations_for', )


@register.tag
def violations_for(parser, token):
    """
    usage:
    {% violations_for trigger_model as var_name optional_silent_indicator_variable %}
    """
    bits = token.split_contents()
    if len(bits) < 4 or bits[2] != 'as':
        raise TemplateSyntaxError("Must pass 'trigger_model as var_name' to %s tag" % bits[0])
    node_args = [bits[1], bits[3]]
    if len(bits) == 5:
        node_args.append(bits[4])
    return ViolationsForNode(*node_args)


class ViolationsForNode(Node):

    def __init__(self, trigger_model, var_name, silent_indicator=None):
        self.trigger_model = Variable(trigger_model)
        self.var_name = var_name
        self.silent_indicator = silent_indicator

    def render(self, context):
        silent_indicator = Variable(self.silent_indicator).resolve(context) if self.silent_indicator else None
        try:
            trigger_model = self.trigger_model.resolve(context)
            violations = models.Violation.objects.get_by_trigger_model(trigger_model)
            if silent_indicator:                                                                                                                                            
                violations = [v for v in violations if not v.rule.dynamic_fields.get('silent')]                                                                           
            context[self.var_name] = models.ViolationsWrapper(violations)
        except VariableDoesNotExist:
            pass
        return ''

