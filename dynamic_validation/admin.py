from django.contrib import admin
from dynamic_validation import models, admin_forms

from djadmin_ext.helpers import  BaseAjaxModelAdmin

class RuleAdmin(BaseAjaxModelAdmin):
    form = admin_forms.RuleForm
    list_display = ('name', 'group_object')

class ViolationAdmin(admin.ModelAdmin):
    list_display = ('rule', 'key', 'validation_object', 'message', 'violated_fields')
    list_filter = ('rule', )
admin.site.register(models.Rule, RuleAdmin)
admin.site.register(models.Violation, ViolationAdmin)