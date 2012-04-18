from django.db import models


class League(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=20)
    league = models.ForeignKey('League', related_name='teams')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.league)


class Player(models.Model):
    name = models.CharField(max_length=20)
    team = models.ForeignKey('Team', related_name='players')
    age = models.SmallIntegerField()
    gender = models.SmallIntegerField(choices=((1, 'Male'), (2, 'Female')))

    def __unicode__(self):
        return self.name
