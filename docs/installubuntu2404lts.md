# Procédure complète de déploiement BRASG sur Ubuntu 24.04 LTS

Ce guide détaille l'installation de toutes les dépendances nécessaires, la configuration de la base de données PostgreSQL, le clonage du dépôt BRASG et le lancement de l'application.

---

## Étape préliminaire : Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

## 1. Prérequis système
- Ubuntu Server/Desktop 24.04 LTS fraîchement installé
- Accès sudo/root
- Accès internet

## 2. Installation des dépendances système
```bash
sudo apt install -y python3 python3-pip python3-venv build-essential libpq-dev git ufw
```

## 3. Installation et configuration de PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
```

### 3.1 Création de l'utilisateur et de la base de données
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

### 3.2 Modifier l'accès local (optionnel, pour accès réseau)
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```
Remplacez `peer` par `md5` pour la ligne `local` si besoin, puis :
```bash
sudo systemctl restart postgresql
```

## 4. Installation et configuration de Redis (pour Celery et cache)
```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 5. Clonage du projet
```bash
sudo mkdir -p /srv && cd /srv
sudo git clone https://github.com/mghazouani/BRASG.git
sudo chown -R $USER:$USER BRASG
cd BRASG
```

## 6. Création et activation de l’environnement virtuel Python
```bash
cd backend
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## 7. Configuration du pare-feu (si accès distant)
```bash
sudo ufw allow 8000
sudo ufw allow 6379  # Pour Redis si besoin
```

## 8. Configuration du fichier .env
Créez/modifiez le fichier `.env` dans `/srv/BRASG/backend/` :
```env
DJANGO_SECRET_KEY=change_me
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=postgres://brasg_user:brasg_pass@localhost:5432/brasg_db
ODOO_URL=http://188.68.35.228:8069
ODOO_DB=DIMAGAZ
ODOO_PASSWORD=mehdi123
ODOO_USER=mehdi.ghazouani@sonomac.ma
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=monuser
EMAIL_HOST_PASSWORD=motdepasse
```
> **Ne jamais commiter ce fichier `.env` dans le dépôt git.**

## 9. Migration et création du superutilisateur
```bash
python manage.py migrate
python manage.py createsuperuser
```

## 10. Collecte des fichiers statiques (pour la production)
```bash
python manage.py collectstatic
```

## 11. Lancement du backend Django
```bash
python manage.py runserver 0.0.0.0:8000
```

## 12. Lancement de Celery (!!!!!!!######dans un autre terminal#####!!!!!!!!)
```bash
cd backend
source venv/bin/activate
celery -A brasg_backend worker -l info
celery -A brasg_backend beat -l info
```

## 13. Sécurisation Django (en production)
- Passez `DEBUG=False` dans `.env`.
- Renseignez les vrais domaines/IP dans `ALLOWED_HOSTS`.
- Utilisez une clé secrète forte et unique pour `DJANGO_SECRET_KEY`.

## 14. Vérifications finales
- Accédez à l’admin Django via `/admin/`.
- Vérifiez les logs (`backend/logs/`, `systemctl status redis-server`, etc.).
- Testez la connexion à la base de données et à Redis.

## 15. (Optionnel) Configuration du service (systemd/supervisor) pour Django et Celery
- Créez des fichiers de service pour automatiser le lancement de Django, Celery worker et beat.

---

**Remarques** :
- Adaptez les ports, chemins et variables à votre environnement.
- Pour un déploiement en production, configurez nginx/gunicorn pour servir Django et les fichiers statiques.
- Pensez à sécuriser les accès SSH et à sauvegarder régulièrement la base de données.

---

## 16. Frontend React (dashboard)
```bash
cd ../frontend/frontend-dashboard
sudo apt install npm
npm install

# (IMPORTANT) Créez ou éditez le fichier .env.local pour paramétrer l'URL de l'API backend :
# /srv/BRASG/frontend/frontend-dashboard/src/utils

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

## 17. (Optionnel) Reverse proxy avec Nginx
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
