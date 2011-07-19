
from django import forms

from dynamic_validation import site

@site.register
class GenderRatio(object):
    key = "GenderRatio"
    display_name = "Ratio of Men to Women must be within x%."

    fields = {
        'percent': forms.IntegerField(help_text="Ratio of Men to Women"),
    }