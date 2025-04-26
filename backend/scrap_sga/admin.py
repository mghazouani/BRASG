from django.contrib import admin
from .models import ScrapDimagazBC, ScrapDimagazBCLine

# Register your models here.

@admin.register(ScrapDimagazBC)
class ScrapDimagazBCAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'depositaire_name', 'date_bc')
    search_fields = ('odoo_id', 'name', 'depositaire_name')
    list_filter = ('depositaire_name',)

@admin.register(ScrapDimagazBCLine)
class ScrapDimagazBCLineAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'bc', 'product_name', 'qty')
    search_fields = ('odoo_id', 'product_name')
    list_filter = ('product_name',)
