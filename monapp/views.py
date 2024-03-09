 # monapp/views.py

from django.shortcuts import render
from django.template.loader import render_to_string
from .forms import SeasonSearchForm
from .models import Match
from django.db.models import F, Q, Sum, Count, Value
from django.db.models.functions import Coalesce
import time

def season_search(request):
    form = SeasonSearchForm(request.GET or None)
    context = {'form': form}
    if form.is_valid():
        start_time = time.time()  # Début du comptage du temps
        season = form.cleaned_data['season']
        matches = Match.objects.filter(season=season)
        num_victories = form.cleaned_data['num_victories']
        num_defeats = form.cleaned_data['num_defeats']
        num_goals = form.cleaned_data['num_goals']
        num_ranking = form.cleaned_data['num_ranking']

        # Calcul des buts totaux, à domicile et à l'extérieur
        total_matches_played = matches.count()
        total_goals = matches.aggregate(total=Coalesce(Sum(F('hometeamgoals') + F('awayteamgoals')), Value(0)))['total']
        home_goals = matches.aggregate(total=Coalesce(Sum('hometeamgoals'), Value(0)))['total']
        away_goals = matches.aggregate(total=Coalesce(Sum('awayteamgoals'), Value(0)))['total']

        # Calcul des taux de victoire à domicile et à l'extérieur
        home_wins = matches.filter(winner=F('hometeam')).count()
        away_wins = matches.filter(winner=F('awayteam')).count()
        total_matches = matches.count()
        home_win_rate = round((home_wins / total_matches) * 100, 2) if total_matches else 0
        away_win_rate = round((away_wins / total_matches) * 100, 2) if total_matches else 0
        

        # Calcul des équipes avec le plus de victoires et le plus de défaites
        team_wins = matches.exclude(winner='Draw').values('winner').annotate(wins=Count('winner')).order_by('-wins')[:num_victories]
        team_losses = (matches.exclude(Q(winner='Draw') | Q(loser='Draw')).values('loser').annotate(losses=Count('loser')).order_by('-losses'))[:num_defeats]

        # Calcul pour les buts marqués pour chaque équipe, combiner les buts à domicile et à l'extérieur
        # Calcul pour les buts marqués pour chaque équipe (à domicile et à l'extérieur combinés)
        home_goals_1 = matches.values('hometeam').annotate(total_goals=Coalesce(Sum('hometeamgoals'), Value(0))).order_by()
        away_goals_1 = matches.values('awayteam').annotate(total_goals=Coalesce(Sum('awayteamgoals'), Value(0))).order_by()

        # Création d'un dictionnaire pour cumuler les totaux
        team_goals_dict = {}
        for entry in home_goals_1:
            team = entry['hometeam']
            goals = entry['total_goals']
            if team in team_goals_dict:
                team_goals_dict[team] += goals
            else:
                team_goals_dict[team] = goals

        for entry in away_goals_1:
            team = entry['awayteam']
            goals = entry['total_goals']
            if team in team_goals_dict:
                team_goals_dict[team] += goals
            else:
                team_goals_dict[team] = goals

        # Conversion du dictionnaire en liste pour le tri et limitation aux 3 premiers
        team_goals_list = [{'team': k, 'total_goals': v} for k, v in team_goals_dict.items()]
        team_goals_sorted = sorted(team_goals_list, key=lambda x: x['total_goals'], reverse=True)[:num_goals]
         
      # Calcul du classement final basé sur les points
    # Utiliser l'annotation pour calculer les points pour les victoires et les nuls à domicile
        home_points = matches.values('hometeam').annotate(
        wins=Count('winner', filter=Q(winner=F('hometeam'))),
        draws=Count('winner', filter=Q(winner='Draw')),
        ).annotate(points=F('wins')*3 + F('draws'))

    # Utiliser l'annotation pour calculer les points pour les victoires et les nuls à l'extérieur
        away_points = matches.values('awayteam').annotate(
        wins=Count('winner', filter=Q(winner=F('awayteam'))),
        draws=Count('winner', filter=Q(winner='Draw')),
        ).annotate(points=F('wins')*3 + F('draws'))

    # Fusionner les points à domicile et à l'extérieur dans un seul dictionnaire
        points_dict = {}
        for entry in home_points:
            team = entry['hometeam']
            points = entry['points']
            points_dict[team] = points_dict.get(team, 0) + points

        for entry in away_points:
            team = entry['awayteam']
            points = entry['points']
            points_dict[team] = points_dict.get(team, 0) + points

    # Trier les équipes par points pour obtenir le classement final
        final_standings = sorted(
        [{'team': k, 'points': v} for k, v in points_dict.items()],
        key=lambda x: x['points'],
        reverse=True    )[:num_ranking]

        end_time = time.time()  
        execution_time = round(end_time - start_time ,2) 


        context.update({
            'total_goals': total_goals,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_win_rate': home_win_rate,
            'away_win_rate': away_win_rate,
            'team_wins': team_wins,
            'team_losses': team_losses,
            'team_goals':  team_goals_sorted,
            'total_matches_played': total_matches_played,
            'final_standings': final_standings,
            'execution_time': execution_time,
        })

    return render(request, 'monapp/season_search.html', context)

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import MatchForm

def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect(reverse('season_search'))  
    else:
        form = MatchForm()
    return render(request, 'monapp/ajout_match.html', {'form': form})



################################################################################################################################
# views.py
from django.shortcuts import render
from .forms import SeasonSelectForm, MatchSelectForm
from .models import Match

def match_view(request):
    season_form = SeasonSelectForm(request.GET or None)
    match_form = MatchSelectForm(season=request.GET.get('season'), data=request.GET or None)

    context = {
        'season_form': season_form,
        'match_form': match_form,
        'match': None
    }

    if season_form.is_valid() and match_form.is_valid():
        home_team = match_form.cleaned_data.get('home_team')
        away_team = match_form.cleaned_data.get('away_team')
        season = season_form.cleaned_data.get('season')
        try:
            match = Match.objects.get(season=season, hometeam=home_team, awayteam=away_team)
            context['match'] = match
        except Match.DoesNotExist:
            context['error'] = "Aucun match trouvé pour les critères donnés."

    return render(request, 'monapp/search_match.html', context)

# views.py
import csv
from django.http import HttpResponse
from .models import Match
from .forms import SeasonSelectForm

def export_season_csv(request):
    if request.method == "POST":
        form = SeasonSelectForm(request.POST)
        if form.is_valid():
            season = form.cleaned_data['season']
            matches = Match.objects.filter(season=season)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="matches_{season}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Season', 'Home Team', 'Away Team', 'Home Team Goals', 'Away Team Goals', 'Winner', 'Loser'])
            for match in matches:
                writer.writerow([match.season, match.hometeam, match.awayteam, match.hometeamgoals, match.awayteamgoals, match.winner, match.loser])
            
            return response
    else:
        form = SeasonSelectForm()
    return render(request, 'monapp/export_season.html', {'form': form})


# views.py
# views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CSVImportForm
from .models import Match
import csv
from django.contrib import messages
from django.http import HttpResponseRedirect

def import_season_csv(request):
    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                Match.objects.create(
                    season=row['Season'],
                    hometeam=row['HomeTeam'],
                    awayteam=row['AwayTeam'],
                    hometeamgoals=row['HomeTeamGoals'],
                    awayteamgoals=row['AwayTeamGoals'],
                    winner=row['Winner'],
                    loser=row['Loser']
                )
            messages.success(request, "Les données ont été importées avec succès !")
            return HttpResponseRedirect(request.path_info)
    else:
        form = CSVImportForm()
    return render(request, 'monapp/import_season.html', {'form': form})


#####

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Match
from .forms import SeasonSelectForm
from django.http import HttpResponseRedirect


def delete_season(request):
    if request.method == 'POST':
        form = SeasonSelectForm(request.POST)
        if form.is_valid():
            season = form.cleaned_data['season']
            # Suppression des matchs de la saison sélectionnée
            Match.objects.filter(season=season).delete()
            messages.success(request, f'La saison {season} a été supprimée avec succès.')
            return HttpResponseRedirect(request.path_info)
    else:
        form = SeasonSelectForm()

    return render(request, 'monapp/delete_season.html', {'form': form})





