# Suivi des tâches - Projet Scrap AGS

Ce document sera mis à jour après chaque modification ou étape technique importante.

## Journal des tâches

- [x] Création de l’app Django `scrap_sga` (backend BRASG)  
  → App créée à zéro (structure Django standard, prête à l’emploi)
- [x] Définition des modèles `scrap_dimagaz_bc` et `scrap_dimagaz_bc_line`  
  → Modèles créés avec champs typés, clé unique Odoo, FK robuste
- [x] Création des migrations/tables  
  → Migrations générées et appliquées, tables physiques prêtes
- [x] Développement du script/commande de synchronisation Odoo → Django  
  → Commande `sync_odoo` créée (anti-doublon, upsert, clé unique Odoo, FK, logs)
- [ ] Mise en place de l’audit log
- [ ] Planification de la tâche automatique (toutes les 5 minutes)
- [ ] Exposition des données via API DRF
- [ ] Mécanisme de relance/résynchronisation en cas d’échec

Chaque étape sera cochée et détaillée au fur et à mesure de l’avancement.

---

**Dernière action :** Initialisation du suivi des tâches.
