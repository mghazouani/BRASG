# Plan d’Action – Gouvernance des Paramètres Globaux (GeneralConfig)

Ce document détaille la gestion centralisée des paramètres globaux de BRASG via l’admin Django. Il structure les catégories de paramètres, explique leur usage, et fournit des exemples pour chaque cas d’usage métier ou technique.

---

## 1. Paramètres techniques d’intégration
### API externes
- **odoo_url** : URL de l’instance Odoo cible
  - *Exemple* : `https://odoo.monsite.com`
  - *Usage* : Permet de connecter le backend à l’ERP Odoo pour la synchronisation.
- **odoo_db** : nom de la base Odoo
  - *Exemple* : `brasg_prod`
  - *Usage* : Sélection de la base Odoo cible lors des appels API.
- **odoo_user** : login technique Odoo
  - *Exemple* : `api_user`
  - *Usage* : Authentification technique sur l’API Odoo.
- **odoo_password** : mot de passe technique Odoo
  - *Exemple* : `********`
  - *Usage* : Authentification technique sur l’API Odoo.

### Notifications
- **notif_email_from** : adresse email d’envoi des notifications
  - *Exemple* : `noreply@brasg.com`
  - *Usage* : Expéditeur des emails envoyés aux clients/utilisateurs.
- **notif_sms_provider** : nom ou paramètres du fournisseur SMS
  - *Exemple* : `"twilio"` ou `{ "provider": "orange", "api_key": "..." }`
  - *Usage* : Configuration dynamique du canal SMS.

---

## 2. Paramètres de file d’attente et cache
### Celery
- **celery_broker_url** : URL du broker
  - *Exemple* : `redis://localhost:6379/0`
  - *Usage* : Permet à Celery de communiquer avec le backend via Redis ou RabbitMQ.
- **celery_result_backend** : backend de résultat
  - *Exemple* : `redis://localhost:6379/1`
  - *Usage* : Stockage des résultats de tâches Celery.
- **celery_task_soft_time_limit** : durée max (sec) avant interruption douce d’une tâche
  - *Exemple* : `300`
- **celery_task_hard_time_limit** : durée max (sec) avant kill forcé d’une tâche
  - *Exemple* : `600`

### Redis
- **redis_url** : URL de connexion Redis
  - *Exemple* : `redis://localhost:6379/0`
- **redis_cache_db** : numéro de base Redis pour le cache
  - *Exemple* : `1`
- **redis_cache_timeout** : durée (sec) de vie des entrées cache
  - *Exemple* : `3600`

---

## 3. Paramètres fonctionnels/métier
### Délais et relances
- **delai_relance_inactif** : délai (jours) avant relance d’un client inactif
  - *Exemple* : `7`
- **delai_relance_app_non_installee** : délai avant relance si l’app n’est pas installée
  - *Exemple* : `3`

### Comportement Dashboard
- **dashboard_nb_jours_affichage** : nb de jours affichés par défaut
  - *Exemple* : `30`
- **dashboard_commentaires_tags** : tags prédéfinis pour les commentaires
  - *Exemple* : `["besoin", "problème", "explication"]`

### Export
- **export_max_rows** : nombre max de lignes exportables
  - *Exemple* : `1000`

---

## 4. Paramètres d’affichage/branding
- **site_title** : titre affiché en haut du dashboard
  - *Exemple* : `BRASG Dashboard`
- **logo_url** : URL du logo personnalisé
  - *Exemple* : `https://brasg.com/static/logo.png`
- **support_contact** : email ou téléphone support
  - *Exemple* : `support@brasg.com` ou `+33 1 23 45 67 89`

---

## 5. Paramètres avancés (pour admins techniques)
- **feature_flags** : toggles pour activer/désactiver des fonctionnalités
  - *Exemple* : `{ "export_csv": true, "sync_auto": false }`
- **maintenance_mode** : activer le mode maintenance
  - *Exemple* : `true`

---

## 6. Paramètres globaux complémentaires (hors installation Django)
### Sécurité applicative
- **password_policy** : politique de mot de passe
  - *Exemple* : `{ "min_length": 8, "require_digit": true, "expire_days": 90 }`
- **session_timeout_minutes** : durée max d’inactivité
  - *Exemple* : `30`
- **max_login_attempts** : tentatives max avant blocage
  - *Exemple* : `5`

### Personnalisation utilisateur
- **default_language** : langue par défaut
  - *Exemple* : `fr`
- **user_can_change_theme** : autoriser changement de thème
  - *Exemple* : `true`
- **available_themes** : thèmes disponibles
  - *Exemple* : `["clair", "sombre"]`

### Gestion documentaire
- **max_upload_size_mb** : taille max upload (Mo)
  - *Exemple* : `10`
- **allowed_upload_types** : extensions autorisées
  - *Exemple* : `["pdf", "jpg", "png"]`
- **retention_period_days** : durée de conservation des documents
  - *Exemple* : `365`

### Communication
- **email_signature** : signature des emails
  - *Exemple* : `L’équipe BRASG`
- **support_hours** : horaires support
  - *Exemple* : `"9h-18h, lundi-vendredi"`

### Monitoring/alertes
- **alert_email_list** : emails à notifier en cas d’erreur
  - *Exemple* : `["admin@brasg.com"]`
- **enable_error_reporting** : activer la remontée d’erreurs
  - *Exemple* : `true`

### Quotas/limites
- **max_clients_per_user** : max de clients par utilisateur
  - *Exemple* : `100`
- **max_notifications_per_day** : max de notifications/jour
  - *Exemple* : `500`

---

## Critères pour ajouter un paramètre dans GeneralConfig
- Il doit pouvoir être modifié sans redéployer ni reconfigurer le serveur.
- Il ne doit pas dépendre d’un chemin système, d’un secret critique, ni d’une config Django interne (pour cela, privilégier `.env` ou `settings.py`).
- Il doit être utile pour ajuster dynamiquement le comportement métier, l’expérience utilisateur, ou la sécurité de l’application.

---

## Actions à planifier
1. **Script d’import initial** : automatiser la création des paramètres de base dans la base de données.
2. **Lecture dynamique** : intégrer dans le code Python une logique pour lire ces paramètres depuis la base (remplacement progressif des constantes dans le code).
3. **Sécurisation** : définir qui peut éditer ces paramètres dans l’admin Django (groupes, permissions).
4. **Documentation** : maintenir ce fichier à jour à chaque ajout/modification de paramètre global.