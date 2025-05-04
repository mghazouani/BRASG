# Plan d’Action Planifié de Configuration des Services Ubuntu Production (PAPCSUP)

## Objectif
Mettre en place une infrastructure fiable, sécurisée et maintenable pour le déploiement de l’application BRASG sur un serveur Ubuntu 24.04 LTS en environnement de production.

---

## 1. Préparation du serveur
- [ ] Installer Ubuntu Server 24.04 LTS (mise à jour complète)
- [ ] Créer l’utilisateur système dédié (ex : brasg)
- [ ] Configurer le hostname et les accès SSH sécurisés
- [ ] Synchroniser l’heure (ntp)

## 2. Installation des dépendances système
- [ ] Installer Python 3, pip, venv
- [ ] Installer PostgreSQL et créer la base de données
- [ ] Installer Redis
- [ ] Installer Node.js, npm
- [ ] Installer Nginx
- [ ] Installer Git

## 3. Sécurisation du serveur
- [ ] Configurer le firewall UFW (ouvrir ports 22, 80, 443)
- [ ] Désactiver root SSH et forcer l’authentification par clé
- [ ] Installer Fail2ban

## 4. Déploiement du code applicatif
- [ ] Cloner le dépôt BRASG dans `/srv/BRASG`
- [ ] Créer et activer l’environnement virtuel Python
- [ ] Installer les dépendances backend (`pip install -r requirements.txt`)
- [ ] Installer les dépendances frontend (`npm install`)
- [ ] Configurer les fichiers `.env` pour la prod

## 5. Configuration des services systemd
- [ ] Créer les services suivants :
    - check-db (attente PostgreSQL)
    - brasg-backend (Django via Gunicorn)
    - redis-server (si nécessaire)
    - celery-worker
    - celery-beat
    - brasg-frontend (React/Node)
- [ ] Activer et démarrer tous les services
- [ ] Vérifier les logs systemd

## 6. Configuration Nginx
- [ ] Créer le virtualhost pour le backend (proxy_pass Gunicorn)
- [ ] Servir les fichiers statiques/media
- [ ] Créer le virtualhost pour le frontend (port 3000 ou build statique)
- [ ] Tester la configuration et recharger Nginx

## 7. Sécurisation HTTPS
- [ ] Installer Certbot
- [ ] Générer et installer les certificats SSL Let’s Encrypt
- [ ] Forcer le HTTPS sur Nginx

## 8. Automatisation & maintenance
- [ ] Ajouter un service systemd pour les migrations Django
- [ ] Ajouter un service/cron de backup régulier de la base et des fichiers
- [ ] Activer la rotation et la persistance des logs (journald)

## 9. Tests & validation
- [ ] Vérifier le démarrage automatique au reboot
- [ ] Tester tous les endpoints backend et frontend
- [ ] Vérifier la sécurité réseau (scan ports, SSL Labs)
- [ ] Documenter les procédures de maintenance

## 10. Documentation & passation
- [ ] Documenter toutes les étapes dans le wiki projet
- [ ] Sauvegarder les scripts et fichiers de config
- [ ] Former le référent technique ou l’équipe d’exploitation

---

**Responsable :** ______________________

**Date de mise en production prévue :** ______________________

**Commentaires :**
- Adapter chaque étape selon les besoins spécifiques du projet.
- Ce plan peut servir de checklist lors de chaque déploiement majeur ou migration.
