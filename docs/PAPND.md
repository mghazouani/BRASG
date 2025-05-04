# Notification automatique via Discord – Plan détaillé

## 1. Lancement manuel et planifié des synchronisations

- **Console d’administration ScrappingConsole** : permet de lancer à la demande les synchronisations suivantes :
    - `sync_BcLinbc` (commandes et lignes de commande)
    - `sync_AlimentationSolde` (alimentations de solde, notifications Discord incluses)
    - Autres types de synchronisation Odoo
- **Planification automatique** : via Celery Beat, la chaîne complète BC + alimentation peut être exécutée périodiquement sans intervention manuelle.
- **Audit automatique** : chaque synchronisation génère une entrée dans SyncLog et met à jour SyncState (date, statut, etc.)

## 2. Édition des états de synchronisation

- **SyncState** est éditable dans l’admin Django :
    - Modifier le nom, la date de dernière synchronisation (`last_sync`) ou le statut (`is_syncing`).
    - Permet de débloquer une synchro ou corriger manuellement un état bloqué.

## 3. Robustesse et traçabilité
- Correction des erreurs d’enregistrement admin (plus de doublon sur SyncState).
- Tâches Celery corrigées pour accepter tous les arguments nécessaires (`*args, **kwargs`).
- Logs et statuts visibles et rafraîchis en temps réel dans la console admin.

## 4. Procédure d’utilisation

### Lancer une synchronisation manuelle
1. Aller dans l’admin Django > ScrappingConsole > Ajouter.
2. Choisir le type de synchronisation souhaité (`sync_BcLinbc`, `sync_AlimentationSolde`, etc.).
3. Cliquer sur "Lancer maintenant".
4. Suivre le statut et les logs dans la fiche.

### Modifier un état de synchronisation
1. Aller dans l’admin Django > Sync States.
2. Cliquer sur l’état à modifier.
3. Changer la date, le nom ou le flag "is_syncing" si besoin.
4. Sauvegarder.

---

**Remarques :**
- Pour toute anomalie, consulter les logs ou contacter l’équipe technique.
- Document mis à jour le 02/05/2025 suite aux évolutions Celery/admin.

---

# Notification automatique via Discord – Plan détaillé

## Ajout d'une alimentation de solde (scraping Odoo)
- **Source** : Table Odoo `alimenteur.solde` (pas un modèle Django natif).
- **Déroulement** :
    1. **Scraper** régulièrement la table Odoo `alimenteur.solde` via XML-RPC.
    2. **Stocker** chaque entrée dans la table Django locale `AlimentationSolde`.
    3. **Détecter** les nouvelles alimentations (présentes dans Odoo mais pas encore en base locale).
    4. **Notifier** via Discord pour chaque nouvelle alimentation détectée.

## Notification Discord pour chaque nouvelle alimentation détectée

- **Déclencheur** : Lorsqu’une nouvelle entrée est insérée dans la table locale `AlimentationSolde` après scraping Odoo.
- **Données envoyées** :
    - `display_name` (nom affiché du client)
    - `reference_no` (référence unique de l’alimentation)
    - `create_date` (date de création de l’alimentation)
    - `solde` (montant crédité)
- **Message structuré (Markdown Discord, attrayant)** :

```markdown
💸 **Nouvelle alimentation détectée !**

> **Client** : `{display_name}`
> **Référence** : `{reference_no}`
> **Date** : `{date_str}`
> **Montant crédité** : **{solde} MAD**
```

- **Envoi** :
    - Utilisation d’un webhook Discord sécurisé (URL dans `.env`, variable `DISCORD_WEBHOOK_SOLDE`).
    - Requête HTTP POST vers le webhook avec le message formaté.
- **Gestion des erreurs** :
    - Si l’envoi échoue, log de l’erreur et fallback local.
- **Sécurité** :
    - Jamais d’URL du webhook dans les logs ou erreurs visibles.
    - Webhook accessible uniquement côté serveur.

---

**Exemple de code Python pour l’envoi Discord :**

```python
import os
import requests
import pytz

def send_discord_notification(obj):
    webhook_url = os.environ.get('DISCORD_WEBHOOK_SOLDE')
    if not webhook_url:
        # log erreur
        return
    # Conversion de la date à l'heure locale Maroc
    maroc_tz = pytz.timezone('Africa/Casablanca')
    create_date = obj.create_date
    if create_date.tzinfo is None or create_date.tzinfo.utcoffset(create_date) is None:
        create_date = pytz.utc.localize(create_date)
    date_maroc = create_date.astimezone(maroc_tz)
    date_str = date_maroc.strftime('%d-%m-%Y %H:%M')
    message = (
        "💸 **Nouvelle alimentation détectée !**\n\n"
        f"> **Client** : `{obj.display_name}`\n"
        f"> **Référence** : `{obj.reference_no}`\n"
        f"> **Date** : `{date_str}`\n"
        f"> **Montant crédité** : **{obj.solde} MAD**"
    )
    try:
        requests.post(webhook_url, json={'content': message})
    except Exception as e:
        # log erreur/fallback
        pass
```

---

**Résumé du flux :**
- Nouvelle alimentation détectée → création locale → notification Discord immédiate et lisible (date à l'heure du Maroc) → logs/audit côté serveur.

## Modèle Django utilisé

```python
class AlimentationSolde(models.Model):
    odoo_id = models.IntegerField(unique=True)
    client_odoo_id = models.IntegerField()
    client_nom = models.CharField(max_length=128)
    solde = models.FloatField()
    state = models.CharField(max_length=32)
    date_done = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    avoir = models.CharField(max_length=32, null=True, blank=True)
    reference_no = models.CharField(max_length=32, unique=True)
    date_creation = models.DateTimeField(null=True, blank=True)
    date_refus = models.DateTimeField(null=True, blank=True)
    refus_raisons = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=32)
    created_by = models.CharField(max_length=128, null=True, blank=True)
    display_name = models.CharField(max_length=128)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)
```

## Commande de synchronisation

- Fichier : `scrap_sga/management/commands/sync_alimentation_solde.py`
- Fonctionnement :
    - Se connecte à Odoo, récupère tous les enregistrements de `alimenteur.solde`.
    - Ignore et logue les lignes mal formées (ex : client non renseigné).
    - Insère chaque nouvelle alimentation dans la table locale.
    - Notifie Discord pour chaque nouvelle alimentation avec : client, montant, date, agent, référence.
    - Affiche dans les logs : `[NOUVEAU] Odoo id=... ref=... client=... montant=...` et `[SKIP] Odoo id=... ref=...` pour les cas ignorés.

## Admin Django

- Le modèle `AlimentationSolde` est accessible et consultable dans l’admin Django.
- Recherche, filtres, readonly, affichage optimisé pour l’audit.
- Le modèle `SyncState` est éditable dans l’admin Django (nom, date, statut).
- La ScrappingConsole permet de lancer manuellement toutes les tâches de synchronisation (y compris alimentation).

## Sécurité & bonnes pratiques
- Webhook Discord dans `.env`.
- Aucun champ modifiable dans l’admin pour AlimentationSolde (audit only).
- Tous les champs modifiables pour SyncState (gestion manuelle possible).
- Logs détaillés pour chaque opération.

## 2. Modification de la date d’écriture d’un BL (bldimagaz.bc.bl_number)
- **Déclencheur** : Quand la date d’écriture d’un bon de livraison (BL) est modifiée.
- **Action** :
    - Générer un message Discord avec :
        - Numéro du BL
        - Ancienne et nouvelle date
        - Nom du client concerné
        - Agent ayant effectué la modification
        - Raison/commentaire si fourni
    - Envoyer sur un canal Discord dédié (ex : #alertes-bl)
- **But** : Assurer la traçabilité des modifications sensibles sur les BL.

## 3. Spécifications techniques (Discord)
- Utiliser un webhook Discord (créé dans les paramètres du serveur Discord)
- Appeler le webhook via une requête HTTP POST (librairie Python : `requests` ou module natif)
- Structurer le message en Markdown ou embed Discord pour lisibilité
- Journaliser chaque envoi (succès/échec) dans un fichier ou base de données

## 4. Sécurité & gouvernance
- Stocker l’URL du webhook dans le `.env` (jamais en dur dans le code)
- Limiter l’accès à la fonction d’envoi aux actions critiques
- Prévoir un fallback (mail/log) en cas d’échec d’envoi Discord

---

### Notification Discord pour Bon de Commande (BC)

```python
maroc_tz = pytz.timezone('Africa/Casablanca')
create_date = bc_obj.create_date
if create_date.tzinfo is None or create_date.tzinfo.utcoffset(create_date) is None:
    create_date = pytz.utc.localize(create_date)
date_maroc = create_date.astimezone(maroc_tz)
date_str = date_maroc.strftime('%d-%m-%Y %H:%M')
message = (
    f"📄 **Nouvelle commande créée !**\n\n"
    f"> **Dépositaire** : `{depositaire}`\n"
    f"> **Numéro BC** : `{bc_obj.name}`\n"
    f"> **Date Création** : `{date_str}`\n"
    f"> [🔗 Voir dans ASG]({record_url}) _(connexion ASG requise)_"
)
```

- **La notification BC n'est envoyée que lors de la première création locale du BC** (pas lors des updates ou modifications).
- **La date affichée est toujours à l'heure du Maroc** (Africa/Casablanca), même si la source est UTC ou naïve.
- **Le wording du message a été harmonisé** pour une lecture claire côté Discord.

---

**Rappel : toutes les notifications Discord affichent la date à l'heure locale du Maroc, été comme hiver, et évitent tout bruit lors des updates en cascade Odoo.**