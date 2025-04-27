# Suivi des tâches - Projet Scrap AGS

Ce document sera mis à jour après chaque modification ou étape technique importante.

## Journal des tâches

- [x] Création de l’app Django `scrap_sga` (backend BRASG)  
  → App créée à zéro (structure Django standard, prête à l’emploi)
- [x] Définition des modèles `scrap_dimagaz_bc`, `scrap_dimagaz_bc_line` et `scrap_product`  
  → Modèles créés avec champs typés, clé unique Odoo, FK robuste, mapping produit Odoo
- [x] Création des migrations/tables  
  → Migrations générées et appliquées, tables physiques prêtes
- [x] Développement du script/commande de synchronisation Odoo → Django  
  → Commande `sync_BcLinbc` créée (anti-doublon, upsert, clé unique Odoo, FK, logs, arrondi montants, filtre par name, mapping produit, bc_date, suppression tracée, **scrap partiel fiable avec --date, suppression locale corrigée**)
- [x] Synchronisation des produits Odoo (`scrap_product`)  
  → Commande `sync_products` fonctionnelle, mapping complet, FK sur les lignes BC, suppression tracée
- [x] Admin Django enrichi  
  → Affichage FK produit, bc_date, filtres améliorés sur les lignes BC et produits
- [x] Scrap/synchronisation des autres tables Odoo (fournisseurs, users, centres, etc.)  
  → Commandes dédiées (`sync_user`, `sync_products`, `sync_fournisseurs`, `sync_centres`, etc.), mapping Odoo → Django, cohérence des FK. **Attention : les tables doivent être scrapées dans l'ordre suivant pour garantir l'intégrité des clés étrangères et des dépendances : 1) user, 2) product, 3) fournisseur, 4) centre, 5) bc, 6) bc.line.**
- [x] Mise en place de l’audit log (historique des changements sur toutes les tables synchronisées, déclenché par synchro et admin, modèle dédié AuditLog)
  → Traçabilité fine : création, modification (diff avant/après), suppression (snapshot avant delete), visualisation dans l’admin Django, recherche/filtres/JSON
- [x] **Correction majeure : scrap partiel (--date) fiable, suppression locale des lignes BC corrigée.**
- [x] Planification de la tâche automatique (toutes les 1 minute via Celery Beat)
  → Celery + Redis configurés, tâche `sync_bc_linbc_task` exécutée toutes les minutes, logs visibles dans le worker, robustesse Windows/Linux assurée (pool=solo sous Windows)
- [x] Correction de la synchro des lignes BC :
  → À chaque BC importé, toutes les lignes associées sont créées/mises à jour (update_or_create) ; suppression locale sélective seulement des lignes absentes d’Odoo pour le BC traité. Plus aucun risque de perte de lignes lors d’un scrap partiel ou d’une table vide.
- [ ] Exposition des données via API DRF
- [ ] Mécanisme de relance/résynchronisation en cas d’échec

Chaque étape sera cochée et détaillée au fur et à mesure de l’avancement.

---

**Dernière action :**
- Synchro BC/lines 100% fiable : insertion des lignes BC rétablie, suppression sélective OK, scrap partiel (--date) et scrap complet robustes.
- Planification Celery Beat passée à 1 minute.
