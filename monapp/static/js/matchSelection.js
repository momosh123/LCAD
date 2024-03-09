$(document).ready(function () {
    // Lorsque l'utilisateur clique sur le bouton pour afficher les équipes
    $('#showTeams').click(function () {
        var url = "/monapp/update-teams/"; // Assurez-vous que cette URL est correcte
        var seasonId = $('#id_season').val(); // Récupère la saison sélectionnée

        if (!seasonId) {
            alert("Veuillez sélectionner une saison.");
            return;
        }

        // Appel AJAX pour récupérer les équipes basées sur la saison choisie
        $.ajax({
            url: url,
            data: { 'season': seasonId },
            success: function (data) {
                $("#id_home_team").html(data.home_teams);
                $("#id_away_team").html(data.away_teams);
                $("#teamsSection").show(); // Affiche les sélecteurs d'équipes
            }
        });
    });

    // Lorsque l'utilisateur clique sur le bouton pour afficher les résultats des matchs
    $('#resultButton').click(function() {
        var season = $('#id_season').val();
        var homeTeam = $('#id_home_team').val();
        var awayTeam = $('#id_away_team').val();

        $.ajax({
            url: '/monapp/match-results/', // Assurez-vous que cette URL mène à votre vue Django
            type: 'GET',
            data: {
                'season': season,
                'home_team': homeTeam,
                'away_team': awayTeam
            },
            success: function(response) {
                // Mettez à jour le contenu de '#matchResults' avec les données reçues
                $('#match-results').html(response).show();
            },
            error: function(xhr, status, error) {
                console.error("Erreur lors de la récupération des résultats.");
            }
        });
    });

    // Cache initialement la section des résultats
    $("#teamsSection").hide();
    $("#match-results").hide();
});
