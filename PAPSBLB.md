# Plan d’Action Planifié – Synchronisation BC & Lignes BC (sync_BcLinbc)

## Objectif
Garantir une synchronisation fiable, incrémentale et performante des Bons de Commande (BC) et de leurs lignes entre Odoo et la base Django, tout en assurant la cohérence, la traçabilité et la robustesse métier.

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
     - Récupération et synchronisation des lignes associées (IDs)
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
- Utiliser uniquement odoo_id comme clé de correspondance
- Indexer tous les odoo_id pour performance
- Paginer systématiquement sur Odoo
- Limiter les champs récupérés pour optimiser le réseau
- Logger toutes les erreurs et actions majeures
- Toujours relâcher le lock même en cas d’erreur

---

## TODO / Suivi
- [x] Implémentation du modèle SyncState avec is_syncing
- [x] Refacto de la commande sync_BcLinbc pour workflow incrémental, lock et pagination
- [x] Timeout XML-RPC global
- [x] Récupération sélective des champs Odoo (fields)
- [x] Logging détaillé par BC et global + monitoring persistant (SyncLog)
- [ ] Ajout de la gestion fine des suppressions de BC (archivage, non suppression)
- [ ] Tests de robustesse et volumétrie
- [ ] Documentation technique et métier

---

**Dernière mise à jour : 2025-04-28**

Responsable : [À compléter]
