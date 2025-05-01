# Plan d'Action - Projet "Scrap AGS"

Ce document sera rempli au fur et à mesure de nos échanges, pour cadrer et planifier toutes les étapes du développement.

## 1. Objectif fonctionnel
Récupérer en lecture seule des champs bien précis dans Odoo et les stocker dans la base locale pour une éventuelle utilisation (analyse, reporting, automatisation, etc.).

## 2. Cible technique
- Utilisation du backend existant du projet BRASG (Django).
- Nouvelle app Django nommée `scrap_sga`, visible uniquement depuis le backend.
- Les données scrapées seront exposées via API pour le frontend BRASG.
- Utilisation des tables existantes + création de nouvelles tables pour cette app, préfixées par `scrap_`.

## 3. Flux attendu
- Synchronisation automatique toutes les 5 minutes.
- Gestion d’historique (audit log) pour chaque import.
- Pas de notifications pour l’instant.
- Prévoir un mécanisme pour relancer/résynchroniser certains objets en cas d’échec.
- Pas de contrainte de volumétrie identifiée pour l’instant.

## 4. Mapping des données
- Modèles Odoo concernés : `dimagaz.bc` et `dimagaz.bc.line`.
- Tous les champs de ces modèles seront synchronisés (copie complète, pas de conversion ni calcul pour l’instant).
- Création de deux nouvelles tables Django : `scrap_dimagaz_bc` et `scrap_dimagaz_bc_line`.
- Pas de correspondance avec des tables existantes pour l’instant, simple copie table à table.

## 5. Planification des étapes
1. Création de l’app Django `scrap_sga` (backend BRASG)
2. Définition des modèles `scrap_dimagaz_bc` et `scrap_dimagaz_bc_line` (copie brute des champs Odoo)
3. Création des migrations/tables
4. Développement d’un script/commande de synchronisation Odoo → Django
   - Attention : éviter absolument les doublons lors de l’import
   - Mécanismes anti-doublon à mettre en place :
     - Utilisation de l’ID Odoo comme clé unique (`unique=True`) dans les modèles Django
     - Upsert (update-or-create) systématique sur la base de l’ID Odoo
     - Optionnel : verrouillage transactionnel lors de l’import
     - Optionnel : indexation DB sur les champs uniques pour garantir l’unicité
     - Nettoyage automatique des doublons éventuels (script de contrôle)
     - Audit log de chaque import/modification
5. Mise en place de l’audit log pour chaque import
6. Planification de la tâche automatique (toutes les 1 minutes)
7. Exposition des données via API DRF pour le frontend
8. Mécanisme de relance/résynchronisation en cas d’échec

**Remarque :**
- Le mécanisme le plus fiable pour garantir zéro doublon est d’imposer une contrainte d’unicité sur l’ID Odoo dans chaque table, et d’utiliser systématiquement un upsert (`update_or_create` en Django) lors de chaque import. Cela garantit qu’aucune ligne n’est dupliquée, même en cas de relance ou de synchronisation partielle/interrompue.

---

Je vais maintenant te proposer la planification détaillée et le découpage des tâches pour le développement.

Si tu valides ce plan, je commence la création de l’app et des modèles avec gestion anti-doublon robuste.

**Mise à jour :**
- L’app Django `scrap_sga` a été recréée à zéro (structure propre, prête pour les modèles).
