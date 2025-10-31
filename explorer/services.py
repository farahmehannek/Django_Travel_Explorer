import random
import time
import requests
from .models import Attraction, Pays, Profil

# --- Clé API TripAdvisor ---
API_KEY = "74EFAB1B966A4D4A9395B60B24FB1ABA"
BASE_URL = "https://api.content.tripadvisor.com/api/v1/location"


# =============================================================
# 🔹 Étape 1 : Requête API TripAdvisor pour un pays / une ville
# =============================================================
def get_attractions_by_country(search_query, limit=10):
    """
    Étape 1 : Récupère les attractions d’un pays ou d’une ville via l’API TripAdvisor.
    Étape 2 : Pour chaque attraction, récupère les détails complets, horaires, coordonnées, photos, etc.
    """

    print(f"🔎 Recherche d'attractions pour : {search_query}")

    search_url = f"{BASE_URL}/search"
    params = {
        "key": API_KEY,
        "searchQuery": search_query,
        "language": "fr",
        "category": "attractions",
        "limit": limit
    }

    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"❌ Erreur API (search): {response.status_code} -> {response.text}")
        return []

    data = response.json().get("data", [])
    attractions = []

    for item in data:
        location_id = item.get("location_id")
        if not location_id:
            continue

        # --- Récupération des détails complets ---
        detail_url = f"{BASE_URL}/{location_id}/details"
        detail_params = {"key": API_KEY, "language": "fr"}
        detail_response = requests.get(detail_url, params=detail_params)

        if detail_response.status_code != 200:
            continue

        details = detail_response.json()

        # --- Photo principale ---
        image_url = None
        photos_url = f"{BASE_URL}/{location_id}/photos"
        photos_params = {"key": API_KEY, "language": "fr", "limit": 5}
        photos_response = requests.get(photos_url, params=photos_params)

        nb_photos = 0
        if photos_response.status_code == 200:
            photos_data = photos_response.json().get("data", [])
            nb_photos = len(photos_data)
            if photos_data:
                image_url = photos_data[0]["images"]["large"]["url"]

        # --- Catégories ---
        categorie = "Inconnue"
        if details.get("subcategory"):
            subcats = details["subcategory"]
            if isinstance(subcats, list):
                categorie = ", ".join(
                    [cat.get("localized_name", cat.get("name", "")) for cat in subcats]
                )

        # --- Coordonnées de contact ---
        coordonnees_contact = details.get("phone", "")
        if details.get("email"):
            coordonnees_contact += f" | {details['email']}"

        # --- Horaires d’ouverture ---
        horaires = details.get("hours", {}).get("week_ranges")
        if isinstance(horaires, list) and horaires:
            horaires = str(horaires[0])
        else:
            horaires = "Non spécifiés"

        # --- Récompenses (Awards) ---
        awards_data = details.get("awards", [])
        awards_text = ", ".join([a.get("display_name", "") for a in awards_data]) if awards_data else "Aucune"

        # --- Type d’attraction ---
        type_obj = "attraction"
        if "restaurant" in details.get("name", "").lower():
            type_obj = "restaurant"
        elif "hôtel" in details.get("name", "").lower():
            type_obj = "hotel"

        # --- Construction du dictionnaire ---
        attraction = {
            "name": details.get("name", "Attraction sans nom"),
            "description": details.get("description", "Aucune description disponible."),
            "subcategory": categorie,
            "rating": float(details.get("rating", 0) or 0),
            "num_reviews": int(details.get("num_reviews", 0) or 0),
            "latitude": details.get("latitude"),
            "longitude": details.get("longitude"),
            "address_obj": details.get("address_obj", {}),
            "photo_url": image_url,
            "web_url": details.get("web_url"),
            "phone": coordonnees_contact,
            "hours": horaires,
            "nb_photos": nb_photos,
            "awards": awards_text,
            "type": type_obj,
        }

        attractions.append(attraction)

        # ⚙️ Pause pour respecter le quota de l’API
        time.sleep(0.4)

        if len(attractions) >= limit:
            break

    print(f"✅ {len(attractions)} attractions détaillées récupérées pour {search_query}")
    return attractions


# =============================================================
# 🔹 Étape 2 : Importation dans la base Django
# =============================================================
def importer_attractions_tripadvisor(search_query="France", profil_nom=None):
    """
    Importe les attractions depuis l'API TripAdvisor et les enregistre dans la base de données Django.
    Remplit tous les champs utiles (description, horaires, coordonnées, photos, awards, etc.)
    """

    print(f"🚀 Importation des attractions pour : {search_query}")

    # Récupération des données depuis l’API TripAdvisor
    data = get_attractions_by_country(search_query, limit=15)
    if not data:
        print("⚠️ Aucune attraction reçue depuis TripAdvisor.")
        return

    # Vérifie ou crée le profil
    profil_obj, _ = Profil.objects.get_or_create(nom=profil_nom or "Visiteur")

    # Vérifie ou crée le pays
    pays_obj, _ = Pays.objects.get_or_create(
        nom=search_query,
        defaults={"code_iso": "N/A", "capitale": search_query}
    )

    # Enregistrement en base
    for item in data:
        ville = item.get("address_obj", {}).get("city", search_query)
        coordonnees_gps = (
            f"{item.get('latitude', '0')},{item.get('longitude', '0')}"
            if item.get("latitude") and item.get("longitude")
            else ""
        )

        Attraction.objects.update_or_create(
            nom=item.get("name", "Attraction sans nom"),
            profil=profil_obj,
            defaults={
                "description": item.get("description"),
                "categorie": item.get("subcategory", "Inconnue"),
                "ville": ville,
                "coordonnees_gps": coordonnees_gps,
                "coordonnees_contact": item.get("phone", ""),
                "horaires": item.get("hours", "Non spécifiés"),
                "prix": round(random.uniform(5, 100), 2),
                "note": item.get("rating", 0.0),
                "nb_reviews": item.get("num_reviews", 0),
                "nb_photos": item.get("nb_photos", 0),
                "likes": random.randint(10, 300),
                "awards": item.get("awards", ""),
                "type": item.get("type", "attraction"),
                "image": item.get("photo_url"),
                "tripadvisor_url": item.get("web_url"),
                "pays": pays_obj,
            },
        )

    print(f"✅ Importation terminée : {len(data)} attractions enregistrées pour {search_query}")
