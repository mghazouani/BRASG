# BRASG Backend

## Lancement rapide

1. Installez les dépendances :
   ```
pip install -r requirements.txt
   ```
2. Configurez PostgreSQL dans `brasg_backend/settings.py`
3. Appliquez les migrations :
   ```
python manage.py migrate
   ```
4. Lancez le serveur :
   ```
python manage.py runserver
   ```

## Fonctionnalités
- API REST sécurisée JWT
- Modèles : Utilisateur, Client, AuditLog
- Historique automatique des modifications

## Configuration PostgreSQL
Adaptez la section DATABASES dans `settings.py` selon votre environnement.
