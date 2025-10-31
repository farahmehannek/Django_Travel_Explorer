from django.urls import path
from . import views

urlpatterns = [
    # 🛬 Page 1 : atterrissage (choix du profil et pays)
    path("", views.atterrissage_view, name="atterrissage"),

    # 🏠 Page 2 : accueil (top attractions + carte)
    path("accueil/", views.accueil_view, name="accueil"),

    # 🔍 Page 3 : recherche / exploration
    path("recherche/", views.recherche_view, name="recherche"),

    # 📍 Page 4 : détail d'une attraction
    path("attraction/<int:attraction_id>/", views.attraction_view, name="attraction"),

    # 📋 Page 5 : compilation
    path("compilation/", views.compilation_view, name="compilation"),

    # ➕ / ❌ Ajout / Suppression
    path("add/<int:id>/", views.add_to_compilation, name="add_to_compilation"),
    path("remove/<int:id>/", views.remove_from_compilation, name="remove_from_compilation"),

    # 🌍 Autocomplete
    path("autocomplete/", views.autocomplete_location, name="autocomplete"),

    # 🔒 Déconnexion
    path("logout/", views.logout_view, name="logout_view"),
]
