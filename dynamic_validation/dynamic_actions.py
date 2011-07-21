
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

    def get_existing_violations(self):
        return Violation.objects.get_violations_for_rule(self.rule_model, self.validation_object)

    def get_matching_violations(self, current_violations):
        """
        If a violation used to exist, but is not in the new violations
        we assume that the issue has been fixed and delete old record.
        """
        existing_violations = self.get_existing_violations()
        matched_violations = []
        for existing_violation in existing_violations:
            if existing_violation in current_violations:
                matched_violations.append(existing_violation)
            else:
                existing_violation.delete()
        return matched_violations
    
    def save_violations(self, matching_violations, current_violations):
        for violation in current_violations:
            if violation in matching_violations:
                position = matching_violations.index(violation)
                existing_violation = matching_violations[position]
                existing_violation.message = violation.message
                existing_violation.save()
            else:
                violation.save()

    def create_violation(self, key, message, violated_fields):
        return Violation(
            rule=self.rule_model,
            validation_object=self.validation_object,
            key=key,
            message=message,
            violated_fields=violated_fields,
        )