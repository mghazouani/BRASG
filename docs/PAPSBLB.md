# Plan d’Action Planifié – Synchronisation BC & Lignes BC (sync_BcLinbc)

## Objectif
Garantir une synchronisation fiable, incrémentale et performante des Bons de Commande (BC) et de leurs lignes entre Odoo et la base Django, tout en assurant la cohérence, la traçabilité et la robustesse métier.

---

## Dernières évolutions (avril 2025)

- Correction de la logique de jointure pour la récupération du dernier BC en backend : la correspondance se fait désormais via `sap_id` (client/user) et `odoo_id` (user/BC), selon la clé métier réellement utilisée côté Odoo et Django.
- Ajout d’un champ calculé `last_bc_info` dans l’API client pour exposer le dernier BC créé (nom + date) dans le dashboard, basé sur la synchronisation.
- Harmonisation des logs : chaque synchro génère une entrée détaillée dans SyncLog, et chaque modification côté client est tracée dans AuditLog (audit métier).
- Vérification stricte de la cohérence des clés métiers (pas de mélange entre `id`, `odoo_id`, `sap_id`).
- Correction du mapping des champs lors de la synchronisation (suppression des champs non existants, utilisation stricte des clés Odoo).
- Amélioration de la robustesse du workflow (gestion fine du lock, relâchement systématique même en cas d’erreur, monitoring persistant).
- Harmonisation de la logique métier backend/SQL/API pour garantir que la donnée affichée dans le dashboard est toujours issue de la dernière synchro Odoo.

---

## Étapes clés du workflow

1. **Connexion Odoo**
   - Connexion XML-RPC sécurisée à Odoo
   - Timeout global appliqué (30s) pour éviter les blocages
   - Authentification utilisateur (récupération uid)

2. **Gestion du lock de synchronisation**
   - Nouveau champ `is_syncing` dans SyncState pour éviter les collisions multi-jobs
   - Si une synchro est en cours, la commande s’arrête immédiatement
   - Le flag est remis à False en toute fin de synchro (même en cas d’erreur)

3. **Gestion du last_sync (incrémental)**
   - Modèle SyncState (clé 'bclinbc') pour stocker la date de dernière synchro
   - Lecture/incrémentation de last_sync à chaque exécution
   - now_sync fixé en début de synchro pour cohérence transactionnelle

4. **Récupération incrémentale et paginée des BC**
   - Utilisation de search_read paginé côté Odoo (limit/offset)
   - Récupération uniquement des champs nécessaires (fields explicites)
   - Aucun risque de surcharge mémoire, même avec >10 000 BC

5. **Synchronisation des BC**
   - Pour chaque BC :
     - Transaction atomique (rollback automatique en cas d’erreur)
     - update_or_create sur odoo_id
     - Mapping complet des champs métier (logique existante conservée)
     - Suppression sélective des lignes orphelines locales
     - Logging/audit métier détaillé

6. **Gestion des suppressions**
   - Suppression locale des lignes BC absentes d’Odoo pour chaque BC traité
   - (Optionnel) Suppression ou archivage des BC absents d’Odoo (non modifié dans cette itération)

7. **Gestion des erreurs**
   - try/except autour de chaque BC pour ne pas bloquer la synchro globale
   - Logging détaillé des erreurs par BC
   - Timeout XML-RPC géré

8. **Mise à jour du last_sync**
   - Si la synchro s’est déroulée sans erreur majeure, mise à jour de SyncState (clé 'bclinbc') avec now_sync

9. **Logs et monitoring persistant**
   - Nouveau modèle SyncLog : chaque exécution de synchro est tracée (début, fin, statut, erreurs, nombre de BC/lignes traités)
   - Toutes les erreurs critiques sont enregistrées dans la base
   - (Optionnel) Possibilité d’alerte email ou dashboard de suivi

---

## Bonnes pratiques
- Utiliser uniquement odoo_id comme clé de correspondance pour les BC et lignes BC.
- Vérifier la cohérence entre les clés métiers utilisées côté Odoo et Django (`sap_id`, `odoo_id`, `id`).
- Indexer tous les odoo_id pour performance.
- Paginer systématiquement sur Odoo.
- Limiter les champs récupérés pour optimiser le réseau.
- Logger toutes les erreurs et actions majeures.
- Toujours relâcher le lock même en cas d’erreur.
- Ne jamais utiliser de champ Odoo non présent dans le modèle cible.
- Toujours vérifier la cohérence des clés utilisées pour les lignes BC.
- Utiliser l’option `--reset` pour forcer une synchro globale complète si besoin.
- Pour afficher le nom produit d’une ligne BC, passer par la relation `product` côté Django.

---

## Axes d'amélioration

1. **Manque d'un vrai Lock de synchronisation**
   - Si deux jobs Django démarrent simultanément, il existe un risque de collision sur SyncState ou de conflits en base.
   - **Suggestion** : implémenter un flag temporaire `is_syncing` (local DB), à poser et relâcher systématiquement pour garantir l'exclusivité de la synchro.

2. **Timeout XML-RPC pas configuré**
   - En l'absence de timeout, un serveur Odoo lent peut bloquer la synchro indéfiniment.
   - **Suggestion** : utiliser un timeout global Python (ex : `socket.setdefaulttimeout(30)`) ou un transport personnalisé pour chaque appel XML-RPC.

3. **Pas de récupération sélective des champs**
   - L'appel `read` sans filtrer les fields charge potentiellement tous les champs, y compris les blobs/binaire si Odoo évolue.
   - **Suggestion** : toujours préciser la liste exacte des fields nécessaires (ex : `fields = ['name', 'fullname', 'bc_date', ...]`).

4. **Pas de contrôle de volume en cas d’explosion**
   - Si la recherche retourne un volume massif (ex : 10 000 BC), la gestion mémoire peut devenir critique.
   - **Suggestion** : privilégier la pagination native via `search_read` côté Odoo plutôt qu'un search global suivi d'un read.

5. **Pas de monitoring distant ou persisté**
   - Le script log uniquement en console, donc perte d'information en cas de cron ou plantage.
   - **Suggestion** : ajouter une table `SyncLog` (date, résultat, erreurs) ou configurer l'envoi d'alertes (ex : `mail_admins` Django) en cas d'échec.

---

## TODO / Suivi
- [x] Correction de la logique de jointure et du mapping des clés métiers (sap_id, odoo_id, id).
- [x] Ajout du champ calculé `last_bc_info` dans l’API client pour le dashboard.
- [x] Harmonisation des logs (SyncLog, AuditLog).
- [x] Refacto de la commande sync_BcLinbc pour workflow incrémental, lock et pagination.
- [x] Timeout XML-RPC global.
- [x] Récupération sélective des champs Odoo (fields).
- [x] Logging détaillé par BC et global + monitoring persistant (SyncLog).
- [x] Correction de la synchronisation des lignes BC (clé correcte, suppression du champ inexistant 'product_name').
- [x] Ajout de l’option --reset pour forcer une synchro globale.
- [ ] Ajout de la gestion fine des suppressions de BC (archivage, non suppression).
- [ ] Tests de robustesse et volumétrie.
- [ ] Documentation technique et métier.

---

**Dernière mise à jour : 2025-04-29**

Responsable : [À compléter]
