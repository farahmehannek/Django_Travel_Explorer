import requests
import time

API_KEY = "74EFAB1B966A4D4A9395B60B24FB1ABA"
BASE_URL = "https://api.content.tripadvisor.com/api/v1/location"


def get_attractions_by_country(search_query, limit=10):
    """
    Étape 1 : Recherche des attractions d’un pays ou d’une ville.
    Étape 2 : Récupération des détails, photos, coordonnées, horaires, awards, etc.
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

        # --- Détails complets ---
        detail_url = f"{BASE_URL}/{location_id}/details"
        detail_params = {"key": API_KEY, "language": "fr"}
        detail_response = requests.get(detail_url, params=detail_params)

        if detail_response.status_code != 200:
            continue

        details = detail_response.json()

        # --- Photos ---
        photos_url = f"{BASE_URL}/{location_id}/photos"
        photos_params = {"key": API_KEY, "language": "fr", "limit": 5}
        photos_response = requests.get(photos_url, params=photos_params)
        image_url = None
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
            else:
                categorie = str(subcats)

        # --- Contact (téléphone + email) ---
        contact = details.get("phone", "")
        if details.get("email"):
            contact += f" | {details['email']}"

        # --- Horaires d’ouverture ---
        horaires = "Non spécifiés"
        if "hours" in details and details["hours"].get("week_ranges"):
            horaires = str(details["hours"]["week_ranges"][0])

        # --- Récompenses ---
        awards = "Aucune"
        if details.get("awards"):
            awards = ", ".join([a.get("display_name", "") for a in details["awards"]])

        # --- Type (restaurant, hôtel, attraction, etc.) ---
        type_obj = "attraction"
        name_lower = details.get("name", "").lower()
        if "hotel" in name_lower or "hôtel" in name_lower:
            type_obj = "hotel"
        elif "restaurant" in name_lower:
            type_obj = "restaurant"

        # --- Nettoyage général ---
        description = details.get("description", "").strip() or "Aucune description disponible."
        ville = details.get("address_obj", {}).get("city", search_query)

        # --- Regroupement de l’attraction ---
        attraction = {
            "name": details.get("name", "Attraction sans nom"),
            "description": description,
            "subcategory": categorie,
            "rating": float(details.get("rating", 0)),
            "num_reviews": int(details.get("num_reviews", 0)),
            "latitude": details.get("latitude"),
            "longitude": details.get("longitude"),
            "address_obj": details.get("address_obj", {}),
            "photo_url": image_url,
            "web_url": details.get("web_url"),
            "nb_photos": nb_photos,
            "awards": awards,
            "phone": contact,
            "hours": horaires,
            "type": type_obj,
        }

        attractions.append(attraction)

        # Pause API pour éviter le blocage de TripAdvisor
        time.sleep(0.4)
        if len(attractions) >= limit:
            break

    print(f"✅ {len(attractions)} attractions détaillées récupérées pour {search_query}")
    return attractions
