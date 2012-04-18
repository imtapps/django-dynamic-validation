
from django.contrib.contenttypes.models import ContentType

from dynamic_rules import models as rule_models
from dynamic_validation import models

__all__ = ('get_violation', )


def get_violation(**kwargs):
    return models.Violation(
        pk=kwargs.get('pk'),
        key=kwargs.get('key', "abc"),
        rule=kwargs.get("rule", rule_models.Rule(pk=100)),
        violated_fields=kwargs.get("violated_fields", {'field': 'one'}),
        trigger_content_type=kwargs.get("trigger_content_type", ContentType(pk=10)),
        trigger_model_id=kwargs.get("trigger_model_id", 1),
        message=kwargs.get('message'),
        acceptable=kwargs.get('acceptable'),
    )
