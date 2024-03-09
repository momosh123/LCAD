# Dans votre fichier monprojet/urls.py

from django.contrib import admin
from django.urls import include, path
from monapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('monapp/', include('monapp.urls')),
   # path('add-match/', views.add_match, name='add_match'),

    # Assurez-vous que le chemin 'monapp/' correspond à ce que vous utilisez dans le navigateur
]
