from django.contrib import admin
from .models import Profil, Pays, Attraction

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)

@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'code_iso', 'capitale')
    search_fields = ('nom', 'code_iso', 'capitale')

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'ville', 'categorie', 'prix', 'note', 'profil', 'pays')
    list_filter = ('ville', 'categorie', 'pays', 'profil')
    search_fields = ('nom', 'ville', 'categorie')
