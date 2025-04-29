from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.

# --- Suppression des modèles SyncState et SyncLog car ils sont définis dans l'app scrap_sga ---
# class SyncState(models.Model):
#     """
#     Stocke l'état de synchronisation incrémentale pour chaque ressource (ex: 'bclinbc').
#     """
#     CLE_CHOICES = [
#         ('bclinbc', 'BC & Lignes BC'),
#         # Ajouter d'autres clés si besoin
#     ]
#     cle = models.CharField(max_length=50, unique=True, choices=CLE_CHOICES)
#     last_sync = models.DateTimeField(null=True, blank=True)
#     is_syncing = models.BooleanField(default=False)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.cle} (last_sync: {self.last_sync})"

#     class Meta:
#         db_table = 'scrap_sga_syncstate'

# class SyncLog(models.Model):
#     """
#     Logge chaque exécution de synchronisation (début, fin, statut, erreurs, volumétrie).
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     cle = models.CharField(max_length=50)  # Ex: 'bclinbc'
#     date_debut = models.DateTimeField(auto_now_add=True)
#     date_fin = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, default='pending')  # success, error, running
#     nb_bc = models.PositiveIntegerField(default=0)
#     nb_lignes = models.PositiveIntegerField(default=0)
#     erreurs = models.TextField(blank=True, null=True)
#     details = models.JSONField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.cle} | {self.date_debut:%Y-%m-%d %H:%M} | {self.status}"

#     class Meta:
#         db_table = 'scrap_sga_synclog'

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
    telephone2 = models.CharField(max_length=20, blank=True, null=True)
    telephone3 = models.CharField(max_length=20, blank=True, null=True)
    langue = models.CharField(max_length=20, choices=LANGUE_CHOICES)
    statut_general = models.CharField(max_length=20, choices=STATUT_CHOICES)
    notification_client = models.BooleanField(default=False)
    date_notification = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    a_demande_aide = models.BooleanField(default=False)
    nature_aide = models.TextField(null=True, blank=True)
    app_installee = models.BooleanField(null=True, blank=True)
    maj_app = models.CharField(max_length=100, null=True, blank=True)
    commentaire_agent = models.TextField(null=True, blank=True)
    segment_client = models.CharField('CMD/Jour', max_length=100, null=True, blank=True)
    ville = models.ForeignKey('core.Ville', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    region = models.CharField(max_length=100, null=True, blank=True, default="")
    canal_contact = models.CharField(max_length=100, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    relance_planifiee = models.BooleanField(default=False)
    cree_par_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='clients_crees')
    modifie_par_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='clients_modifies')

    def __str__(self):
        return f"{self.sap_id} - {self.nom_client}"

    def evaluer_actions_metier(self):
        """
        Calcule et retourne la liste des actions métier à appliquer pour ce client.
        Cette méthode doit être appelée chaque fois qu'un événement susceptible de changer la logique métier intervient (modif client, notification, etc).
        """
        actions = []
        # 1. Statut actif
        if self.statut_general == 'actif':
            pass
        # 2. Priorisation assistance (toujours prioritaire)
        if self.a_demande_aide:
            actions.append({
                "action": "planifier_assistance",
                "reason": "A demandé de l’aide, assistance à prioriser.",
                "priorite": "haute"
            })
        # 3. Suspension relance si notif succès < 1h, SAUF si demande d'aide active
        if not self.a_demande_aide:
            from django.utils import timezone
            now = timezone.now()
            derniere_notif_succes = self.notifications.filter(statut='succes').order_by('-date_notification').first()
            if derniere_notif_succes:
                delta = now - derniere_notif_succes.date_notification
                if delta.total_seconds() < 3600:
                    actions.append({
                        "action": "aucune_relance",
                        "reason": "Dernière notification avec succès il y a moins d'une heure.",
                        "priorite": "basse"
                    })
                    return actions  # On arrête la logique relance ici (sauf assistance)
        # 4. Relance si app non installée ou non à jour
        from .models import default_dashboard_settings
        settings = default_dashboard_settings()
        version_attendue = settings.get("maj_app")
        maj_app_client = str(self.maj_app).strip() if self.maj_app is not None else None
        version_attendue = str(version_attendue).strip() if version_attendue is not None else None
        if self.app_installee is not True:
            actions.append({
                "action": "notifier_client",
                "reason": "Application non installée, relance nécessaire.",
                "priorite": "normale"
            })
        elif maj_app_client != version_attendue:
            actions.append({
                "action": "notifier_client",
                "reason": f"Application installée mais version ({maj_app_client}) différente de la version attendue ({version_attendue}), relance nécessaire.",
                "priorite": "normale"
            })
        # 5. Notification à programmer si non notifié et pas de date
        if not self.notification_client and not self.date_notification:
            actions.append({
                "action": "notifier_client",
                "reason": "Notification jamais envoyée, programmation requise.",
                "priorite": "normale"
            })
        # 6. Commentaire agent à surveiller
        if self.commentaire_agent:
            mots_cles = ["besoin", "problème", "explication"]
            if any(mot in self.commentaire_agent.lower() for mot in mots_cles):
                actions.append({
                    "action": "marquer_a_suivre",
                    "reason": "Commentaire agent à surveiller (mot-clé détecté)",
                    "priorite": "haute"
                })
        # 7. Statut bloqué : suspendre relance
        if self.statut_general == "bloque":
            actions.append({
                "action": "bloquer_relance",
                "reason": "Client bloqué, suspension des relances.",
                "priorite": "haute"
            })
        return actions

    def save(self, *args, **kwargs):
        # Synchroniser la région à partir de la ville sélectionnée
        if self.ville:
            self.region = self.ville.region
        else:
            self.region = ""
        # --- RÈGLES MÉTIER AUTOMATIQUES ---
        actions = self.evaluer_actions_metier()
        # Synchronisation automatique du champ relance_planifiee
        self.relance_planifiee = any(a['action'] == 'notifier_client' for a in actions)
        # --- FIN RÈGLES MÉTIER ---
        # Audit automatique : enregistrement des changements
        is_creation = self._state.adding
        prev_instance = None
        if not is_creation:
            try:
                prev_instance = Client.objects.get(pk=self.pk)
            except Client.DoesNotExist:
                is_creation = True
        changes: dict = {}
        if prev_instance:
            import datetime
            def serialize_date(val):
                if isinstance(val, (datetime.date, datetime.datetime)):
                    return val.isoformat()
                return val
            for field in self._meta.fields:
                name = field.name
                old_val = field.value_from_object(prev_instance)
                new_val = field.value_from_object(self)
                # Convert UUID to string for JSONField
                if isinstance(old_val, uuid.UUID):
                    old_val = str(old_val)
                if isinstance(new_val, uuid.UUID):
                    new_val = str(new_val)
                old_val = serialize_date(old_val)
                new_val = serialize_date(new_val)
                if old_val != new_val:
                    changes[name] = {'old': old_val, 'new': new_val}
        super().save(*args, **kwargs)
        if actions:
            changes['actions_declenchees'] = actions
        from .models import AuditLog, User
        import logging
        logger = logging.getLogger(__name__)
        user = getattr(self, '_current_user', None)
        print(f"[AUDIT] _current_user reçu: {user} (type: {type(user)})")
        logger.warning(f"[AUDIT] _current_user reçu: {user} (type: {type(user)})")
        if user is not None and not isinstance(user, User):
            try:
                user = User.objects.get(pk=user)
            except Exception:
                user = None
        if user is not None:
            AuditLog.objects.create(
                table_name='Client',
                record_id=self.pk,
                user=user,
                action='create' if is_creation else 'update',
                champs_changes=changes
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
    target_model = models.CharField(
        max_length=20,
        choices=[('clients','Clients'),('villes','Villes')],
        default='clients'
    )
    date_import = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    resultat = models.TextField(null=True, blank=True)
    termine = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Déclenche l'import réel si le fichier vient d'être ajouté
        if self.fichier and not self.termine:
            import pandas as pd
            import numpy as np
            # modèles disponibles
            from .models import Client, Ville
            # utilitaires pour nettoyage des valeurs
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
            try:
                # chargement des données
                if self.fichier.name.endswith('.csv'):
                    df = pd.read_csv(self.fichier)
                else:
                    df = pd.read_excel(self.fichier)
                # choix du modèle cible
                if self.target_model == 'clients':
                    champs_attendus = [
                        'sap_id','nom_client','telephone','telephone2','telephone3','langue','statut_general','notification_client','date_notification',
                        'a_demande_aide','nature_aide','app_installee','maj_app','commentaire_agent','segment_client','region','ville','canal_contact','relance_planifiee'
                    ]
                elif self.target_model == 'villes':
                    champs_attendus = ['nom','latitude','longitude','pays','iso2','region']
                else:
                    self.resultat = f"Modèle d'import inconnu : {self.target_model}"
                    self.termine = True
                    super().save(update_fields=['resultat','termine'])
                    return
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
                erreurs_lignes = []
                # Champs obligatoires selon le modèle cible
                if self.target_model == 'clients':
                    champs_obligatoires = ['sap_id', 'nom_client', 'telephone']
                else:
                    champs_obligatoires = ['nom', 'latitude', 'longitude', 'pays', 'iso2', 'region']
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
                # traitement des lignes selon cible
                if self.target_model == 'clients':
                    for _, row in df.iterrows():
                        client, created_flag = Client.objects.update_or_create(
                            sap_id=safe_str(row['sap_id']),
                            defaults={
                                'nom_client': safe_str(row.get('nom_client', '')),
                                'telephone': safe_str(row.get('telephone', '')),
                                'telephone2': safe_str(row.get('telephone2', '')),
                                'telephone3': safe_str(row.get('telephone3', '')),
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
                                'ville': Ville.objects.filter(nom__iexact=safe_str(row.get('ville', ''))).first(),
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
                elif self.target_model == 'villes':
                    for _, row in df.iterrows():
                        nom = safe_str(row.get('nom',''))
                        latitude = float(row.get('latitude') or 0)
                        longitude = float(row.get('longitude') or 0)
                        pays = safe_str(row.get('pays',''))
                        iso2 = safe_str(row.get('iso2',''))
                        region = safe_str(row.get('region',''))
                        ville, flag = Ville.objects.update_or_create(
                            nom=nom,
                            defaults={
                                'latitude': latitude,
                                'longitude': longitude,
                                'pays': pays,
                                'iso2': iso2,
                                'region': region,
                            }
                        )
                        if flag:
                            created += 1
                        else:
                            updated += 1
                # résumé de l'import
                if self.target_model == 'clients':
                    self.resultat = (self.resultat or '') + f"\nImport clients terminé : {created} créés, {updated} mis à jour."
                else:
                    self.resultat = (self.resultat or '') + f"\nImport villes terminé : {created} créés, {updated} mis à jour."
                self.termine = True
            except Exception as e:
                self.resultat = f"Erreur lors de l'import : {e}"
                self.termine = True
            super().save(update_fields=["resultat", "termine"])

    def __str__(self):
        return f"Import du {self.date_import} par {self.utilisateur}"

class NotificationClient(models.Model):
    STATUT_CHOICES = [
        ('succes', 'Succès'),
        ('echec', 'Échec (injoignable)'),
    ]
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='notifications')
    utilisateur = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    date_notification = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    canal = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.client} - {self.get_statut_display()} le {self.date_notification:%Y-%m-%d %H:%M}"

# Signal : mise à jour automatique du champ date_notification ET notification_client du Client après chaque notification
@receiver(post_save, sender=NotificationClient)
def update_client_notification_fields(sender, instance, created, **kwargs):
    if instance.client:
        # 1. Mettre à jour la date de notification si création
        if created:
            instance.client.date_notification = instance.date_notification  # Garder date + heure
        # 2. Mettre à jour notification_client selon la logique métier
        has_success = instance.client.notifications.filter(statut='succes').exists()
        instance.client.notification_client = has_success
        # Correction : on force un full save pour déclencher toute la logique métier
        instance.client.save()  # NE PAS utiliser update_fields pour déclencher evaluer_actions_metier et la vérification <1h
        # 3. Recalculer toutes les actions métier à jour (optionnel, déjà fait dans save())
        # actions = instance.client.evaluer_actions_metier()

# BONUS : si une notification est supprimée, on vérifie si notification_client doit être mis à jour
@receiver(post_delete, sender=NotificationClient)
def update_client_notification_fields_on_delete(sender, instance, **kwargs):
    if instance.client:
        has_success = instance.client.notifications.filter(statut='succes').exists()
        instance.client.notification_client = has_success
        instance.client.save(update_fields=["notification_client"])

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
