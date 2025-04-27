# Procédure complète de déploiement BRASG sur Ubuntu 24.04 LTS

Ce guide détaille l'installation de toutes les dépendances nécessaires, la configuration de la base de données PostgreSQL, le clonage du dépôt BRASG et le lancement de l'application.

---

## 1. Prérequis système
- Ubuntu Server/Desktop 24.04 LTS fraîchement installé
- Accès sudo/root
- Accès internet

## 2. Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

## 3. Installation des dépendances principales
```bash
sudo apt install -y git python3 python3-venv python3-pip build-essential libpq-dev
```

## 4. Installation et configuration de PostgreSQL
```bash
sudo apt install -y postgresql-17 postgresql-contrib
```

### 4.1 Création de l'utilisateur et de la base de données
Remplacez `brasg_user`, `brasg_db` et `brasg_pass` par les valeurs souhaitées si besoin.

```bash
sudo -u postgres psql
```
Dans le shell psql :
```sql
CREATE USER brasg_user WITH PASSWORD 'brasg_pass';
CREATE DATABASE brasg_db OWNER brasg_user;
GRANT ALL PRIVILEGES ON DATABASE brasg_db TO brasg_user;
\q
```

### 4.2 Modifier l'accès local (optionnel, pour accès réseau)
```bash
sudo nano /etc/postgresql/17/main/pg_hba.conf
```
Remplacez `peer` par `md5` pour la ligne `local` si besoin, puis :
```bash
sudo systemctl restart postgresql
```

## 5. Clonage du repository BRASG

**Chemin recommandé :** `/srv/BRASG` (ou autre selon vos standards)
```bash
sudo mkdir -p /srv && cd /srv
sudo git clone https://github.com/mghazouani/BRASG.git
sudo chown -R $USER:$USER BRASG
cd BRASG
```

## 6. Backend Django : installation et configuration
```bash
cd backend
python3 -m venv venv
cd ..

pip install --upgrade pip
pip install -r requirements.txt
```

Créez/modifiez le fichier `.env` dans `/srv/BRASG/backend/` :
```env
DJANGO_SECRET_KEY=change_me
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=postgres://brasg_user:brasg_pass@localhost:5432/brasg_db
```

### 6.1 Migration et création du superutilisateur
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6.2 Lancement du backend
```bash
python manage.py runserver 0.0.0.0:8000
```

## 6.bis Installation et configuration de Celery + Redis pour la synchronisation automatique

```bash
# Installer Redis (service de messages pour Celery)
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Installer Celery et lier à Django (dans le venv Python du backend)
pip install celery redis
```

**Configuration Django**
- Vérifiez que `celery.py` est bien dans le dossier principal du projet Django (`backend/brasg_backend/`).
- Ajoutez dans `settings.py` :
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'sync_bc_linbc_every_5min': {
        'task': 'scrap_sga.tasks.sync_bc_linbc_task',
        'schedule': 300,  # toutes les 5 minutes
    },
}
```
- Créez le fichier `tasks.py` dans `scrap_sga` si besoin :
```python
from celery import shared_task
import subprocess

@shared_task
def sync_bc_linbc_task():
    subprocess.call(['python', 'manage.py', 'sync_BcLinbc'])
```

**Lancement des workers Celery**
Dans deux terminaux :
```bash
cd /srv/BRASG/backend
celery -A brasg_backend worker --loglevel=info
celery -A brasg_backend beat --loglevel=info
```

**Vérification**
- La synchro BC/lines s’exécutera automatiquement toutes les 5 minutes.
- Les logs apparaîtront dans la console Celery.

---

## 7. Frontend React (dashboard)
```bash
cd ../frontend/frontend-dashboard
sudo apt install npm
npm install

# (IMPORTANT) Créez ou éditez le fichier .env.local pour paramétrer l'URL de l'API backend :
# /srv/BRASG/frontend/frontend-dashboard/src/app

echo "NEXT_PUBLIC_API_URL=http://<adresse-backend>:8000/api/" > .env.local

changer dans le fichier frontend/frontend-dashboard/src/utils/api.ts par 
- l'adresse du backend 
ou http://localhost:8000/api/ 
ou par la variable NEXT_PUBLIC_API_URL "process.env	.NEXT_PUBLIC_API_URL"

	const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/";

	export const api = axios.create({
  		baseURL: API_BASE_URL,
  		...
		});


```

npm run build
npm start
```

- Accès par défaut au dashboard : http://localhost:3000

## 8. (Optionnel) Reverse proxy avec Nginx
Pour exposer le service sur un domaine, configurer Nginx comme reverse proxy (hors scope de ce guide).

---

## Résumé des chemins importants
- Backend : `/srv/BRASG/backend/`
- Frontend : `/srv/BRASG/frontend/frontend-dashboard/`
- Base PostgreSQL : `brasg_db` (user : `brasg_user`)

---

## Configuration initiale application BRSAG 
importer ville_region.csv
importer clients.csv
ajouter enregistrement json dans Configuration du Dashboard :

	{"langue": [{"label": "Arabe", "value": "arabe"}, {"label": "Français", "value": "francais"}], "maj_app": "1.3.2+34", "app_installee": [{"label": "Oui", "value": true}, {"label": "Non", "value": false}], "canal_contact": [{"label": "Téléphone", "value": "telephone"}, {"label": "Whatsapp", "value": "whatsapp"}], "a_demande_aide": [{"label": "Oui", "value": true}, {"label": "Non", "value": false}], "statut_general": [{"label": "Actif", "value": "actif"}, {"label": "Inactif", "value": "inactif"}, {"label": "Bloqué", "value": "bloque"}], "notification_client": [{"label": "Notifié", "value": true}, {"label": "Non notifié", "value": false}]}


## Support
Pour toute question, ouvrez un ticket sur le repository GitHub ou contactez l’administrateur système.
