# 🚦 Plan d’Action Priorisé (PAP) Sécurité BRASG

## 1. Sécuriser les environnements
- Restreindre les CORS en production (ne jamais laisser *)
- Forcer HTTPS sur tous les services (backend, frontend, proxy)
- Changer toutes les clés et secrets faibles ou par défaut

## 2. Renforcer l’authentification
- Vérifier la configuration JWT (durée, blacklist, refresh)
- Activer la validation stricte des mots de passe
- Mettre à jour les permissions DRF pour chaque endpoint

## 3. Protéger la base de données
- Créer un utilisateur PostgreSQL dédié avec droits minimaux
- Mettre en place des sauvegardes automatisées et testées

## 4. Automatiser la sécurité
- Mettre en place un pipeline CI/CD (Github Actions/Gitlab CI)
- Ajouter des étapes d’audit de dépendances (npm/pip)
- Ajouter des tests automatisés (backend et frontend)

## 5. Surveiller et auditer
- Activer Sentry (ou équivalent) pour le monitoring des erreurs
- Vérifier que l’audit log Django fonctionne et est exploité

## 6. Documenter et onboarder
- Vérifier la présence et la clarté des .env.example
- Maintenir à jour la documentation technique et stack.md
- Documenter les endpoints API (Swagger/Redoc)

---

**Priorité absolue :**
- CORS, HTTPS, secrets, permissions, audit log
- CI/CD et automatisation sécurité
- Sauvegardes DB

**À moyen terme :**
- Monitoring avancé, tests automatisés, documentation API
