from django.contrib import admin
from .models import GlobalConfig, CeleryConfig, RedisConfig, IntegrationConfig, FunctionalConfig, BrandingConfig, AdvancedConfig

# Register your models here.

@admin.register(CeleryConfig)
class CeleryConfigAdmin(admin.ModelAdmin):
    list_display = ("broker_url", "result_backend", "accept_content", "task_serializer", "result_serializer", "timezone", "updated_at")
    search_fields = ("broker_url", "result_backend", "timezone")
    readonly_fields = ("updated_at",)

@admin.register(RedisConfig)
class RedisConfigAdmin(admin.ModelAdmin):
    list_display = ("redis_url", "cache_db", "cache_timeout", "updated_at")
    search_fields = ("redis_url",)
    readonly_fields = ("updated_at",)

@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description", "updated_at")
    search_fields = ("key", "description")
    list_filter = ("updated_at",)
    ordering = ("key",)
    readonly_fields = ("updated_at",)

@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ("odoo_url", "odoo_db", "odoo_user", "notif_email_from", "notif_sms_provider", "updated_at")
    search_fields = ("odoo_url", "odoo_db", "odoo_user", "notif_email_from", "notif_sms_provider")
    readonly_fields = ("updated_at",)

@admin.register(FunctionalConfig)
class FunctionalConfigAdmin(admin.ModelAdmin):
    list_display = ("delai_relance_inactif", "delai_relance_app_non_installee", "dashboard_nb_jours_affichage", "export_max_rows", "updated_at")
    search_fields = ()
    readonly_fields = ("updated_at",)

@admin.register(BrandingConfig)
class BrandingConfigAdmin(admin.ModelAdmin):
    list_display = ("site_title", "logo_url", "support_contact", "updated_at")
    search_fields = ("site_title", "support_contact")
    readonly_fields = ("updated_at",)

@admin.register(AdvancedConfig)
class AdvancedConfigAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode", "updated_at")
    search_fields = ()
    readonly_fields = ("updated_at",)
