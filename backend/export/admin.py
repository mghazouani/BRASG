from django import forms
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
from django.urls import path
from datetime import datetime
from .models import SalamGazTab, SalamGazTabLigne
from scrap_sga.models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapProduct, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser
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
        widgets = {
            'prix_3kg': forms.NumberInput(attrs={'step': '0.01', 'style': 'width: 55px;', 'maxlength': '3', 'max': '999', 'required': 'required'}),
            'prix_6kg': forms.NumberInput(attrs={'step': '0.01', 'style': 'width: 55px;', 'maxlength': '3', 'max': '999', 'required': 'required'}),
            'prix_12kg': forms.NumberInput(attrs={'step': '0.01', 'style': 'width: 55px;', 'maxlength': '3', 'max': '999', 'required': 'required'}),
            'qte_bd_3kg': forms.NumberInput(attrs={'min': '0', 'style': 'width: 55px;', 'required': 'required'}),
            'qte_bd_6kg': forms.NumberInput(attrs={'min': '0', 'style': 'width: 55px;', 'required': 'required'}),
            'qte_bd_12kg': forms.NumberInput(attrs={'min': '0', 'style': 'width: 55px;', 'required': 'required'}),
            'mt_bl': forms.NumberInput(attrs={'step': '0.01', 'style': 'width: 100px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'qte_bd_3kg' in self.fields:
            self.fields['qte_bd_3kg'].label = 'Qté Bt 03kg'
            self.fields['qte_bd_3kg'].initial = 0
        if 'qte_bd_6kg' in self.fields:
            self.fields['qte_bd_6kg'].label = 'Qté Bt 06kg'
            self.fields['qte_bd_6kg'].initial = 0
        if 'qte_bd_12kg' in self.fields:
            self.fields['qte_bd_12kg'].label = 'Qté Bt 12kg'
            self.fields['qte_bd_12kg'].initial = 0
        # S'assurer que les champs prix et mt_bl sont bien éditables
        for f in ['prix_3kg', 'prix_6kg', 'prix_12kg', 'mt_bl']:
            if f in self.fields:
                self.fields[f].disabled = False
                self.fields[f].required = True
                if f.startswith('prix_'):
                    self.fields[f].initial = 0
        # Change les labels des champs prix en PU xxKG
        if 'prix_3kg' in self.fields:
            self.fields['prix_3kg'].label = 'PU 03kg'
        if 'prix_6kg' in self.fields:
            self.fields['prix_6kg'].label = 'PU 06kg'
        if 'prix_12kg' in self.fields:
            self.fields['prix_12kg'].label = 'PU 12kg'
        # Champ depositaire : autocomplétion sur tous les ScrapUser
        from scrap_sga.models import ScrapUser
        if 'depositaire' in self.fields:
            self.fields['depositaire'].widget = forms.TextInput(attrs={
                'class': 'vTextField autocomplete-depositaire',
                'autocomplete': 'off',
                'placeholder': 'Nom ou code client...'
            })
            # Optionnel : liste pour datalist html5 (non natif admin)
            try:
                users = ScrapUser.objects.all().order_by('nom')
                self.fields['depositaire'].widget.attrs['list'] = 'depositaire-list'
                self.fields['depositaire'].widget.attrs['autocomplete'] = 'off'
                self.fields['depositaire'].widget.attrs['data-autocomplete-source'] = ','.join([
                    f"{u.nom} ({u.codeclientSG})" if u.codeclientSG else u.nom for u in users if u.nom
                ])
            except Exception:
                pass

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

class SalamGazTabLigneInline(admin.TabularInline):
    model = SalamGazTabLigne
    form = SalamGazTabLigneForm
    extra = 0
    show_change_link = True
    filter_horizontal = ("source_bcs",)
    autocomplete_fields = ["depositaire"]
    fields = (
        "client", "depositaire", "marque_bouteille",
        "qte_bd_3kg", "prix_3kg", "qte_bd_6kg", "prix_6kg", "qte_bd_12kg", "prix_12kg",
        "societe", "centre_emplisseur", "mt_bl", "mt_vers_virt", "observation", "tonnage", "ecart_js"
    )
    readonly_fields = ("tonnage", "ecart_js")

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'depositaire':
            from scrap_sga.models import ScrapUser
            kwargs['queryset'] = ScrapUser.objects.all()
            kwargs['to_field_name'] = 'id'
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.display_name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
                    
                    # Déterminer la marque de bouteille (DIMAGAZ ou ZERGAGAZ) à partir du nom du produit
                    product_brand = None
                    if line.product_name:
                        if 'dimagaz' in line.product_name.lower():
                            product_brand = 'DIMAGAZ'
                        elif 'zergagaz' in line.product_name.lower():
                            product_brand = 'ZERGAGAZ'
                    
                    # Si on a détecté une marque spécifique, l'utiliser à la place de product_category_name
                    if product_brand:
                        marque_bouteille = product_brand
                    else:
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
                            'prix_3kg': 0,
                            'prix_6kg': 0,
                            'prix_12kg': 0,
                            'source_bcs': set(),
                        }
                    
                    # Extraction des quantités et prix
                    if line.product_name:
                        pname = line.product_name.lower()
                        qty = int(line.qty) if line.qty is not None else 0
                        prix = float(line.prix) if line.prix is not None else 0
                        
                        # Enregistre le prix si non nul, sinon cherche dans le produit
                        if not prix and line.product_id:
                            prod = ScrapProduct.objects.filter(id=line.product_id).first()
                            if prod and prod.prix:
                                prix = float(prod.prix)
                        
                        # Stocke la quantité et le prix selon le type de bouteille
                        # Détection améliorée pour tous les types de bouteilles
                        if any(marker in pname for marker in ['3kg', '3 kg']):
                            group_map[key]['qte_bd_3kg'] += qty
                            if prix > 0:  # Ne remplace que si le prix est valide
                                group_map[key]['prix_3kg'] = prix
                        elif any(marker in pname for marker in ['6kg', '6 kg']):
                            group_map[key]['qte_bd_6kg'] += qty
                            if prix > 0:
                                group_map[key]['prix_6kg'] = prix
                        elif any(marker in pname for marker in ['12kg', '12 kg']):
                            group_map[key]['qte_bd_12kg'] += qty
                            if prix > 0:
                                group_map[key]['prix_12kg'] = prix
                    
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

                # Recherche du code client SG à partir du ou des BC sources (on prend le premier BC trouvé)
                codeclientSG = None
                debug_query = None
                debug_user = None
                if data['source_bcs']:
                    first_bc = ScrapDimagazBC.objects.filter(pk__in=data['source_bcs']).first()
                    if first_bc and getattr(first_bc, 'depositaire_id', None):
                        debug_query = f"ScrapUser.objects.filter(id={first_bc.depositaire_id}).first()"
                        user = ScrapUser.objects.filter(id=first_bc.depositaire_id).first()
                        debug_user = user.codeclientSG if user else None
                        print(f"[EXPORT][DEBUG] Requête: {debug_query} -> Résultat: {debug_user}")

                ligne = SalamGazTabLigne.objects.create(
                    export=obj,
                    client=debug_user,
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
                    prix_3kg=data['prix_3kg'],
                    prix_6kg=data['prix_6kg'],
                    prix_12kg=data['prix_12kg'],
                )
                ligne.source_bcs.set(data['source_bcs'])
                lignes_total += 1
            if lignes_total > 0:
                self.message_user(request, f"{lignes_total} lignes générées automatiquement pour la période sélectionnée.", messages.SUCCESS)
            else:
                self.message_user(request, "Aucune ligne générée pour la période sélectionnée.", messages.WARNING)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'depositaire':
            from scrap_sga.models import ScrapUser
            kwargs['queryset'] = ScrapUser.objects.all()
            kwargs['to_field_name'] = 'id'
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.display_name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    readonly_fields = ("client", "tonnage", "ecart_colored")

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'depositaire':
            from scrap_sga.models import ScrapUser
            kwargs['queryset'] = ScrapUser.objects.all()
            kwargs['to_field_name'] = 'id'
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.display_name
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
