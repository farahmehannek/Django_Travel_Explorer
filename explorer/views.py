from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
import requests

from .models import Attraction, Profil, Compilation

API_KEY = "74EFAB1B966A4D4A9395B60B24FB1ABA"


# ----------------------------
# 🛬 PAGE 1 : Atterrissage
# ----------------------------
def atterrissage_view(request):
    profils = Profil.objects.all()
    if request.method == "POST":
        profil_nom = request.POST.get("profil")
        pays_nom = request.POST.get("pays")
        request.session["profil_nom"] = profil_nom
        request.session["pays_nom"] = pays_nom
        return redirect("accueil")
    return render(request, "explorer/atterrissage.html", {"profils": profils})


# ----------------------------
# 🏠 PAGE 2 : Accueil
# ----------------------------
def accueil_view(request):
    profil_nom = request.session.get("profil_nom")
    pays_nom = request.session.get("pays_nom")

    if not profil_nom or not pays_nom:
        return redirect("atterrissage")

    top_attractions = Attraction.objects.filter(
        pays__nom__iexact=pays_nom
    ).order_by("-likes")[:10]

    profil = Profil.objects.filter(nom=profil_nom).first()
    compilation = Compilation.objects.filter(profil=profil).first()
    selected_attractions = compilation.attractions.all() if compilation else []

    return render(
        request,
        "explorer/accueil.html",
        {
            "top_attractions": top_attractions,
            "selected_attractions": selected_attractions,
            "profil": profil_nom,
            "pays": pays_nom,
        },
    )


# ----------------------------
# 🔍 PAGE 3 : Recherche
# ----------------------------
def recherche_view(request):
    profil_nom = request.session.get("profil_nom")
    pays_nom = request.session.get("pays_nom")

    if not profil_nom or not pays_nom:
        return redirect("atterrissage")

    if not Attraction.objects.filter(pays__nom=pays_nom, profil__nom=profil_nom).exists():
        importer_attractions_tripadvisor(pays_nom, profil_nom)

    attractions = Attraction.objects.filter(profil__nom=profil_nom, pays__nom=pays_nom)
    capitale = "Paris" if pays_nom.lower() == "france" else "Tokyo"

    # --- Filtres ---
    ville = request.GET.get("ville")
    categorie = request.GET.get("categorie")
    note_min = request.GET.get("note_min")
    prix_max = request.GET.get("prix_max")
    reviews_min = request.GET.get("reviews_min")
    photos_min = request.GET.get("photos_min")

    if ville:
        attractions = attractions.filter(ville__icontains=ville)
    elif attractions.filter(ville__iexact=capitale).exists():
        attractions = attractions.filter(ville__iexact=capitale)

    if categorie and categorie != "Toutes":
        attractions = attractions.filter(categorie__icontains=categorie)
    if note_min:
        attractions = attractions.filter(note__gte=note_min)
    if prix_max:
        attractions = attractions.filter(prix__lte=prix_max)
    if reviews_min:
        attractions = attractions.filter(nb_reviews__gte=reviews_min)
    if photos_min:
        attractions = attractions.filter(nb_photos__gte=photos_min)

    # --- Pagination ---
    paginator = Paginator(attractions, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- Liste des villes uniques ---
    raw_villes = Attraction.objects.filter(pays__nom=pays_nom).values_list("ville", flat=True)
    villes = sorted(set(v.strip().title() for v in raw_villes if v and v.strip()))

    # --- Liste des catégories uniques et nettoyées ---
    raw_categories = Attraction.objects.filter(pays__nom=pays_nom).values_list("categorie", flat=True)
    categories_set = set()
    for c in raw_categories:
        if c:
            c = str(c).replace(";", ",").replace("/", ",")
            parts = [p.strip().capitalize() for p in c.split(",") if p.strip()]
            categories_set.update(parts)
    categories = sorted(categories_set)

    return render(
        request,
        "explorer/recherche.html",
        {
            "page_obj": page_obj,
            "villes": villes,
            "categories": categories,
            "profil": profil_nom,
            "pays": pays_nom,
            "capitale": capitale,
        },
    )

    profil_nom = request.session.get("profil_nom")
    pays_nom = request.session.get("pays_nom")

    if not profil_nom or not pays_nom:
        return redirect("atterrissage")

    # Charger les attractions si la base est vide pour ce pays + profil
    if not Attraction.objects.filter(pays__nom=pays_nom, profil__nom=profil_nom).exists():
        importer_attractions_tripadvisor(pays_nom, profil_nom)

    attractions = Attraction.objects.filter(profil__nom=profil_nom, pays__nom=pays_nom)
    capitale = "Paris" if pays_nom.lower() == "france" else "Tokyo"

    # -------------------------
    # 🔍 Filtres de recherche
    # -------------------------
    ville = request.GET.get("ville")
    categorie = request.GET.get("categorie")
    note_min = request.GET.get("note_min")
    prix_max = request.GET.get("prix_max")
    reviews_min = request.GET.get("reviews_min")
    photos_min = request.GET.get("photos_min")

    if ville:
        attractions = attractions.filter(ville__icontains=ville)
    elif attractions.filter(ville__iexact=capitale).exists():
        attractions = attractions.filter(ville__iexact=capitale)

    if categorie and categorie != "Toutes":
        attractions = attractions.filter(categorie__icontains=categorie)
    if note_min:
        attractions = attractions.filter(note__gte=note_min)
    if prix_max:
        attractions = attractions.filter(prix__lte=prix_max)
    if reviews_min:
        attractions = attractions.filter(nb_reviews__gte=reviews_min)
    if photos_min:
        attractions = attractions.filter(nb_photos__gte=photos_min)

    # -------------------------
    # 📄 Pagination
    # -------------------------
    paginator = Paginator(attractions, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # -------------------------
    # 🏙️ Liste des villes sans doublons (nettoyées et unifiées)
    # -------------------------
    raw_villes = (
        Attraction.objects.filter(pays__nom=pays_nom, profil__nom=profil_nom)
        .values_list("ville", flat=True)
    )
    villes_set = {v.strip().title() for v in raw_villes if v and v.strip()}
    villes = sorted(villes_set)

    # -------------------------
    # 🧭 Liste des catégories sans doublons et bien séparées
    # -------------------------
    raw_categories = (
        Attraction.objects.filter(pays__nom=pays_nom, profil__nom=profil_nom)
        .values_list("categorie", flat=True)
    )

    categories_set = set()
    for c in raw_categories:
        if c:
            # Remplace les séparateurs incohérents et supprime les espaces parasites
            c = str(c).replace(";", ",").replace("/", ",")
            parts = [p.strip().capitalize() for p in c.split(",") if p.strip()]
            categories_set.update(parts)

    # Tri alphabétique pour affichage
    categories = sorted(categories_set)

    # -------------------------
    # 🖼️ Rendu du template
    # -------------------------
    return render(
        request,
        "explorer/recherche.html",
        {
            "page_obj": page_obj,
            "villes": villes,
            "categories": categories,
            "profil": profil_nom,
            "pays": pays_nom,
            "capitale": capitale,
        },
    )


# ----------------------------
# 📍 PAGE 4 : Détail attraction
# ----------------------------
def attraction_view(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    suggestions = Attraction.objects.filter(ville=attraction.ville).exclude(id=attraction.id)[:5]
    return render(request, "explorer/attraction.html", {"a": attraction, "suggestions": suggestions})


# ----------------------------
# 📋 PAGE 5 : Compilation
# ----------------------------
import math

def haversine(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points GPS."""
    R = 6371  # Rayon de la Terre (km)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def itineraire_court(attractions):
    """Retourne une liste d’attractions dans l’ordre le plus court (greedy)."""
    if not attractions:
        return []

    non_visitees = list(attractions)
    itineraire = [non_visitees.pop(0)]  # on part de la première

    while non_visitees:
        derniere = itineraire[-1]
        if not derniere.coordonnees_gps:
            break

        lat1, lon1 = map(float, derniere.coordonnees_gps.split(","))

        # Cherche la plus proche attraction restante
        plus_proche = min(
            non_visitees,
            key=lambda a: haversine(lat1, lon1, *map(float, a.coordonnees_gps.split(","))) if a.coordonnees_gps else float("inf")
        )
        itineraire.append(plus_proche)
        non_visitees.remove(plus_proche)

    return itineraire


def compilation_view(request):
    profil_nom = request.session.get("profil_nom")
    profil = get_object_or_404(Profil, nom=profil_nom)
    compilation, _ = Compilation.objects.get_or_create(profil=profil)

    tri = request.GET.get("tri", "prix_asc")

    # Tri par prix ou par distance
    if tri == "prix_desc":
        attractions = compilation.attractions.all().order_by("-prix")
    elif tri == "distance":
        attractions = list(itineraire_court(list(compilation.attractions.all())))
    else:
        attractions = compilation.attractions.all().order_by("prix")

    total_budget = sum(a.prix for a in compilation.attractions.all())

    return render(
        request,
        "explorer/compilation.html",
        {
            "compilation": compilation,
            "attractions": attractions,
            "total_budget": total_budget,
            "tri": tri,
        },
    )

    profil_nom = request.session.get("profil_nom")
    profil = get_object_or_404(Profil, nom=profil_nom)
    compilation, _ = Compilation.objects.get_or_create(profil=profil)

    tri = request.GET.get("tri", "prix_asc")

    if tri == "prix_desc":
        attractions = compilation.attractions.all().order_by("-prix")
    else:
        attractions = compilation.attractions.all().order_by("prix")

    total_budget = sum(a.prix for a in compilation.attractions.all())

    return render(
        request,
        "explorer/compilation.html",
        {
            "compilation": compilation,
            "attractions": attractions,
            "total_budget": total_budget,
            "tri": tri,
        },
    )

    profil_nom = request.session.get("profil_nom")
    profil = get_object_or_404(Profil, nom=profil_nom)
    compilation, _ = Compilation.objects.get_or_create(profil=profil)
    total_budget = sum(a.prix for a in compilation.attractions.all())
    attractions = compilation.attractions.all().order_by("prix")

    return render(
        request,
        "explorer/compilation.html",
        {"compilation": compilation, "attractions": attractions, "total_budget": total_budget},
    )


# ----------------------------
# ➕ / ❌ Compilation actions
# ----------------------------
def add_to_compilation(request, id):
    profil_nom = request.session.get("profil_nom")
    profil = get_object_or_404(Profil, nom=profil_nom)
    attraction = get_object_or_404(Attraction, id=id)
    compilation, _ = Compilation.objects.get_or_create(profil=profil)
    compilation.attractions.add(attraction)
    messages.success(request, f"{attraction.nom} ajouté à votre compilation.")
    return redirect("recherche")


def remove_from_compilation(request, id):
    profil_nom = request.session.get("profil_nom")
    profil = get_object_or_404(Profil, nom=profil_nom)
    compilation = get_object_or_404(Compilation, profil=profil)
    attraction = get_object_or_404(Attraction, id=id)
    compilation.attractions.remove(attraction)
    messages.warning(request, f"{attraction.nom} supprimé de votre compilation.")
    return redirect("compilation")


# ----------------------------
# 🌍 Autocomplete API TripAdvisor
# ----------------------------
def autocomplete_location(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse([], safe=False)

    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    params = {"key": API_KEY, "searchQuery": query, "language": "fr", "category": "geos", "limit": 10}

    try:
        response = requests.get(url, params=params, timeout=4)
        if response.status_code == 200:
            data = response.json().get("data", [])
            results = []
            for d in data:
                name = d.get("name")
                type_ = d.get("result_type", "").lower()
                if name and any(k in type_ for k in ["geo", "country", "city", "region"]):
                    results.append(name)
            if results:
                return JsonResponse(sorted(set(results)), safe=False)
    except Exception:
        pass

    fallback = ["France", "Japon", "Espagne", "Italie", "États-Unis", "Canada", "Royaume-Uni", "Brésil"]
    filtered = [p for p in fallback if query.lower() in p.lower()]
    return JsonResponse(filtered, safe=False)


# ----------------------------
# 🔒 Déconnexion
# ----------------------------
def logout_view(request):
    request.session.flush()
    messages.info(request, "Session réinitialisée. Sélectionnez un nouveau profil.")
    return redirect("atterrissage")


# ----------------------------
# ⚙️ Service : Importation TripAdvisor
# ----------------------------
def importer_attractions_tripadvisor(pays_nom, profil_nom):
    print(f"📡 Importation des attractions TripAdvisor pour {pays_nom} ({profil_nom})...")

    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    params = {
        "key": API_KEY,
        "searchQuery": pays_nom,
        "language": "fr",
        "category": "attractions",
        "limit": 50,
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for d in data:
                name = d.get("name")
                adresse = d.get("address_obj", {}).get("city", "")
                image = d.get("photo", {}).get("images", {}).get("large", {}).get("url", "")
                note = float(d.get("rating", 0))
                reviews = d.get("num_reviews", 0)
                latitude = d.get("latitude")
                longitude = d.get("longitude")
                coordonnees = f"{latitude},{longitude}" if latitude and longitude else None
                description = d.get("description") or "Aucune description disponible"

                Attraction.objects.get_or_create(
                    nom=name,
                    defaults={
                        "ville": (adresse or "Inconnue").strip().title(),
                        "categorie": (
                            d.get("subcategory", ["Attraction"])[0].strip().capitalize()
                            if d.get("subcategory") else "Attraction"
                        ),
                        "note": note,
                        "nb_reviews": reviews,
                        "prix": d.get("price_level") or 0,
                        "image": image,
                        "coordonnees_gps": coordonnees,
                        "description": description,
                        "pays_id": pays_nom,
                        "profil_id": profil_nom,
                    },
                )
            print(f"✅ Importation terminée ({len(data)} attractions).")
        else:
            print(f"⚠️ Erreur API TripAdvisor : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de l’importation TripAdvisor : {e}")
