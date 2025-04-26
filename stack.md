Objectif
je veux créer une application web moderne et jolie, avec :

# Stack technique (Mise à jour détaillée)

| Composant          | Technologie / Version          | Dépendances principales                    |
|--------------------|-------------------------------|--------------------------------------------|
| **Frontend**       | Next.js 15.3.1                | React 19, TypeScript, MUI 7.0.2, TailwindCSS 4, Axios 1.8.4, Chart.js 4.4.9, jwt-decode 4.0.0 |
| **Backend**        | Django >=4.2 (5.2 utilisé)     | djangorestframework, simplejwt, django-filter, decouple, dj-database-url, pandas, Pillow, openpyxl, cors-headers |
| **Base de données**| PostgreSQL                     | psycopg2-binary                            |
| **Auth**           | JWT (djangorestframework-simplejwt) | Stockage token côté client (localStorage/cookie), Intercepteur axios |
| **Historique**     | ORM Django (AuditLog, migrations auto) |                                        |
| **UI Design**      | Material UI (MUI)              | emotion/react, emotion/styled              |
| **API**            | REST (DRF)                     | Pagination, filtres, CORS                  |
| **DevOps**         | Docker, docker-compose         |                                            |
| **Sécurité**       | Password validation Django, JWT, CORS, .env non versionné |


## Arborescence du projet (extrait réel)

BRASG/
├── backend/
│   ├── brasg_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── ...
│   ├── core/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── views_api.py
│   │   ├── admin.py
│   │   ├── tests/ (backend)
│   │   └── ...
│   ├── villes/
│   │   ├── models.py
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── frontend-dashboard/
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── .env.local (non versionné)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── components/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── kpi/
│   │   │   │   └── ...
│   │   │   └── utils/
│   │   ├── public/
│   │   ├── tsconfig.json
│   │   ├── postcss.config.mjs
│   │   ├── tailwind.config.js
│   │   ├── eslint.config.mjs
│   │   └── ...
│   └── ...
├── docker-compose.yml
├── stack.md
└── ...

## Authentification & Sécurité

- **Authentification JWT (DRF SimpleJWT)**
    - Token stocké côté client (localStorage/cookie)
    - Intercepteur axios pour ajouter automatiquement le token dans l'en-tête Authorization
    - Expiration automatique, redirection vers /login si 401
- **Sécurité Django** :
    - Password validation (min length, common, numérique...)
    - User model personnalisé (core.User)
    - Permissions DRF sur les vues sensibles
    - Historique des modifications (AuditLog)
    - CORS (cors-headers) : ouvert en dev, à restreindre en prod
    - Variables sensibles dans .env (jamais versionné)
- **Sécurité Frontend** :
    - Variables d'environnement Next.js via .env.local (NEXT_PUBLIC_API_URL)
    - Pas de secret exposé côté client
- **Gestion des erreurs API** centralisée (intercepteur axios)

## Tests & Linting
- **Backend** : tests unitaires présents (core/tests.py, core/tests/), à renforcer (pytest recommandé)
- **Frontend** : pas de tests automatisés détectés (Jest/Testing Library à ajouter)
- **Lint** : ESLint (frontend, désactivé au build), config TypeScript stricte

## DevOps & Workflows
- **Docker** : Dockerfile backend, docker-compose.yml global (backend + DB + frontend possible)
- **CI/CD** : Pas de workflow Github Actions/Gitlab CI détecté, à mettre en place
- **Branching** : convention main/develop/feature/fix recommandée
- **Documentation** : README présents, stack.md mis à jour, doc technique à automatiser
- **Logs** : audit log côté backend, logs API côté frontend

## Points complémentaires ou manquants
- **Pas de SSR/ISR avancé** détecté côté Next.js (App Router prêt)
- **Pas de gestion avancée des rôles/permissions frontend** (possible à ajouter)
- **Pas de tests automatisés frontend** (Jest/Testing Library à ajouter)
- **Pas de gestion de cache/optimisation images Next.js** (possible à ajouter)
- **Pas de monitoring/alerting automatisé**
- **Pas de workflow CI/CD automatisé détecté**
- **Pas de scripts de migration DB automatisés** (hors Django migrate)
- **Pas d’internationalisation (i18n)** côté frontend (à prévoir si besoin)
- **Pas de gestion fine des droits d’accès API** (RBAC/ABAC à préciser si besoin)
- **Pas de gestion d’assets statiques frontend (CDN, optimisation)**

## Recommandations Sécurité & Modernité

1. **Restreindre CORS en production** :
   - Remplacer `CORS_ALLOW_ALL_ORIGINS = True` par une liste blanche de domaines.
2. **Utiliser HTTPS partout** (backend et frontend).
3. **Ne jamais versionner les fichiers .env** (utiliser .env.example pour documenter).
4. **Rotation régulière des secrets et tokens**.
5. **Activer les logs d'audit Django** pour toutes les modifications sensibles.
6. **Automatiser les tests de sécurité** (lint, SAST, dépendances vulnérables).
7. **Mettre à jour régulièrement les dépendances** (npm audit, pip list --outdated).
8. **Utiliser Docker pour isoler les environnements**.
9. **Limiter les droits DB et serveur** (principe du moindre privilège).
10. **Ajouter un workflow CI/CD** (Github Actions, Gitlab CI) pour lint, tests, build, audit dépendances, déploiement.
11. **Ajouter un `.env.example`** (backend + frontend) pour faciliter l’onboarding.
12. **Ajouter des tests automatisés** (frontend et backend).
13. **Ajouter un monitoring applicatif** (Sentry, Prometheus).
14. **Documenter les endpoints API** (Swagger/Redoc via DRF).
15. **Automatiser la génération de la doc technique** (mkdocs, sphinx).
16. **Mettre en place une politique de gestion des secrets** (Vault, Doppler, etc. si besoin).
17. **Gérer le versioning d’API** si évolutions majeures prévues.
18. **Ajouter un script de backup automatisé** pour la DB PostgreSQL.

---

**Pour toute évolution, se référer à ce fichier et à la roadmap technique.**
