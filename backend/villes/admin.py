from django.contrib import admin
from core.models import Ville

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'pays', 'region', 'latitude', 'longitude', 'iso2')
    search_fields = ('nom', 'region', 'pays', 'iso2')
    list_filter = ('pays', 'region')
