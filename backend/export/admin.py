from django import forms
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
from django.urls import path
from datetime import datetime
from .models import SalamGazTab, SalamGazTabLigne
from scrap_sga.models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapProduct, ScrapFournisseur, ScrapFournisseurCentre
from django.utils.html import format_html
from django.forms import TextInput

class GenerationLignesExportForm(forms.Form):
    date_debut = forms.DateTimeField(
        label="Date début",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"]
    )
    date_fin = forms.DateTimeField(
        label="Date fin",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"]
    )

class SalamGazTabLigneForm(forms.ModelForm):
    class Meta:
        model = SalamGazTabLigne
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'qte_bd_3kg' in self.fields:
            self.fields['qte_bd_3kg'].label = 'Qté Bt 3kg'
        if 'qte_bd_6kg' in self.fields:
            self.fields['qte_bd_6kg'].label = 'Qté Bt 6kg'
        if 'qte_bd_12kg' in self.fields:
            self.fields['qte_bd_12kg'].label = 'Qté Bt 12kg'

class SalamGazTabLigneInline(admin.TabularInline):
    model = SalamGazTabLigne
    form = SalamGazTabLigneForm
    extra = 0
    show_change_link = True
    filter_horizontal = ("source_bcs",)
    fields = (
        "client", "depositaire", "marque_bouteille", "qte_bd_3kg", "qte_bd_6kg", "qte_bd_12kg",
        "tonnage", "societe", "centre_emplisseur", "mt_bl", "mt_vers_virt", "ecart_js", "bcs_sources_display", "observation"
    )
    readonly_fields = ("tonnage", "ecart_js", "bcs_sources_display", "mt_bl")

    def bcs_sources_display(self, obj):
        bcs = obj.source_bcs.all()
        return ", ".join(f"BC {bc.name} (ASG {bc.odoo_id})" for bc in bcs)
    bcs_sources_display.short_description = "BC(s) source(s)"

    def ecart_js(self, obj=None):
        # Affiche la valeur initiale de l'écart, qui sera ensuite mise à jour dynamiquement par le JS
        val = obj.ecart if obj else 0
        color = 'red' if val < 0 else 'black'
        return format_html('<span class="js-ecart-dyn" style="color:{};">{}</span>', color, val)
    ecart_js.short_description = "Écart (live)"
    ecart_js.allow_tags = True

    def ecart_colored(self, obj):
        ecart = obj.ecart
        if ecart < 0:
            return format_html('<span style="color: red;">{}</span>', ecart)
        return ecart
    ecart_colored.short_description = "Écart"

    class Media:
        css = {
            'all': ('admin/css/compact_inline.css',)
        }
        js = ('admin/js/ecart_live_update.js',)

@admin.register(SalamGazTab)
class SalamGazTabAdmin(admin.ModelAdmin):
    list_display = ("reference", "date_export", "date_debut", "date_fin", "description")
    search_fields = ("reference", "description")
    list_filter = ("date_export",)
    inlines = [SalamGazTabLigneInline]
    fields = ("reference", "date_export", "date_debut", "date_fin", "description")
    readonly_fields = ("date_export",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Génération automatique des lignes si période renseignée
        if obj.date_debut and obj.date_fin:
            # Suppression des anciennes lignes
            obj.lignes.all().delete()
            from scrap_sga.models import ScrapDimagazBC
            bcs = ScrapDimagazBC.objects.filter(bc_date__gte=obj.date_debut, bc_date__lte=obj.date_fin)
            lignes_total = 0
            group_map = {}
            for bc in bcs:
                for line in bc.lines.all():
                    depositaire = bc.depositaire
                    societe = getattr(bc, 'fournisseur', None)
                    centre_emplisseur = getattr(bc, 'fournisseur_centre', None)
                    marque_bouteille = getattr(line.product, 'product_category_name', None)
                    if not marque_bouteille:
                        marque_bouteille = 'INCONNU'
                    key = (depositaire, marque_bouteille, societe, centre_emplisseur)
                    if key not in group_map:
                        group_map[key] = {
                            'depositaire': depositaire,
                            'marque_bouteille': marque_bouteille,
                            'societe': societe,
                            'centre_emplisseur': centre_emplisseur,
                            'qte_bd_3kg': 0,
                            'qte_bd_6kg': 0,
                            'qte_bd_12kg': 0,
                            'source_bcs': set(),
                        }
                    if '3kg' in line.product_name.lower():
                        group_map[key]['qte_bd_3kg'] += int(line.qty)
                    elif '6kg' in line.product_name.lower():
                        group_map[key]['qte_bd_6kg'] += int(line.qty)
                    elif '12kg' in line.product_name.lower():
                        group_map[key]['qte_bd_12kg'] += int(line.qty)
                    group_map[key]['source_bcs'].add(bc.pk)
            for k, data in group_map.items():
                # Calcul du montant HT total (mt_bl) pour ce groupe, une seule fois par BC unique
                data['mt_bl'] = sum([
                    bc.ht for bc in ScrapDimagazBC.objects.filter(pk__in=data['source_bcs']) if bc.ht
                ])
                poids_3kg = 3
                poids_6kg = 6
                poids_12kg = 12
                tonnage = data['qte_bd_3kg'] * poids_3kg + data['qte_bd_6kg'] * poids_6kg + data['qte_bd_12kg'] * poids_12kg
                ligne = SalamGazTabLigne.objects.create(
                    export=obj,
                    depositaire=data['depositaire'],
                    marque_bouteille=data['marque_bouteille'],
                    societe=data['societe'],
                    centre_emplisseur=data['centre_emplisseur'],
                    qte_bd_3kg=data['qte_bd_3kg'],
                    qte_bd_6kg=data['qte_bd_6kg'],
                    qte_bd_12kg=data['qte_bd_12kg'],
                    tonnage=tonnage,
                    mt_bl=data['mt_bl'],
                    mt_vers_virt=0,
                    ecart=0,
                    observation='',
                )
                ligne.source_bcs.set(data['source_bcs'])
                lignes_total += 1
            if lignes_total > 0:
                self.message_user(request, f"{lignes_total} lignes générées automatiquement pour la période sélectionnée.", messages.SUCCESS)
            else:
                self.message_user(request, "Aucune ligne générée pour la période sélectionnée.", messages.WARNING)

@admin.register(SalamGazTabLigne)
class SalamGazTabLigneAdmin(admin.ModelAdmin):
    form = SalamGazTabLigneForm
    list_display = (
        "export", "client", "depositaire", "marque_bouteille",
        "qte_bd_3kg", "qte_bd_6kg", "qte_bd_12kg", "tonnage", "societe", "centre_emplisseur", "mt_bl", "mt_vers_virt", "ecart_colored"
    )
    search_fields = ("client", "depositaire", "marque_bouteille", "societe", "centre_emplisseur")
    list_filter = ("export",)
    filter_horizontal = ("source_bcs",)
    readonly_fields = ("tonnage", "ecart_colored")

    def ecart_colored(self, obj):
        ecart = obj.ecart
        if ecart < 0:
            return format_html('<span style="color: red;">{}</span>', ecart)
        return ecart
    ecart_colored.short_description = "Écart"
    ecart_colored.admin_order_field = 'ecart'

    def get_field_queryset(self, db, db_field, request):
        return super().get_field_queryset(db, db_field, request)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        # Personnalise les labels Qté Bd -> Qté Bt
        if db_field.name == 'qte_bd_3kg':
            formfield.label = 'Qté Bt 3kg'
        elif db_field.name == 'qte_bd_6kg':
            formfield.label = 'Qté Bt 6kg'
        elif db_field.name == 'qte_bd_12kg':
            formfield.label = 'Qté Bt 12kg'
        return formfield
