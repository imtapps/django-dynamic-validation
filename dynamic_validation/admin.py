from django.contrib import admin

from dynamic_validation import models


class ViolationAdmin(admin.ModelAdmin):
    list_display = ('rule', 'key', 'trigger_model', 'message', 'violated_fields')
    list_filter = ('rule', )

admin.site.register(models.Violation, ViolationAdmin)
