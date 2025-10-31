from django.db.models import Q
from .models import Attraction

def filtrer_attractions(request, queryset=None):
    """
    Applique les filtres envoyés via GET (catégorie, note, prix...).
    """
    if queryset is None:
        queryset = Attraction.objects.all()

    categorie = request.GET.get("categorie")
    note_min = request.GET.get("note_min")
    prix_max = request.GET.get("prix_max")
    ville = request.GET.get("ville")

    # Filtre par catégorie
    if categorie:
        queryset = queryset.filter(categorie__icontains=categorie)

    # Filtre par note
    if note_min:
        try:
            queryset = queryset.filter(note__gte=float(note_min))
        except ValueError:
            pass

    # Filtre par prix
    if prix_max:
        try:
            queryset = queryset.filter(prix__lte=float(prix_max))
        except ValueError:
            pass

    # Filtre par ville
    if ville:
        queryset = queryset.filter(ville__icontains=ville)

    return queryset
