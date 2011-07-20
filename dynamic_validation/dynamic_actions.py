
from dynamic_validation.models import Violation

class BaseDynamicAction(object):

    def __init__(self, rule_model, validation_object):
        self.rule_model = rule_model
        self.validation_object = validation_object

    def run(self, *args, **kwargs):
        current_violations = self.get_current_violations(*args, **kwargs)
        if not isinstance(current_violations, list):
            raise TypeError("get_current_violations must return a list.")

        matching_violations = self.get_matching_violations(current_violations)
        self.save_violations(matching_violations, current_violations)

    def get_current_violations(self, *args, **kwargs):
        raise NotImplementedError

    def get_matching_violations(self, current_violations):
        pass

    def save_violations(self, matching_violations, current_violations):
        pass

    def create_violation(self, key, message, violated_fields):
        return Violation(
            rule=self.rule_model,
            validation_object=self.validation_object,
            key=key,
            message=message,
            violated_fields=violated_fields,
        )