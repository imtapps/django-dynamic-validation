
from django import forms
from django.db.models import Avg

from dynamic_rules import site
from dynamic_validation.dynamic_actions import BaseDynamicValidation


@site.register
class GenderRatio(BaseDynamicValidation):
    key = "GenderRatio"
    display_name = "Ratio of Men to Women must be within x%."
    trigger_model_name = 'team'

    fields = {
        'percent': forms.IntegerField(help_text="Ratio of Men to Women"),
    }

    def get_current_violations(self, *args, **kwargs):
        acceptable_percent = self.rule_model.dynamic_fields['percent'] / 100.0

        male_players = self.team.players.filter(gender=1).count()
        female_players = self.team.players.filter(gender=2).count()

        all_players = (male_players + female_players) * 1.0
        male_percent = male_players / all_players
        female_percent = female_players / all_players

        violation_fields = dict(males=male_players, females=female_players)
        if male_percent > acceptable_percent:
            message = "Violated... %s men over coed percent allowed (%s)" % (male_percent, acceptable_percent)
            return self.create_violation(self.team.pk, message, violation_fields)
        elif female_percent > acceptable_percent:
            message = "Violated... %s female over coed percent allowed (%s)" % (female_percent, acceptable_percent)
            return self.create_violation(self.team.pk, message, violation_fields)


@site.register
class LimitNumberOfPlayersUnderAge(BaseDynamicValidation):
    key = "LimitNumberOfPlayersUnderAge"
    display_name = "Limit the number of players under a given age"
    trigger_model_name = 'team'

    fields = {
        'players': forms.IntegerField(help_text="Maximum players allowed below age."),
        'age': forms.IntegerField(help_text="Minimum age."),
    }

    def get_current_violations(self, *args, **kwargs):
        min_age = self.rule_model.dynamic_fields['age']
        player_count_limit = self.rule_model.dynamic_fields['players']

        players_under_age = self.team.players.filter(age__lt=min_age).count()
        violation_fields = {'under_age_players': players_under_age}

        if players_under_age > player_count_limit:
            message = "%s can only have %s players under %s. (it has %s)" % (self.team, player_count_limit, min_age, players_under_age)
            return self.create_violation(self.team.pk, message, violation_fields)


@site.register
class RangeOfAveragePlayerAge(BaseDynamicValidation):
    key = "RangeOfAveragePlayerAge"
    display_name = "the average age of all players on a team must be within an allowed range."
    trigger_model_name = 'team'

    fields = {
        'min_age': forms.IntegerField(help_text="Minimum average age allowed."),
        'max_age': forms.IntegerField(help_text="Maximum average age allowed."),
    }

    def get_current_violations(self, *args, **kwargs):
        min_age = self.rule_model.dynamic_fields['min_age']
        max_age = self.rule_model.dynamic_fields['max_age']

        average_player_age = self.team.players.all().aggregate(Avg('age'))['age__avg']

        violation_fields = dict(average_player_age=average_player_age)
        if not min_age <= average_player_age <= max_age:
            message = "Average player age %s needs to between %s and %s." % (average_player_age, min_age, max_age)
            return self.create_violation(self.team.pk, message, violation_fields)
