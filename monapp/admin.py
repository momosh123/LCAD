from django.contrib import admin
from .models import Match

# Option simple
admin.site.register(Match)

# Option avancée avec personnalisation
class MatchAdmin(admin.ModelAdmin):
    list_display = ('season', 'hometeam', 'awayteam', 'hometeamgoals', 'awayteamgoals', 'score', 'winner', 'loser')
    search_fields = ('season', 'hometeam', 'awayteam', 'winner', 'loser')
    list_filter = ('season', 'winner', 'loser')

# Décommentez la ligne suivante pour utiliser la personnalisation
# admin.site.register(Match, MatchAdmin)
