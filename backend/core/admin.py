from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, AuditLog, ImportFichier, DashboardConfig, Ville
from django import forms
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import pandas as pd
from django.utils.safestring import mark_safe

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Ajout uniquement des champs personnalisés non déjà présents
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'last_login')
    search_fields = ('username', 'email', 'role')

class ImportClientsForm(forms.Form):
    fichier = forms.FileField(label="Fichier Excel ou CSV")

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Charger choix depuis la config JSON
        config = DashboardConfig.objects.first()
        settings = config.settings if config else {}
        # Liste déroulante pour langue et statut
        self.fields['langue'].widget = forms.Select(choices=[(opt['value'], opt['label']) for opt in settings.get('langue', [])])
        self.fields['statut_general'].widget = forms.Select(choices=[(opt['value'], opt['label']) for opt in settings.get('statut_general', [])])
        # Boutons radio pour booléens
        for bf in ['notification_client', 'a_demande_aide', 'app_installee']:
            self.fields[bf].widget = forms.RadioSelect(choices=[(opt['value'], opt['label']) for opt in settings.get(bf, [])])

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    list_display = ('sap_id', 'nom_client', 'statut_general', 'langue', 'telephone', 'date_creation')
    search_fields = ('sap_id', 'nom_client', 'telephone')
    list_filter = ('statut_general', 'langue', 'ville__region')
    # Region auto-populée et non modifiable
    readonly_fields = ('date_creation', 'date_derniere_maj', 'region')
    # Ordre des champs et inclusion explicite de 'ville' et 'region'
    fields = (
        'sap_id', 'nom_client', 'telephone', 'langue', 'statut_general',
        'notification_client', 'date_notification', 'action', 'a_demande_aide',
        'nature_aide', 'app_installee', 'maj_app', 'commentaire_agent',
        'segment_client', 'ville', 'region', 'canal_contact',
        'date_creation', 'date_derniere_maj', 'relance_planifiee',
        'cree_par_user', 'modifie_par_user'
    )

    class Media:
        js = ()
        css = {
            'all': ('admin/css/widgets.css',)
        }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-clients/', self.admin_site.admin_view(self.import_clients_view), name='import-clients'),
        ]
        return custom_urls + urls

    def import_clients_view(self, request):
        if request.method == 'POST':
            form = ImportClientsForm(request.POST, request.FILES)
            if form.is_valid():
                fichier = form.cleaned_data['fichier']
                try:
                    if fichier.name.endswith('.csv'):
                        df = pd.read_csv(fichier)
                    else:
                        df = pd.read_excel(fichier)
                    created, updated = 0, 0
                    user = request.user if request.user.is_authenticated else None
                    for _, row in df.iterrows():
                        # Valider l'ID de ville et récupérer l'objet Ville
                        ville_obj = None
                        ville_id = row.get('ville')
                        if ville_id:
                            try:
                                ville_obj = Ville.objects.get(id=ville_id)
                            except Ville.DoesNotExist:
                                self.message_user(request, f"Ville introuvable: {ville_id}", messages.WARNING)
                        defaults = {
                            'nom_client': row.get('nom_client', ''),
                            'telephone': row.get('telephone', ''),
                            'langue': row.get('langue', 'francais'),
                            'statut_general': row.get('statut_general', 'actif'),
                            'notification_client': bool(row.get('notification_client', False)),
                            'date_notification': row.get('date_notification') or None,
                            'a_demande_aide': bool(row.get('a_demande_aide', False)),
                            'nature_aide': row.get('nature_aide', ''),
                            'app_installee': bool(row.get('app_installee', False)),
                            'maj_app': row.get('maj_app', ''),
                            'commentaire_agent': row.get('commentaire_agent', ''),
                            'segment_client': row.get('segment_client', ''),
                            'ville': ville_obj,
                            'canal_contact': row.get('canal_contact', ''),
                            'relance_planifiee': bool(row.get('relance_planifiee', False)),
                            'cree_par_user': user,
                            'modifie_par_user': user,
                        }
                        client, created_flag = Client.objects.update_or_create(sap_id=row['sap_id'], defaults=defaults)
                        client._current_user = user
                        client.save()
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
                    self.message_user(request, f"Import terminé : {created} créés, {updated} mis à jour.", messages.SUCCESS)
                    return redirect('..')
                except Exception as e:
                    self.message_user(request, f"Erreur lors de l'import : {e}", messages.ERROR)
        else:
            form = ImportClientsForm()
        from django.template.response import TemplateResponse
        return TemplateResponse(request, "admin/import_clients.html", {"form": form, "title": "Import de clients"})

@admin.register(ImportFichier)
class ImportFichierAdmin(admin.ModelAdmin):
    list_display = ('date_import', 'utilisateur', 'fichier', 'resultat', 'termine')
    readonly_fields = ('resultat', 'termine', 'date_import')
    change_list_template = 'admin/core/importfichier/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_format'] = self.format_attendu()
        return super().changelist_view(request, extra_context=extra_context)

    def format_attendu(self, obj=None):
        try:
            config = DashboardConfig.objects.first()
            settings = config.settings if config else {}
        except:
            settings = {}
        metadata = {
            'sap_id': {'required': True, 'type': 'Texte (unique, non vide)'},
            'nom_client': {'required': True, 'type': 'Texte (non vide)'},
            'telephone': {'required': True, 'type': 'Texte (non vide)'},
            'langue': {'required': False, 'type': 'Enum (arabe/francais)'},
            'statut_general': {'required': False, 'type': 'Enum (actif/inactif/bloque)'},
            'notification_client': {'required': False, 'type': 'Booléen'},
            'date_notification': {'required': False, 'type': 'Date (YYYY-MM-DD)'},
            'a_demande_aide': {'required': False, 'type': 'Booléen'},
            'nature_aide': {'required': False, 'type': 'Texte libre'},
            'app_installee': {'required': False, 'type': 'Booléen'},
            'maj_app': {'required': False, 'type': 'Texte libre'},
            'commentaire_agent': {'required': False, 'type': 'Texte libre'},
            'segment_client': {'required': False, 'type': 'Texte libre'},
            'ville': {'required': False, 'type': 'ID (core_ville)'},
            'canal_contact': {'required': False, 'type': 'Texte libre'},
            'relance_planifiee': {'required': False, 'type': 'Booléen'},
        }
        html = """
        <div style='background:#f0f9ff;border:2px solid #2563eb;padding:16px;border-radius:8px;margin-bottom:16px;'>
        <h3 style='color:#2563eb;margin-top:0;'>Format attendu du fichier d'import</h3>
        <a href='/static/import_template_clients.csv' download style='display:inline-block;margin-bottom:10px;background:#2563eb;color:#fff;padding:6px 18px;border-radius:4px;text-decoration:none;font-weight:bold;'>⬇️ Télécharger le modèle CSV</a>
        <table style='border-collapse:collapse;width:100%;background:#fff;'>
            <tr style='background:#2563eb;color:#fff;'>
                <th style='padding:8px;border:1px solid #2563eb;'>Champ</th>
                <th style='padding:8px;border:1px solid #2563eb;'>Paramètres JSON</th>
                <th style='padding:8px;border:1px solid #2563eb;'>Obligatoire</th>
                <th style='padding:8px;border:1px solid #2563eb;'>Type</th>
            </tr>
        """
        for i, field in enumerate(metadata):
            val = settings.get(field)
            if isinstance(val, list):
                details = ', '.join(f"{opt['value']} : {opt['label']}" for opt in val)
            else:
                details = val or ''
            req = 'Oui' if metadata[field]['required'] else 'Non'
            ftype = metadata[field]['type']
            bg = '#f1f5f9' if i % 2 == 0 else '#fff'
            html += f"<tr style='background:{bg};'><td style='padding:8px;border:1px solid #e5e7eb;'><b>{field}</b></td><td style='padding:8px;border:1px solid #e5e7eb;'>{details}</td><td style='padding:8px;border:1px solid #e5e7eb;'>{req}</td><td style='padding:8px;border:1px solid #e5e7eb;'>{ftype}</td></tr>"
        html += "</table></div>"
        return mark_safe(html)
    format_attendu.short_description = "Format attendu du fichier"
    format_attendu.allow_tags = True

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'action', 'user', 'timestamp')
    search_fields = ('table_name', 'action', 'user__username')
    list_filter = ('action', 'table_name', 'timestamp')
    readonly_fields = ('table_name', 'record_id', 'user', 'action', 'champs_changes', 'timestamp')

@admin.register(DashboardConfig)
class DashboardConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'settings')
    readonly_fields = ('id',)
    fieldsets = (
        (None, {'fields': ('settings',)}),
    )
