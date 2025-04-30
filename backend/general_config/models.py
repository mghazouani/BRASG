from django.db import models

# Create your models here.

class CeleryConfig(models.Model):
    broker_url = models.CharField(max_length=255, verbose_name="Broker URL", default="redis://localhost:6379/0")
    result_backend = models.CharField(max_length=255, verbose_name="Result Backend", default="redis://localhost:6379/0")
    accept_content = models.CharField(max_length=100, default="json")
    task_serializer = models.CharField(max_length=50, default="json")
    result_serializer = models.CharField(max_length=50, default="json")
    timezone = models.CharField(max_length=50, default="Europe/Paris")
    beat_schedule = models.JSONField(default=dict, blank=True, verbose_name="Beat Schedule (JSON)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration Celery"
        verbose_name_plural = "Configurations Celery"

    def __str__(self):
        return "Configuration Celery"

class RedisConfig(models.Model):
    redis_url = models.CharField(max_length=255, verbose_name="Redis URL", default="redis://localhost:6379/0")
    cache_db = models.PositiveIntegerField(default=1, verbose_name="Cache DB")
    cache_timeout = models.PositiveIntegerField(default=3600, verbose_name="Cache Timeout (s)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration Redis"
        verbose_name_plural = "Configurations Redis"

    def __str__(self):
        return "Configuration Redis"

class GlobalConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Clé")
    value = models.JSONField(verbose_name="Valeur")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Paramètre global"
        verbose_name_plural = "Paramètres globaux"

    def __str__(self):
        return f"{self.key}"

class IntegrationConfig(models.Model):
    odoo_url = models.URLField(verbose_name="URL Odoo", max_length=255)
    odoo_db = models.CharField(verbose_name="Nom base Odoo", max_length=100)
    odoo_user = models.CharField(verbose_name="Utilisateur Odoo", max_length=100)
    odoo_password = models.CharField(verbose_name="Mot de passe Odoo", max_length=100)
    notif_email_from = models.EmailField(verbose_name="Email d'envoi notifications", max_length=100)
    notif_sms_provider = models.CharField(verbose_name="Fournisseur SMS (ou config)", max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres techniques (API/Notifications)"
        verbose_name_plural = "Paramètres techniques (API/Notifications)"

    def __str__(self):
        return "Intégration/API/Notifications"

class FunctionalConfig(models.Model):
    delai_relance_inactif = models.PositiveIntegerField(verbose_name="Délai relance inactif (jours)", default=7)
    delai_relance_app_non_installee = models.PositiveIntegerField(verbose_name="Délai relance app non installée (jours)", default=3)
    dashboard_nb_jours_affichage = models.PositiveIntegerField(verbose_name="Nb jours affichés dashboard", default=30)
    dashboard_commentaires_tags = models.JSONField(verbose_name="Tags commentaires dashboard", default=list, blank=True)
    export_max_rows = models.PositiveIntegerField(verbose_name="Nb max lignes export", default=1000)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres fonctionnels/metier"
        verbose_name_plural = "Paramètres fonctionnels/metier"

    def __str__(self):
        return "Paramètres fonctionnels/metier"

class BrandingConfig(models.Model):
    site_title = models.CharField(verbose_name="Titre du site", max_length=100, default="BRASG Dashboard")
    logo_url = models.URLField(verbose_name="URL du logo", max_length=255, blank=True)
    support_contact = models.CharField(verbose_name="Contact support", max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres d'affichage/branding"
        verbose_name_plural = "Paramètres d'affichage/branding"

    def __str__(self):
        return "Branding/Affichage"

class AdvancedConfig(models.Model):
    feature_flags = models.JSONField(verbose_name="Feature flags (toggles)", default=dict, blank=True)
    maintenance_mode = models.BooleanField(verbose_name="Mode maintenance", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres avancés (technique)"
        verbose_name_plural = "Paramètres avancés (technique)"

    def __str__(self):
        return "Paramètres avancés"
