
from django.contrib.contenttypes.models import ContentType

from dynamic_validation import models

__all__ = ('get_violation', )

def get_violation(**kwargs):
    return models.Violation(
        pk=kwargs.get('pk'),
        key=kwargs.get('key', "abc"),
        rule=kwargs.get("rule", models.Rule(pk=100)),
        violated_fields=kwargs.get("violated_fields", {'field': 'one'}),
        content_type=kwargs.get("content_type", ContentType(pk=10)),
        validation_object_id=kwargs.get("validation_object_id", 1),
        message=kwargs.get('message'),
    )