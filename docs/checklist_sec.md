# ✅ Checklist Sécurité BRASG

## 🔑 Gestion des secrets & variables d’environnement
- [x] Les fichiers .env et .env.local ne sont **jamais** versionnés (présents dans .gitignore)
- [x] Un fichier .env.example est fourni pour chaque partie (backend, frontend)
- [ ] Les clés secrètes sont fortes et changées régulièrement (DJANGO_SECRET_KEY, tokens JWT, etc.)
- [x] Les secrets ne sont **jamais** exposés côté frontend

## 🔒 Authentification & Permissions
- [x] Authentification JWT (DRF SimpleJWT) activée, tokens courts et rotation possible
- [ ] Permissions DRF configurées sur toutes les vues sensibles (backend)
- [x] Validation de mot de passe Django activée (longueur, complexité, blacklist)
- [x] User model personnalisé utilisé
- [ ] Gestion des rôles et permissions côté frontend (si besoin, à renforcer)

## 🌐 Sécurité Web & API
- [ ] CORS restreint en production (CORS_ALLOW_ALL_ORIGINS = False + whitelist)
- [ ] HTTPS activé partout (backend, frontend, reverse proxy)
- [ ] Headers de sécurité HTTP (HSTS, X-Frame-Options, etc.) ajoutés côté Django/Nginx
- [x] Pas de données sensibles dans les logs côté frontend
- [x] Pagination, filtrage et validation des entrées API

## 🗃️ Base de données & fichiers
- [ ] Accès DB limité (utilisateur dédié, droits minimaux)
- [ ] Sauvegardes régulières et testées de la base PostgreSQL
- [x] Fichiers uploadés stockés dans des dossiers protégés (MEDIA_ROOT)
- [x] Pas de fichiers de log ou backup exposés publiquement

## 🛡️ Monitoring & Audit
- [x] Audit log activé pour toutes les modifications sensibles (backend)
- [ ] Monitoring applicatif (Sentry, Prometheus, etc.) en place
- [ ] Alertes sur erreurs critiques et tentatives d’intrusion

## 🛠️ DevOps & CI/CD
- [ ] Workflows CI/CD automatisés (lint, tests, build, audit dépendances, déploiement)
- [ ] Scans de vulnérabilités réguliers (npm audit, pip-audit, safety)
- [x] Docker utilisé pour isoler les environnements
- [ ] Documentation technique et API à jour (Swagger/Redoc, README, stack.md)
