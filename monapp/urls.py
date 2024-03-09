# monapp/urls.py

from django.urls import path
from . import views

app_name = 'monapp'

urlpatterns = [
    path('season-search/', views.season_search, name='season_search'),
    path('ajout-match/', views.add_match, name='ajout_match'),
    path('search-match/', views.match_view, name='search_match'),
    path('export-season/', views.export_season_csv, name='export_season'),
    path('import-season/', views.import_season_csv, name='import_season'),
    path('delete-season/', views.delete_season, name='delete_season'),
   
    
    
]




