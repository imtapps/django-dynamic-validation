from django.db import models
from django.contrib.contenttypes import generic
#from django.contrib.contenttypes import models as contenttype_models

from django_fields import fields as helper_fields

#class ContentTypeMixinManager(models.Manager):
#
#    def get_by_related_object(self, related_object):
#        content_type = contenttype_models.ContentType.objects.get_for_model(related_object)
#        return self.filter(content_type=content_type,
#                           related_object_id=related_object.pk)
#
#class ContentTypeMixin(models.Model):
#    objects = ContentTypeMixinManager()
#    content_type = models.ForeignKey('contenttypes.ContentType')
#    related_object_id = models.PositiveIntegerField(db_index=True)
#    related_object = generic.GenericForeignKey(fk_field='related_object_id')
#
#    class Meta(object):
#        abstract = True

class Rule(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType')
    related_object_id = models.PositiveIntegerField(db_index=True)
    related_object = generic.GenericForeignKey(fk_field='related_object_id')

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    dynamic_fields = helper_fields.PickleField()

    def __unicode__(self):
        return self.name