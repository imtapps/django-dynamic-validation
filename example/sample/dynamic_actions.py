
from django import forms

from dynamic_validation import site

@site.register
class GenderRatio(object):
    key = "GenderRatio"
    display_name = "Ratio of Men to Women must be within x%."

    fields = {
        'percent': forms.IntegerField(help_text="Ratio of Men to Women"),
    }

@site.register
class LimitNumberOfPlayersUnderAge(object):
    key = "LimitNumberOfPlayersUnderAge"
    display_name = "Limit the number of players under a given age"

    fields = {
        'players': forms.IntegerField(help_text="Maximum players allowed below age."),
        'age': forms.IntegerField(help_text="Minimum age."),
    }

@site.register
class RangeOfAveragePlayerAge(object):
    key = "RangeOfAveragePlayerAge"
    display_name = "the average age of all players on a team must be within an allowed range."

    fields = {
        'players': forms.IntegerField(help_text="Maximum players allowed below age."),
        'min_age': forms.IntegerField(help_text="Minimum average age allowed."),
        'max_age': forms.IntegerField(help_text="Maximum average age allowed."),
    }