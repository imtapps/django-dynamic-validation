from django.views.generic import ListView

from dynamic_validation import models as validation_models

from sample import models as sample_models

class Index(ListView):
    template_name = 'sample/index.html'
    model = sample_models.League

    def get(self, request, *args, **kwargs):
        for league in sample_models.League.objects.all():
            league_rules = validation_models.Rule.objects.get_by_group_object(league)
            for team in league.teams.all():
                for rule in league_rules:
                    rule.run_action(team)

        return super(Index, self).get(request, *args, **kwargs)
