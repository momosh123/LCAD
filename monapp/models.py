from django.db import models

class Match(models.Model):
    season = models.CharField(max_length=7, verbose_name="Season")
    hometeam = models.CharField(max_length=100, verbose_name="Home_Team")
    awayteam = models.CharField(max_length=100, verbose_name="Away_Team")
    hometeamgoals = models.IntegerField(verbose_name="Home_Team_Goals")
    awayteamgoals = models.IntegerField(verbose_name="Away_Team_Goals")
    score = models.IntegerField(verbose_name="Score")
    winner = models.CharField(max_length=100, verbose_name="Winner")
    loser = models.CharField(max_length=100, verbose_name="Loser")

    class Meta:
        db_table = 'matches'  # Assurez-vous que cela correspond au nom réel de votre table dans la base de données

    def __str__(self):
       return f"{self.hometeam} vs {self.awayteam} - {self.season}"



