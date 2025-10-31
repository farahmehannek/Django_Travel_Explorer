from django.db import models


# ========================
# 👤 Profil utilisateur
# ========================
class Profil(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


# ========================
# 🌍 Pays
# ========================
class Pays(models.Model):
    nom = models.CharField(max_length=100)
    code_iso = models.CharField(max_length=5, default="N/A")
    capitale = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nom


# ========================
# 🏖️ Attraction touristique
# ========================
class Attraction(models.Model):
    TYPE_CHOICES = [
        ("attraction", "Attraction"),
        ("restaurant", "Restaurant"),
        ("hotel", "Hôtel"),
        ("autre", "Autre"),
    ]

    # --- Données principales ---
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    categorie = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="attraction")

    # --- Localisation ---
    ville = models.CharField(max_length=100, blank=True, null=True)
    coordonnees_gps = models.CharField(max_length=100, blank=True, null=True)

    # --- Contact et infos pratiques ---
    coordonnees_contact = models.CharField(max_length=255, blank=True, null=True)  # téléphone/email
    horaires = models.TextField(blank=True, null=True)
    awards = models.TextField(blank=True, null=True)  # récompenses TripAdvisor

    # --- Données numériques ---
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    note = models.FloatField(default=0.0)
    nb_reviews = models.IntegerField(default=0)
    nb_photos = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    # --- Média & lien ---
    image = models.URLField(max_length=500, null=True, blank=True)
    tripadvisor_url = models.URLField(null=True, blank=True)

    # --- Relations ---
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} ({self.ville or 'Ville inconnue'})"

    class Meta:
        verbose_name = "Attraction"
        verbose_name_plural = "Attractions"
        ordering = ["-note", "-likes"]


# ========================
# 📋 Compilation (Favoris)
# ========================
class Compilation(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    attractions = models.ManyToManyField(Attraction)
    date_creation = models.DateTimeField(auto_now_add=True)

    def budget_total(self):
        """Calcule le budget total estimé pour la compilation."""
        return sum(a.prix for a in self.attractions.all())

    def __str__(self):
        return f"Compilation de {self.profil.nom}"
