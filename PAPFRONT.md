# DASHBOARD FRONTEND

## Priorisation des tâches (détail, priorité, complexité)

### 1. Ajout de filtres sur dashboard : commentaires
- **Description** : Permettre de filtrer les éléments du dashboard selon les mots-clés, tags ou contenus présents dans les commentaires clients/agents.
Exemple :GitHub : Combinaison de labels prédéfinis (ex : bug) et de tags personnalisés.

- **Priorité** : Haute
- **Complexité** : Faible à modérée (si les champs sont déjà exposés côté backend)
- **Détails** :
  - Ajout d’un champ de recherche ou de sélection multiple (dropdown/tags) dans l’UI du dashboard.
  - Filtrage dynamique côté front (et/ou requête API filtrée côté back).
  - UX : Affichage des résultats filtrés en temps réel.

### 2. Consolider les commentaires et les unifier en liste déroulante ou tags
- **Description** : Centraliser tous les types de commentaires (client, agent, système) et proposer une interface unifiée pour les visualiser/filtrer (ex : dropdown, tags).
- **Priorité** : Haute
- **Complexité** : Modérée à élevée (dépend du nombre de sources et du format actuel des commentaires)
- **Détails** :
  - Normaliser le format des commentaires (structure, auteur, date, type).
  - Afficher tous les commentaires dans une seule colonne ou widget, avec typage (couleur/tag).
  - Permettre la sélection rapide d’un type de commentaire via dropdown ou tags interactifs.

### 3. Ajout d'une page d’export des données filtrées (dashboard, notifications, tableau salamgaz)
- **Description** : Permettre aux utilisateurs d’exporter les données affichées ou filtrées sous forme de fichier (CSV, Excel, etc.), depuis le dashboard ou les autres vues principales.
- **Priorité** : Moyenne
- **Complexité** : Modérée
- **Détails** :
  - Bouton d’export sur chaque page concernée.
  - Export des données selon les filtres actifs.
  - Génération du fichier côté backend (API) ou frontend (JS), selon le volume.

### 4. Logique d’assignation de clients par utilisateur
- **Description** : Permettre d’assigner explicitement un ou plusieurs clients à chaque utilisateur (agent, conseiller, etc.) depuis l’interface d’administration ou via un module dédié dans le dashboard.
- **Priorité** : Haute (impact direct sur la gestion et la répartition de la charge)
- **Complexité** : Modérée
- **Détails** :
  - Afficher la liste des clients non assignés et la liste des utilisateurs disponibles.
  - Permettre l’assignation manuelle (drag & drop, sélection multiple, bouton « Assigner »).
  - Visualiser les clients déjà assignés à chaque utilisateur (vue tableau ou carte).
  - Option de désassignation/réaffectation rapide.
  - Prendre en compte les quotas éventuels (paramètre global : `max_clients_per_user`).
  - Historiser chaque changement d’assignation (audit log).

---

**Résumé** :
1. Filtres sur dashboard (commentaires) → rapide, impact immédiat
2. Unification des commentaires (dropdown/tags) → plus structurant, mais essentiel pour la clarté
3. Export des données filtrées → utile, mais moins urgent
4. Assignation de clients par utilisateur → clé pour la gestion opérationnelle, à intégrer dès que possible

À ajuster selon les retours utilisateurs et la faisabilité technique (stack front utilisée).
