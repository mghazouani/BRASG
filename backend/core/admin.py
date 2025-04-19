from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, AuditLog, ImportFichier
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

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('sap_id', 'nom_client', 'statut_general', 'langue', 'telephone', 'date_creation')
    search_fields = ('sap_id', 'nom_client', 'telephone')
    list_filter = ('statut_general', 'langue', 'region', 'ville')
    readonly_fields = ('date_creation', 'date_derniere_maj')

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
                        client, created_flag = Client.objects.update_or_create(
                            sap_id=row['sap_id'],
                            defaults={
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
                                'region': row.get('region', ''),
                                'ville': row.get('ville', ''),
                                'canal_contact': row.get('canal_contact', ''),
                                'relance_planifiee': bool(row.get('relance_planifiee', False)),
                                'cree_par_user': user,
                                'modifie_par_user': user,
                            }
                        )
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
    list_display = ('date_import', 'utilisateur', 'fichier', 'resultat', 'termine', 'format_attendu')
    readonly_fields = ('resultat', 'termine', 'date_import', 'format_attendu')
    search_fields = ('utilisateur__username', 'fichier')
    list_filter = ('termine',)

    def format_attendu(self, obj=None):
        champs = [
            ('sap_id', '<span style="color:#b91c1c;font-weight:bold">OBLIGATOIRE</span>, unique, non vide'),
            ('nom_client', '<span style="color:#b91c1c;font-weight:bold">OBLIGATOIRE</span>, non vide'),
            ('telephone', '<span style="color:#b91c1c;font-weight:bold">OBLIGATOIRE</span>, non vide'),
            ('langue', 'francais ou arabe <span style="color:#2563eb">(défaut : francais)</span>'),
            ('statut_general', 'actif, inactif ou bloque <span style="color:#2563eb">(défaut : actif)</span>'),
            ('notification_client', 'TRUE/FALSE'),
            ('date_notification', 'YYYY-MM-DD ou vide'),
            ('a_demande_aide', 'TRUE/FALSE'),
            ('nature_aide', 'texte libre'),
            ('app_installee', 'TRUE/FALSE'),
            ('maj_app', 'texte libre'),
            ('commentaire_agent', 'texte libre'),
            ('segment_client', 'texte libre'),
            ('region', 'texte libre'),
            ('ville', 'texte libre'),
            ('canal_contact', 'texte libre'),
            ('relance_planifiee', 'TRUE/FALSE'),
        ]
        html = """
        <div style='background:#f0f9ff;border:2px solid #2563eb;padding:16px;border-radius:8px;margin-bottom:16px;'>
        <h3 style='color:#2563eb;margin-top:0;'>Format attendu du fichier d'import</h3>
        <a href='/static/import_template_clients.csv' download style='display:inline-block;margin-bottom:10px;background:#2563eb;color:#fff;padding:6px 18px;border-radius:4px;text-decoration:none;font-weight:bold;'>⬇️ Télécharger le modèle CSV</a>
        <table style='border-collapse:collapse;width:100%;background:#fff;'>
            <tr style='background:#2563eb;color:#fff;'>
                <th style='padding:8px;border:1px solid #2563eb;'>Colonne</th>
                <th style='padding:8px;border:1px solid #2563eb;'>Contraintes / Remarques</th>
            </tr>
        """
        for i, (nom, remarque) in enumerate(champs):
            bg = '#f1f5f9' if i % 2 == 0 else '#fff'
            html += f"<tr style='background:{bg};'><td style='padding:8px;border:1px solid #e5e7eb;'><b>{nom}</b></td><td style='padding:8px;border:1px solid #e5e7eb;'>{remarque}</td></tr>"
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
