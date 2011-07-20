from django.contrib import admin
from dynamic_validation import models, admin_forms

from djadmin_ext.helpers import  BaseAjaxModelAdmin

class RuleAdmin(BaseAjaxModelAdmin):
    form = admin_forms.RuleForm
    list_display = ('name', 'group_object')

admin.site.register(models.Rule, RuleAdmin)