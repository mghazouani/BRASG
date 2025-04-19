# BRASG — Backend Django

Application web de gestion de clients installés, remplaçant un fichier Excel de suivi. Pensée pour les équipes terrain, superviseurs et administrateurs.

## Fonctionnalités principales
- **Gestion des clients** : suivi, relance, priorisation, audit log
- **Import CSV/Excel** : validation avancée, gestion des erreurs
- **Gestion des utilisateurs** : rôles Agent, Superviseur, Admin (voir `docs/UserRoleExplained.md`)
- **Gestion des avatars** : upload sécurisé, miniatures, suppression propre, placeholder automatique
- **API REST** : pagination, recherche, filtres avancés, endpoints sécurisés JWT

## Installation rapide
```bash
# Cloner le projet
git clone https://github.com/mghazouani/BRASG.git
cd BRASG
python -m venv venv
venv\Scripts\activate  # ou source venv/bin/activate sous Linux/Mac
pip install -r backend/requirements.txt

# Lancer le serveur Django
cd backend
python manage.py migrate
python manage.py runserver
```

## Configuration
- Variables sensibles à placer dans `.env` (jamais en clair dans le code)
- Fichiers médias dans `/media/`, statiques dans `/static/`

## Documentation
- **Rôles utilisateurs** : voir `docs/UserRoleExplained.md`
- **Roadmap technique** : voir `stack.md`
- **Modèle métier** : voir `modelDJANGO.md`

## Sécurité
- Authentification JWT obligatoire pour toutes les actions sensibles
- Permissions adaptées selon le rôle utilisateur

## À faire
- Tests automatisés, doc API interactive, i18n, optimisation performance...

---

**Projet piloté par M. Ghazouani.**

Pour toute question ou contribution, ouvrir une issue sur GitHub ou contacter l’auteur.
