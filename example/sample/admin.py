
from django import forms
from django.contrib import admin
from django.contrib.contenttypes import models as contenttype_models

from dynamic_rules import admin_forms
from dynamic_rules import models as rule_models
from dynamic_rules import admin as rule_admin

from sample import models


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    list_filter = ('league',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'team', )
    list_filter = ('team', 'team__league')


class RuleForm(admin_forms.RuleForm):
    def __init__(self, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        self.fields['group_object_id'] = forms.ChoiceField(
            choices=((l.pk, l) for l in models.League.objects.all()),
            label="League",
        )

    def save(self, commit=True):
        content_type = contenttype_models.ContentType.objects.get_for_model(models.League)
        self.instance.content_type = content_type
        return super(RuleForm, self).save(commit)

    class Meta(object):
        model = rule_models.Rule
        fields = ('name', 'key', 'group_object_id')


class RuleAdmin(rule_admin.RuleAdmin):
    form = RuleForms
    list_display = ('name', 'group_obj')

    def group_obj(self, obj):
        return obj.group_object
    group_obj.short_description = "League"

admin.site.unregister(rule_models.Rule)
admin.site.register(rule_models.Rule, RuleAdmin)

admin.site.register(models.League)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Player, PlayerAdmin)
