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
    fields = ("reference", "date_debut", "date_fin", "description")
    readonly_fields = ("date_export",)
    
    class Media:
        js = ('admin/js/ecart_live_update.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Initialiser une liste pour stocker les messages de log
        log_messages = []
        
        # Fonction pour ajouter un log à la fois dans la console et dans la liste des messages
        def add_log(message):
            print(message)
            log_messages.append(message)
        
        # Génération automatique des lignes seulement lors de la création initiale, pas lors des modifications
        if obj.date_debut and obj.date_fin and not change:
            # Suppression des anciennes lignes uniquement lors de la création initiale
            obj.lignes.all().delete()
            from scrap_sga.models import ScrapDimagazBC, ScrapUser
            
            # Vérification et log des dates
            add_log(f"[EXPORT][DEBUG] Filtrage des BC entre {obj.date_debut} et {obj.date_fin}")
            
            # Conversion des dates en UTC pour le filtrage
            from django.utils import timezone
            import pytz
            
            # Définir la timezone de Casablanca
            casablanca_tz = pytz.timezone('Africa/Casablanca')
            
            # Convertir les dates en UTC si elles ne le sont pas déjà
            if obj.date_debut.tzinfo is None:
                date_debut_utc = casablanca_tz.localize(obj.date_debut).astimezone(pytz.UTC)
            else:
                date_debut_utc = obj.date_debut.astimezone(pytz.UTC)
                
            if obj.date_fin.tzinfo is None:
                date_fin_utc = casablanca_tz.localize(obj.date_fin).astimezone(pytz.UTC)
            else:
                date_fin_utc = obj.date_fin.astimezone(pytz.UTC)
            
            add_log(f"[EXPORT][DEBUG] Date début originale: {obj.date_debut}, convertie en UTC: {date_debut_utc}")
            add_log(f"[EXPORT][DEBUG] Date fin originale: {obj.date_fin}, convertie en UTC: {date_fin_utc}")
            
            # Ajustement automatique de la date de fin pour inclure toute la journée
            # Si la date de fin est dans la même journée que maintenant, étendre jusqu'à 23:59:59
            now = timezone.now()
            if date_fin_utc.date() == now.date():
                # Étendre la date de fin jusqu'à la fin de la journée
                from datetime import datetime, time
                end_of_day = datetime.combine(date_fin_utc.date(), time(23, 59, 59))
                end_of_day = pytz.UTC.localize(end_of_day)
                date_fin_utc = end_of_day
                add_log(f"[EXPORT][DEBUG] Date fin ajustée automatiquement à la fin de la journée: {date_fin_utc}")
            
            # Filtrage de base : exclure les BC sans dépositaire
            bcs = ScrapDimagazBC.objects.filter(depositaire__isnull=False)
            
            # Appliquer le filtre de date
            bcs = bcs.filter(bc_date__gte=date_debut_utc, bc_date__lte=date_fin_utc)
            
            # Initialisation du dictionnaire pour stocker les prix par défaut de chaque type de produit
            default_prices = {
                'DIMAGAZ': {'3kg': 0, '6kg': 0, '12kg': 0},
                'ZERGAGAZ': {'3kg': 0, '6kg': 0, '12kg': 0},
            }
            
            # Récupération des prix par défaut depuis ScrapProduct
            from scrap_sga.models import ScrapProduct
            
            # Pour DIMAGAZ
            for bottle_type in ['3kg', '6kg', '12kg']:
                products = ScrapProduct.objects.filter(
                    name__icontains='dimagaz'
                ).filter(
                    name__icontains=bottle_type
                )
                for product in products:
                    if product.prix and product.prix > 0:
                        default_prices['DIMAGAZ'][bottle_type] = float(product.prix)
                        add_log(f"[EXPORT][DEBUG] Prix par défaut pour DIMAGAZ {bottle_type}: {default_prices['DIMAGAZ'][bottle_type]} (produit: {product.name})")
                        break
            
            # Pour ZERGAGAZ
            for bottle_type in ['3kg', '6kg', '12kg']:
                products = ScrapProduct.objects.filter(
                    name__icontains='zergagaz'
                ).filter(
                    name__icontains=bottle_type
                )
                for product in products:
                    if product.prix and product.prix > 0:
                        default_prices['ZERGAGAZ'][bottle_type] = float(product.prix)
                        add_log(f"[EXPORT][DEBUG] Prix par défaut pour ZERGAGAZ {bottle_type}: {default_prices['ZERGAGAZ'][bottle_type]} (produit: {product.name})")
                        break
            
            # Vérification des BC par dépositaire
            depositaires_data = {}
            for bc in bcs:
                dep_id = bc.depositaire_id
                if dep_id not in depositaires_data:
                    user = ScrapUser.objects.filter(id=dep_id).first()
                    name = user.display_name if user else f"ID:{dep_id}"
                    depositaires_data[dep_id] = {
                        "name": name,
                        "count": 0,
                        "bc_ids": []
                    }
                depositaires_data[dep_id]["count"] += 1
                depositaires_data[dep_id]["bc_ids"].append(bc.id)
            
            # Log détaillé des dépositaires
            for dep_id, data in depositaires_data.items():
                add_log(f"[EXPORT][DEBUG] Dépositaire: {data['name']} (ID: {dep_id}) - {data['count']} BC(s) - IDs: {data['bc_ids'][:5]}{' et plus...' if len(data['bc_ids']) > 5 else ''}")
            
            # Vérification des BC spécifiques pour ALPHA
            alpha_bcs = ScrapDimagazBC.objects.filter(
                bc_date__gte=obj.date_debut, 
                bc_date__lte=obj.date_fin,
                depositaire__display_name__icontains="ALPHA"
            )
            if alpha_bcs.exists():
                add_log(f"[EXPORT][DEBUG] BC pour ALPHA trouvés: {alpha_bcs.count()}")
                for bc in alpha_bcs[:3]:  # Limiter à 3 pour éviter trop de logs
                    add_log(f"[EXPORT][DEBUG] BC ALPHA: ID={bc.id}, Name={bc.name}, Date={bc.bc_date}")
            else:
                add_log(f"[EXPORT][DEBUG] Aucun BC pour ALPHA trouvé dans la période sélectionnée")
            
            lignes_total = 0
            group_map = {}
            for bc in bcs:
                for line in bc.lines.all():
                    # Vérifier que le dépositaire existe
                    if not bc.depositaire:
                        add_log(f"[EXPORT][DEBUG] BC {bc.name} sans dépositaire, ignoré")
                        continue
                        
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
                    
                    # Utiliser l'ID du dépositaire dans la clé pour garantir l'unicité
                    key = (depositaire.id if depositaire else None, marque_bouteille, 
                           societe.id if societe else None, 
                           centre_emplisseur.id if centre_emplisseur else None)
                    if key not in group_map:
                        group_map[key] = {
                            'depositaire': depositaire,
                            'marque_bouteille': marque_bouteille,
                            'societe': societe,
                            'centre_emplisseur': centre_emplisseur,
                            'qte_bd_3kg': 0,
                            'qte_bd_6kg': 0,
                            'qte_bd_12kg': 0,
                            'prix_3kg': default_prices[marque_bouteille]['3kg'] if marque_bouteille in default_prices else 0,
                            'prix_6kg': default_prices[marque_bouteille]['6kg'] if marque_bouteille in default_prices else 0,
                            'prix_12kg': default_prices[marque_bouteille]['12kg'] if marque_bouteille in default_prices else 0,
                            'source_bcs': set(),
                        }
                    
                    # Extraction des quantités et prix
                    if line.product_name:
                        pname = line.product_name.lower()
                        qty = int(line.qty) if line.qty is not None else 0
                        prix = float(line.prix) if line.prix is not None else 0
                        
                        # Détermine le type de bouteille (3kg, 6kg ou 12kg)
                        bottle_type = None
                        if any(marker in pname for marker in ['3kg', '3 kg']):
                            bottle_type = '3kg'
                        elif any(marker in pname for marker in ['6kg', '6 kg']):
                            bottle_type = '6kg'
                        elif any(marker in pname for marker in ['12kg', '12 kg']):
                            bottle_type = '12kg'
                        
                        # Si le prix n'est pas disponible dans la ligne BC, chercher dans ScrapProduct
                        if not prix and bottle_type and line.product:
                            from scrap_sga.models import ScrapProduct
                            # Construire le pattern de recherche pour le produit correspondant
                            search_terms = []
                            
                            # Ajouter la marque (DIMAGAZ ou ZERGAGAZ)
                            if marque_bouteille in ['DIMAGAZ', 'ZERGAGAZ']:
                                search_terms.append(marque_bouteille.lower())
                            
                            # Ajouter le type de bouteille
                            search_terms.append(bottle_type)
                            
                            # Rechercher les produits correspondants
                            matching_products = ScrapProduct.objects.filter(
                                name__icontains=search_terms[0]
                            ).filter(
                                name__icontains=search_terms[1]
                            )
                            
                            # Prendre le premier produit correspondant avec un prix
                            for product in matching_products:
                                if product.prix and product.prix > 0:
                                    prix = float(product.prix)
                                    add_log(f"[EXPORT][DEBUG] Prix récupéré de ScrapProduct pour {marque_bouteille} {bottle_type}: {prix} (produit: {product.name})")
                                    break
                        
                        # Stocke la quantité et le prix selon le type de bouteille
                        if bottle_type == '3kg':
                            group_map[key]['qte_bd_3kg'] += qty
                            if prix > 0:  # Ne remplace que si le prix est valide
                                group_map[key]['prix_3kg'] = prix
                        elif bottle_type == '6kg':
                            group_map[key]['qte_bd_6kg'] += qty
                            if prix > 0:
                                group_map[key]['prix_6kg'] = prix
                        elif bottle_type == '12kg':
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
                depositaire_name = None
                
                if data['source_bcs']:
                    first_bc = ScrapDimagazBC.objects.filter(pk__in=data['source_bcs']).first()
                    if first_bc and getattr(first_bc, 'depositaire_id', None):
                        debug_query = f"ScrapUser.objects.filter(id={first_bc.depositaire_id}).first()"
                        user = ScrapUser.objects.filter(id=first_bc.depositaire_id).first()
                        debug_user = user.codeclientSG if user else None
                        
                        # Récupérer le nom du dépositaire pour l'affichage, même si codeclientSG est None
                        if user:
                            depositaire_name = user.display_name
                            add_log(f"[EXPORT][DEBUG] Dépositaire trouvé: {depositaire_name} (codeclientSG: {debug_user})")
                        else:
                            add_log(f"[EXPORT][DEBUG] Utilisateur avec ID={first_bc.depositaire_id} non trouvé")
                
                # Créer la ligne même si codeclientSG est None
                ligne = SalamGazTabLigne.objects.create(
                    export=obj,
                    client=debug_user,  # Peut être None
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
            
            # Afficher les logs dans l'interface d'administration
            if log_messages:
                self.message_user(
                    request, 
                    f"Logs de génération :<br>{'<br>'.join(log_messages)}", 
                    level=messages.INFO
                )

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
