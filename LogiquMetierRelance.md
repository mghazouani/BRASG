# Logique Métier de la Relance Client

## 1. Vue d’ensemble
Cette documentation décrit en détail la logique métier de la gestion des relances clients, telle qu’implémentée dans le projet (backend Django, frontend React/Next.js, et synchronisation BDD). Elle explique le fonctionnement automatique des relances, les cas d’exception, la synchronisation des champs calculés, ainsi que les interactions entre les différentes couches de l’application.

---

## 2. Logique Métier (Backend & BDD)

### a) Règles Principales
- **Relance planifiée** (`relance_planifiee`) :
  - Ce champ booléen est automatiquement synchronisé à chaque modification du client.
  - Il est à `True` si une action métier de type `notifier_client` est requise (application non installée ou version non conforme).
  - Il est à `False` sinon.

- **Suspension de la relance** :
  - Si une notification de succès a été envoyée il y a moins d’1h, la relance est suspendue (aucune relance n’est affichée ni planifiée).
  - **Exception** : Si une demande d’aide (`a_demande_aide`) est active, l’assistance reste prioritaire et la suspension de relance ne s’applique pas.

- **Mise à jour automatique** :
  - À chaque sauvegarde d’un client (`save()`), la méthode `evaluer_actions_metier()` est appelée pour recalculer toutes les actions métier et synchroniser le champ `relance_planifiee`.
  - Lorsqu’une notification est ajoutée via le frontend, le signal `post_save` sur `NotificationClient` force un `save()` complet du client, déclenchant ainsi la logique métier complète.

### b) Synchronisation BDD
- Le champ `relance_planifiee` est calculé côté backend et stocké en base, garantissant la cohérence des KPI, filtres et exports.
- Le frontend ne modifie jamais ce champ directement.

---

## 3. Logique Frontend
- Le frontend affiche l’état de la relance, de la notification et de l’assistance en fonction des champs renvoyés par l’API.
- Lorsqu’une notification est créée via la modale, le backend met à jour automatiquement la logique métier : le frontend n’a qu’à rafraîchir les données du client pour obtenir l’état à jour.
- Le formulaire d’édition client (`ClientEditForm`) et l’édition inline déclenchent la logique métier via l’API, qui applique toutes les règles côté backend.

---

## 4. Cas d’utilisation

### Cas 1 : Application non installée
- **Situation** : `app_installee = False`, version attendue peu importe.
- **Résultat** :
  - Action `notifier_client` générée.
  - `relance_planifiee = True`.
  - Relance affichée côté frontend.

### Cas 2 : Application installée mais version non conforme
- **Situation** : `app_installee = True`, `maj_app` ≠ version attendue.
- **Résultat** :
  - Action `notifier_client` générée.
  - `relance_planifiee = True`.
  - Relance affichée côté frontend.

### Cas 3 : Application installée et à jour
- **Situation** : `app_installee = True`, `maj_app` == version attendue.
- **Résultat** :
  - Aucune action de relance.
  - `relance_planifiee = False`.

### Cas 4 : Notification de succès il y a moins d’1h
- **Situation** : Dernière notification de succès < 1h, pas de demande d’aide.
- **Résultat** :
  - Action `aucune_relance` générée.
  - `relance_planifiee = False`.
  - La relance disparaît côté frontend.

### Cas 5 : Demande d’aide active
- **Situation** : `a_demande_aide = True`, notification récente ou non.
- **Résultat** :
  - Action `planifier_assistance` générée (toujours prioritaire).
  - La suspension de relance ne bloque pas l’assistance.

### Cas 6 : Ajout d’une notification via le frontend
- **Situation** : Une notification de succès est ajoutée via la modale.
- **Résultat** :
  - Le signal backend met à jour la date et le statut de notification du client.
  - Un `save()` complet est déclenché, la logique métier est réévaluée, la suspension de relance fonctionne immédiatement.
  - Le frontend n’a qu’à rafraîchir la fiche client pour voir la relance disparaître.

---

## 5. Points de vigilance
- Toujours laisser le backend gérer la logique métier : ne jamais modifier `relance_planifiee` côté frontend.
- Toute modification du client ou ajout de notification déclenche automatiquement la réévaluation des actions métier.
- Les KPI et exports sont fiables car basés sur la donnée calculée en base.

---

## 6. Schéma de flux (résumé)

1. **Modification client** (formulaire ou import) → `save()` → `evaluer_actions_metier()` → mise à jour automatique de `relance_planifiee`.
2. **Ajout notification** (modale frontend) → signal `post_save` → mise à jour client + `save()` → logique métier complète exécutée.
3. **Frontend** : affiche toujours l’état réel, sans logique métier locale.

---

**Auteur :** Cascade AI — Documentation générée automatiquement (2025-04-26)
