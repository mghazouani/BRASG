from django.contrib import admin
from .models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser, ScrapProduct, AuditLog, ScrappingConsole
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import subprocess
import sys
from django.utils import timezone

# Register your models here.

@admin.register(ScrapDimagazBC)
class ScrapDimagazBCAdmin(admin.ModelAdmin):
    list_display = (
        'odoo_id', 'name', 'fullname', 'bc_date', 'bl_date',
        'fournisseur', 'fournisseur_centre', 'depositaire',
        'montant_paye', 'done', 'sap', 'confirmed', 'remise', 'tva', 'ht', 'ttc',
        'bc_type', 'state', 'terminated', 'verify_state', 'qty_retenue', 'paye_par',
        'bl_number', 'solde', 'non_conforme', 'version', 'prefix', 'source', 'product_type',
        'display_name', 'create_date', 'write_date', 'lignes_bc_link'
    )
    search_fields = ('odoo_id', 'name', 'fullname', 'display_name', 'bl_number', 'state', 'product_type')
    list_filter = (
        'fournisseur', 'fournisseur_centre', 'depositaire',
        'done', 'sap', 'confirmed', 'state', 'terminated', 'non_conforme',
        'product_type', 'bc_type', 'prefix', 'source',
        ('bc_date', admin.DateFieldListFilter),
        ('bl_date', admin.DateFieldListFilter),
        ('create_date', admin.DateFieldListFilter),
        ('write_date', admin.DateFieldListFilter),
        ('montant_paye', admin.AllValuesFieldListFilter),
        ('ttc', admin.AllValuesFieldListFilter),
    )
    date_hierarchy = 'bc_date'
    readonly_fields = ('lignes_bc_link', 'odoo_id', 'name', 'fullname', 'bc_date', 'bl_date', 'fournisseur', 'fournisseur_centre', 'depositaire', 'montant_paye', 'done', 'sap', 'confirmed', 'remise', 'tva', 'ht', 'ttc', 'bc_type', 'state', 'terminated', 'verify_state', 'qty_retenue', 'paye_par', 'bl_number', 'solde', 'non_conforme', 'version', 'prefix', 'source', 'product_type', 'display_name', 'create_date', 'write_date')

    def lignes_bc_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:scrap_sga_scrapdimagazbcline_changelist') + f'?bc__id__exact={obj.id}'
        return format_html('<a href="{}">Voir les lignes BC associées</a>', url)
    lignes_bc_link.short_description = "Lignes BC associées"

@admin.register(ScrapDimagazBCLine)
class ScrapDimagazBCLineAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'bc', 'product', 'product_name', 'qty', 'qty_vide', 'qty_retenue', 'qty_defect', 'prix', 'subtotal', 'bc_date', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'product_name', 'product__name', 'bc__name')
    list_filter = (
        'product', 'bc',
        ('bc_date', admin.DateFieldListFilter),
        ('create_date', admin.DateFieldListFilter),
        ('write_date', admin.DateFieldListFilter),
        ('qty', admin.AllValuesFieldListFilter),
        ('prix', admin.AllValuesFieldListFilter),
    )
    date_hierarchy = 'bc_date'

@admin.register(ScrapFournisseur)
class ScrapFournisseurAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'name')

    def centres_associes_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:scrap_sga_scrapfournisseurcentre_changelist') + f'?fournisseur__id__exact={obj.id}'
        return format_html('<a href="{}">Voir les centres associés</a>', url)
    centres_associes_link.short_description = "Centres associés"

    readonly_fields = ('odoo_id', 'name', 'create_date', 'write_date', 'centres_associes_link')

@admin.register(ScrapFournisseurCentre)
class ScrapFournisseurCentreAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'fournisseur', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'name', 'fournisseur__name')

@admin.register(ScrapUser)
class ScrapUserAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'display_name', 'username', 'sap_id', 'codeclientSG', 'create_date', 'write_date')
    search_fields = ('odoo_id', 'display_name', 'username', 'sap_id', 'codeclientSG')

@admin.register(ScrapProduct)
class ScrapProductAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'product_id', 'product_id_name', 'product_category', 'product_category_name', 'prix', 'product_type', 'display_name', 'create_date', 'write_date')
    search_fields = ('name', 'display_name', 'product_id_name', 'product_category_name')
    list_filter = ('product_type', 'product_category_name')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('change_time', 'model_name', 'object_id', 'action', 'changed_by', 'source', 'diff_pretty')
    search_fields = ('model_name', 'object_id', 'changed_by', 'source')
    list_filter = ('model_name', 'action', 'changed_by', 'source')
    readonly_fields = ('model_name', 'object_id', 'action', 'changed_by', 'change_time', 'diff', 'source')
    ordering = ('-change_time',)
    def diff_pretty(self, obj):
        import json
        return json.dumps(obj.diff, indent=2, ensure_ascii=False)
    diff_pretty.short_description = 'Diff (JSON)'

class ScrappingConsoleAdmin(admin.ModelAdmin):
    list_display = ('scrap_type', 'status', 'last_run', 'auto_schedule', 'schedule_cron', 'updated_at', 'run_now_button')
    list_filter = ('scrap_type', 'status', 'auto_schedule')
    search_fields = ('scrap_type', 'result')
    readonly_fields = ('last_run', 'status', 'result', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('scrap_type', 'params', 'auto_schedule', 'schedule_cron')
        }),
        ('Monitoring', {
            'fields': ('status', 'last_run', 'result', 'created_at', 'updated_at')
        })
    )

    class Media:
        js = ('scrap_sga/js/scrapconsole_live.js', 'scrap_sga/js/scrapconsole_params_help.js')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Ajout dynamique d'une aide sur les paramètres selon le type de scrap
        param_help = {
            'sync_BcLinbc': [
                {'arg': 'batch_size', 'type': 'int', 'help': 'Taille du batch pour la synchro BC/Ligne BC (défaut: 100)'},
                {'arg': 'last', 'type': 'int', 'help': 'Limiter aux X derniers BC (et leurs lignes)'},
                {'arg': 'name', 'type': 'str', 'help': 'Filtrer sur le champ name de dimagaz.bc'},
            ],
            'test_view_odoo': [
                {'arg': 'name', 'type': 'str', 'help': 'Nom (name) du BC à exporter'},
                {'arg': 'product_id', 'type': 'int', 'help': 'ID Odoo du produit à visualiser (optionnel)'},
            ],
        }
        scrap_map = {
            'bc': 'sync_BcLinbc',
            'bc_line': 'sync_BcLinbc',
            'user': None,
            'product': None,
            'fournisseur': None,
            'centre': None,
        }
        scrap_type = getattr(obj, 'scrap_type', None) if obj else None
        cmd = scrap_map.get(scrap_type)
        if cmd and 'params' in form.base_fields:
            help_txt = '\n'.join([
                f"--{p['arg']} : {p['type']} | {p['help']}" for p in param_help.get(cmd, [])
            ])
            form.base_fields['params'].help_text += f"\n\nParamètres disponibles pour ce scrap :\n{help_txt}"
        return form

    def render_change_form(self, request, context, *args, **kwargs):
        # Ajoute l'ID de l'objet pour le JS uniquement si le champ 'result' existe dans le formulaire
        adminform = context.get('adminform')
        if context.get('original') and adminform:
            form = adminform.form
            if 'result' in form.fields:
                form.fields['result'].widget.attrs['data-scrap-id'] = context['original'].pk
        return super().render_change_form(request, context, *args, **kwargs)

    def run_now_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Lancer maintenant</a>',
            f'run_scrap/{obj.pk}/'
        )
    run_now_button.short_description = 'Lancement manuel'
    run_now_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run_scrap/<int:pk>/', self.admin_site.admin_view(self.run_scrap), name='run_scrap'),
        ]
        return custom_urls + urls

    def run_scrap(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        if obj.status in ('success', 'failed', 'erreur'):
            self.message_user(request, "Ce scrap a déjà été exécuté et ne peut pas être relancé.", level=messages.WARNING)
            return redirect(f'/admin/scrap_sga/scrappingconsole/{pk}/change/')
        scrap_map = {
            'sync_user': 'sync_user',
            'sync_products': 'sync_products',
            'sync_FounisseursCentres': 'sync_FounisseursCentres',
            'sync_BcLinbc': 'sync_BcLinbc',
        }
        cmd = scrap_map.get(obj.scrap_type)
        if not cmd:
            messages.error(request, "Type de scrap non supporté.")
            return redirect(request.META.get('HTTP_REFERER'))
        # Ajout dynamique des paramètres passés au script
        params = obj.params or {}
        cmdline = [sys.executable, 'manage.py', cmd]
        for k, v in params.items():
            if v not in (None, "", []):
                arg = f"--{k.replace('_', '-')}"
                if isinstance(v, bool):
                    if v:
                        cmdline.append(arg)
                else:
                    cmdline.extend([arg, str(v)])
        try:
            result = subprocess.run(cmdline, capture_output=True, text=True, cwd=sys.path[0], timeout=600)
            obj.status = 'success' if result.returncode == 0 else 'failed'
            obj.result = result.stdout + '\n' + result.stderr
            obj.last_run = timezone.now()
            obj.save()
            messages.success(request, f"Scrap '{obj.get_scrap_type_display()}' lancé. Statut : {obj.status}")
        except Exception as e:
            obj.status = 'failed'
            obj.result = str(e)
            obj.last_run = timezone.now()
            obj.save()
            messages.error(request, f"Erreur lors du lancement : {e}")
        return redirect(f'/admin/scrap_sga/scrappingconsole/{pk}/change/')

    def get_readonly_fields(self, request, obj=None):
        ro_fields = super().get_readonly_fields(request, obj)
        if obj and obj.status in ('running', 'success', 'failed', 'erreur'):
            # Tous les champs deviennent readonly si le scrap est terminé ou en cours
            return [f.name for f in self.model._meta.fields]
        return ro_fields

    def has_change_permission(self, request, obj=None):
        # Interdire toute modification si le scrap est terminé ou en cours
        if obj and obj.status in ('running', 'success', 'failed', 'erreur'):
            return False
        return super().has_change_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Désactive l'action "Lancer maintenant" si un scrap est terminé ou en cours
        if any(obj.status in ('running', 'success', 'failed', 'erreur') for obj in self.model.objects.all()):
            if 'run_scrap' in actions:
                actions.pop('run_scrap')
        return actions

admin.site.register(ScrappingConsole, ScrappingConsoleAdmin)
