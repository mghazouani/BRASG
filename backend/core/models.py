from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('agent', 'Agent'), ('superviseur', 'Superviseur')], default='agent')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    image_profil = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

class Client(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('bloque', 'Bloqué'),
    ]
    LANGUE_CHOICES = [
        ('arabe', 'Arabe'),
        ('francais', 'Français'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sap_id = models.CharField(max_length=50, unique=True)
    nom_client = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    langue = models.CharField(max_length=20, choices=LANGUE_CHOICES)
    statut_general = models.CharField(max_length=20, choices=STATUT_CHOICES)
    notification_client = models.BooleanField(default=False)
    date_notification = models.DateField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    a_demande_aide = models.BooleanField(default=False)
    nature_aide = models.TextField(null=True, blank=True)
    app_installee = models.BooleanField(null=True, blank=True)
    maj_app = models.CharField(max_length=100, null=True, blank=True)
    commentaire_agent = models.TextField(null=True, blank=True)
    segment_client = models.CharField('CMD/Jour', max_length=100, null=True, blank=True)
    ville = models.ForeignKey('core.Ville', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    region = models.CharField(max_length=100, null=True, blank=True)
    canal_contact = models.CharField(max_length=100, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    relance_planifiee = models.BooleanField(default=False)
    cree_par_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='clients_crees')
    modifie_par_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='clients_modifies')

    def __str__(self):
        return f"{self.sap_id} - {self.nom_client}"

    def save(self, *args, **kwargs):
        # Synchroniser la région à partir de la ville sélectionnée
        if self.ville:
            self.region = self.ville.region
        else:
            self.region = None
        # --- RÈGLES MÉTIER AUTOMATIQUES ---
        actions = []
        # 1. Statut actif
        if self.statut_general == 'actif':
            pass  # Client actif
        # 2. Priorisation assistance
        if self.a_demande_aide:
            actions.append({
                "action": "planifier_assistance",
                "reason": "A demandé de l’aide, assistance à prioriser.",
                "priorite": "haute"
            })
        # 3. Relance si app non installée ou non à jour
        if not self.app_installee or (self.maj_app and self.maj_app.lower() != 'à jour'):
            actions.append({
                "action": "notifier_client",
                "reason": "Application non installée ou non à jour, relance nécessaire.",
                "priorite": "normale"
            })
        # 4. Notification à programmer si non notifié et pas de date
        if not self.notification_client and not self.date_notification:
            actions.append({
                "action": "notifier_client",
                "reason": "Notification jamais envoyée, programmation requise.",
                "priorite": "normale"
            })
        # 5. Commentaire agent à surveiller
        if self.commentaire_agent:
            mots_cles = ["besoin", "problème", "explication"]
            if any(mot in self.commentaire_agent.lower() for mot in mots_cles):
                actions.append({
                    "action": "marquer_a_suivre",
                    "reason": "Commentaire agent à surveiller (mot-clé détecté)",
                    "priorite": "haute"
                })
        # 6. Statut inactif/bloqué : suspendre relance
        if self.statut_general in ["inactif", "bloque"]:
            actions.append({
                "action": "bloquer_relance",
                "reason": "Client inactif ou bloqué, suspension des relances.",
                "priorite": "haute"
            })
        # --- FIN RÈGLES MÉTIER ---
        super().save(*args, **kwargs)
        # Audit automatique
        from .models import AuditLog, User
        import inspect
        user = getattr(self, '_current_user', None)
        AuditLog.objects.create(
            table_name='Client',
            record_id=self.id,
            user=user,
            action='update' if self.pk else 'create',
            champs_changes={'actions_declenchees': actions}
        )

class Ville(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pays = models.CharField(max_length=100)
    iso2 = models.CharField(max_length=2)
    region = models.CharField(max_length=100)

    class Meta:
        db_table = 'core_ville'
        verbose_name = 'Ville'
        verbose_name_plural = 'Villes'

    def __str__(self):
        return self.nom

class ImportFichier(models.Model):
    fichier = models.FileField(upload_to='imports_clients/')
    date_import = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    resultat = models.TextField(null=True, blank=True)
    termine = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Déclenche l'import réel si le fichier vient d'être ajouté
        if self.fichier and not self.termine:
            import pandas as pd
            from .models import Client
            try:
                champs_attendus = [
                    'sap_id','nom_client','telephone','langue','statut_general','notification_client','date_notification',
                    'a_demande_aide','nature_aide','app_installee','maj_app','commentaire_agent','segment_client','region','ville','canal_contact','relance_planifiee'
                ]
                if self.fichier.name.endswith('.csv'):
                    df = pd.read_csv(self.fichier)
                else:
                    df = pd.read_excel(self.fichier)
                # Validation stricte de l'en-tête
                missing = [col for col in champs_attendus if col not in df.columns]
                extra = [col for col in df.columns if col not in champs_attendus]
                if missing:
                    self.resultat = f"Erreur : Colonnes manquantes dans l'en-tête : {', '.join(missing)}"
                    self.termine = True
                    super().save(update_fields=["resultat", "termine"])
                    return
                if extra:
                    self.resultat = f"Avertissement : Colonnes inconnues ignorées : {', '.join(extra)}"
                import numpy as np
                def safe_str(val, default=''):
                    if pd.isna(val):
                        return default
                    return str(val)
                def safe_bool(val):
                    if pd.isna(val):
                        return False
                    if isinstance(val, bool):
                        return val
                    return str(val).strip().lower() in ['true','1','oui','vrai','yes']
                erreurs_lignes = []
                champs_obligatoires = ['sap_id', 'nom_client', 'telephone']
                # Prévalidation de toutes les lignes
                for idx, row in df.iterrows():
                    champs_vides = [champ for champ in champs_obligatoires if not safe_str(row.get(champ, '')).strip()]
                    if champs_vides:
                        erreurs_lignes.append(f"Ligne {idx+2} : champs obligatoires vides : {', '.join(champs_vides)}")
                if erreurs_lignes:
                    self.resultat = (self.resultat or '') + '\nImport annulé :\n' + '\n'.join(erreurs_lignes)
                    self.termine = True
                    super().save(update_fields=["resultat", "termine"])
                    return
                created, updated = 0, 0
                for _, row in df.iterrows():
                    client, created_flag = Client.objects.update_or_create(
                        sap_id=safe_str(row['sap_id']),
                        defaults={
                            'nom_client': safe_str(row.get('nom_client', '')),
                            'telephone': safe_str(row.get('telephone', '')),
                            'langue': safe_str(row.get('langue', 'francais')).lower() if safe_str(row.get('langue', '')) else 'francais',
                            'statut_general': safe_str(row.get('statut_general', 'actif')).lower() if safe_str(row.get('statut_general', '')) else 'actif',
                            'notification_client': safe_bool(row.get('notification_client', False)),
                            'date_notification': safe_str(row.get('date_notification', None)) or None,
                            'a_demande_aide': safe_bool(row.get('a_demande_aide', False)),
                            'nature_aide': safe_str(row.get('nature_aide', '')),
                            'app_installee': safe_bool(row.get('app_installee', False)),
                            'maj_app': safe_str(row.get('maj_app', '')),
                            'commentaire_agent': safe_str(row.get('commentaire_agent', '')),
                            'segment_client': safe_str(row.get('segment_client', '')),
                            'ville': safe_str(row.get('ville', '')),
                            'canal_contact': safe_str(row.get('canal_contact', '')),
                            'relance_planifiee': safe_bool(row.get('relance_planifiee', False)),
                            'cree_par_user': self.utilisateur,
                            'modifie_par_user': self.utilisateur,
                        }
                    )
                    client._current_user = self.utilisateur
                    client.save()
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                if not extra:
                    self.resultat = (self.resultat or '') + f"\nImport terminé : {created} créés, {updated} mis à jour."
                else:
                    self.resultat += f"\nImport terminé : {created} créés, {updated} mis à jour."
                self.termine = True
            except Exception as e:
                self.resultat = f"Erreur lors de l'import : {e}"
                self.termine = True
            super().save(update_fields=["resultat", "termine"])

    def __str__(self):
        return f"Import du {self.date_import} par {self.utilisateur}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_name = models.CharField(max_length=100)
    record_id = models.UUIDField()
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    champs_changes = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.table_name} - {self.action} par {self.user} le {self.timestamp}"

def default_dashboard_settings():
    return {
        "statut_general": [
            {"value": "actif", "label": "Actif"},
            {"value": "inactif", "label": "Inactif"},
            {"value": "bloque", "label": "Bloqué"},
        ],
        "langue": [
            {"value": "arabe", "label": "Arabe"},
            {"value": "francais", "label": "Français"},
        ],
        "notification_client": [
            {"value": True, "label": "Notifié"},
            {"value": False, "label": "Non notifié"},
        ],
        "a_demande_aide": [
            {"value": True, "label": "Oui"},
            {"value": False, "label": "Non"},
        ],
        "app_installee": [
            {"value": True, "label": "Oui"},
            {"value": False, "label": "Non"},
        ],
        "maj_app": ""
    }

class DashboardConfig(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    settings = models.JSONField(default=default_dashboard_settings)

    class Meta:
        verbose_name = "Configuration du Dashboard"
        verbose_name_plural = "Configurations du Dashboard"

    def __str__(self):
        return "Configuration du Dashboard"
