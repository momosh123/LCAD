# monapp/forms.py


from django import forms
from .models import Match

class SeasonSearchForm(forms.Form):
    season = forms.ChoiceField(choices=[], required=False)
    num_victories = forms.IntegerField(label='Top équipes avec plus de victoires', initial=3, min_value=1,max_value=20, required=False)
    num_defeats = forms.IntegerField(label='Top équipes avec plus de défaites', initial=3, min_value=1,max_value=20, required=False)
    num_goals = forms.IntegerField(label='Top équipes avec plus de buts', initial=3, min_value=1,max_value=20, required=False)
    num_ranking = forms.IntegerField(label='Top du classement', initial=3, min_value=1,max_value=20, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        seasons = Match.objects.values_list('season', flat=True).distinct()
        self.fields['season'].choices = [(season, season) for season in seasons]

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['season', 'hometeam', 'awayteam', 'hometeamgoals', 'awayteamgoals']

    def save(self, commit=True):
        match = super().save(commit=False)
        
        # Calculer le score
        match.score = match.hometeamgoals + match.awayteamgoals

        # Déterminer le gagnant, le perdant ou égalité
        if match.hometeamgoals > match.awayteamgoals:
            match.winner = match.hometeam
            match.loser = match.awayteam
        elif match.hometeamgoals < match.awayteamgoals:
            match.winner = match.awayteam
            match.loser = match.hometeam
        else:
            match.winner = 'Draw'
            match.loser = 'Draw'

        if commit:
            match.save()
        return match

class SeasonSelectForm(forms.Form):
    season = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['season'].choices = [(season, season) for season in Match.objects.values_list('season', flat=True).distinct()]

class MatchSelectForm(forms.Form):
    home_team = forms.ChoiceField(choices=[], label="Home Team")
    away_team = forms.ChoiceField(choices=[], label="Away Team")

    def __init__(self, *args, **kwargs):
        season = kwargs.pop('season', None)
        super().__init__(*args, **kwargs)
        if season:
            matches = Match.objects.filter(season=season)
            self.fields['home_team'].choices = [(match.hometeam, match.hometeam) for match in matches]
            self.fields['away_team'].choices = [(match.awayteam, match.awayteam) for match in matches]



# forms.py
from django import forms

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(label='Fichier CSV')
