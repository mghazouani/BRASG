from django.contrib import admin
from .models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser, ScrapProduct

# Register your models here.

@admin.register(ScrapDimagazBC)
class ScrapDimagazBCAdmin(admin.ModelAdmin):
    list_display = (
        'odoo_id', 'name', 'fullname', 'bc_date', 'bl_date',
        'fournisseur', 'fournisseur_centre', 'depositaire',
        'montant_paye', 'done', 'sap', 'confirmed', 'remise', 'tva', 'ht', 'ttc',
        'bc_type', 'state', 'terminated', 'verify_state', 'qty_retenue', 'paye_par',
        'bl_number', 'solde', 'non_conforme', 'version', 'prefix', 'source', 'product_type',
        'display_name', 'create_date', 'write_date'
    )
    search_fields = ('odoo_id', 'name', 'fullname', 'display_name')
    list_filter = ('fournisseur', 'fournisseur_centre', 'depositaire', 'done', 'sap', 'confirmed', 'state', 'terminated', 'non_conforme', 'product_type')

@admin.register(ScrapDimagazBCLine)
class ScrapDimagazBCLineAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'bc', 'product', 'product_name', 'qty', 'bc_date')
    search_fields = ('odoo_id', 'product_name', 'product__name')
    list_filter = ('product__name',)

@admin.register(ScrapFournisseur)
class ScrapFournisseurAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'name')

@admin.register(ScrapFournisseurCentre)
class ScrapFournisseurCentreAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'fournisseur', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'name', 'fournisseur__name')

@admin.register(ScrapUser)
class ScrapUserAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'display_name', 'username', 'sap_id', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'display_name', 'username', 'sap_id')

@admin.register(ScrapProduct)
class ScrapProductAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'product_id', 'product_id_name', 'product_category', 'product_category_name', 'prix', 'product_type', 'display_name', 'create_date', 'write_date')
    search_fields = ('name', 'display_name', 'product_id_name', 'product_category_name')
    list_filter = ('product_type', 'product_category_name')
