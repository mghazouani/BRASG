# Rôles Utilisateurs — Application de Gestion Clients

Ce document synthétise les différences de droits et responsabilités entre les trois rôles principaux de l’application : **Agent**, **Superviseur**, **Admin**.

---

## 1. Agent

- **Mission** : Suivi et accompagnement des clients installés.
- **Accès** :
  - Liste et fiches des clients qui lui sont attribués.
  - Mise à jour des infos clients, gestion des demandes d’aide, relances, commentaires.
  - Historique de ses propres actions.
- **Restrictions** :
  - Ne voit que ses clients.
  - Ne peut pas gérer les autres utilisateurs ni accéder à l’audit log global.

---

## 2. Superviseur

- **Mission** : Pilotage et contrôle de l’activité de toute l’équipe.
- **Accès** :
  - Liste complète de tous les clients (tous agents).
  - Audit log global (toutes les actions).
  - Réattribution de clients, gestion des priorités/alertes.
  - Génération de rapports, export de listes, statistiques avancées.
- **Pouvoirs supplémentaires** :
  - Peut modifier certains paramètres globaux et voir tous les historiques/commentaires.
- **Restrictions** :
  - Ne peut pas créer/supprimer des utilisateurs ni modifier la configuration technique.

---

## 3. Admin

- **Mission** : Gestion technique, sécurité, configuration globale.
- **Accès** :
  - Gestion complète des utilisateurs (création, modification, suppression, rôles).
  - Accès total à toutes les données, logs, imports/exports, statistiques.
  - Paramétrage global de l’application (règles, notifications, sécurité, modèles de données).
  - Interface d’administration Django.
- **Pouvoirs supplémentaires** :
  - Supervision technique, gestion des sauvegardes, logs système, politiques de sécurité.
- **Restrictions** :
  - Aucun (accès total).

---

## Tableau comparatif

| Rôle        | Portée d’action        | Gestion utilisateurs | Paramètres globaux | Audit log | Import/export | Statistiques | Sécurité |
|-------------|------------------------|---------------------|-------------------|-----------|--------------|--------------|----------|
| Agent       | Ses clients uniquement | Non                 | Non               | Non       | Limité       | Non          | Non      |
| Superviseur | Tous les clients       | Non                 | Partiel           | Oui       | Oui          | Oui          | Non      |
| Admin       | Tout (global)          | Oui                 | Oui               | Oui       | Oui          | Oui          | Oui      |

---

**Résumé** : L’agent agit sur le terrain, le superviseur pilote l’activité, l’admin gère tout le système.
