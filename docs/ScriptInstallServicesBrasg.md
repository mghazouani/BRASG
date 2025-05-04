#!/bin/bash

set -e

USER_NAME="ton_user"  # <<< Remplace par ton nom d'utilisateur système
PROJECT_DIR="/srv/BRASG"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend/frontend-dashboard"
PYTHON="$BACKEND_DIR/venv/bin/python"
CELERY="$BACKEND_DIR/venv/bin/celery"
NPM="/usr/bin/npm"

echo "Création du script wait-for-postgres.sh..."
sudo tee /usr/local/bin/wait-for-postgres.sh > /dev/null <<EOF
#!/bin/bash
HOST=localhost
PORT=5432
RETRIES=30
echo "Waiting for PostgreSQL on \$HOST:\$PORT..."
until pg_isready -h "\$HOST" -p "\$PORT" >/dev/null 2>&1 || [ \$RETRIES -eq 0 ]; do
  echo "PostgreSQL not ready - retrying..."
  sleep 2
  RETRIES=\$((RETRIES-1))
done
if [ \$RETRIES -eq 0 ]; then
  echo "PostgreSQL did not become ready in time."
  exit 1
fi
echo "PostgreSQL is up!"
exit 0
EOF

sudo chmod +x /usr/local/bin/wait-for-postgres.sh

# --- check-db ---
sudo tee /etc/systemd/system/check-db.service > /dev/null <<EOF
[Unit]
Description=Check if PostgreSQL is ready
After=network.target
Before=brasg-backend.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/wait-for-postgres.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# --- brasg-backend ---
sudo tee /etc/systemd/system/brasg-backend.service > /dev/null <<EOF
[Unit]
Description=BRASG Django Backend
After=check-db.service
Requires=check-db.service

[Service]
User=$USER_NAME
WorkingDirectory=$BACKEND_DIR
ExecStart=$PYTHON manage.py runserver 0.0.0.0:8000
Restart=always
Environment=DJANGO_SETTINGS_MODULE=brasg_backend.settings

[Install]
WantedBy=multi-user.target
EOF

# --- redis-server (si manuel) ---
sudo tee /etc/systemd/system/redis-server.service > /dev/null <<EOF
[Unit]
Description=Redis Server
After=brasg-backend.service
Requires=brasg-backend.service

[Service]
ExecStart=/usr/bin/redis-server
Restart=always
User=redis

[Install]
WantedBy=multi-user.target
EOF

# --- celery-worker ---
sudo tee /etc/systemd/system/celery-worker.service > /dev/null <<EOF
[Unit]
Description=Celery Worker
After=redis-server.service
Requires=redis-server.service

[Service]
User=$USER_NAME
WorkingDirectory=$BACKEND_DIR
ExecStart=$CELERY -A brasg_backend worker -l info
Restart=always
Environment=DJANGO_SETTINGS_MODULE=brasg_backend.settings

[Install]
WantedBy=multi-user.target
EOF

# --- celery-beat ---
sudo tee /etc/systemd/system/celery-beat.service > /dev/null <<EOF
[Unit]
Description=Celery Beat
After=celery-worker.service
Requires=celery-worker.service

[Service]
User=$USER_NAME
WorkingDirectory=$BACKEND_DIR
ExecStart=$CELERY -A brasg_backend beat -l info
Restart=always
Environment=DJANGO_SETTINGS_MODULE=brasg_backend.settings

[Install]
WantedBy=multi-user.target
EOF

# --- brasg-frontend ---
sudo tee /etc/systemd/system/brasg-frontend.service > /dev/null <<EOF
[Unit]
Description=BRASG Frontend
After=celery-beat.service
Requires=celery-beat.service

[Service]
User=$USER_NAME
WorkingDirectory=$FRONTEND_DIR
ExecStart=$NPM run start
Restart=always
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable all services
echo "Activation des services..."
sudo systemctl daemon-reload

for service in check-db brasg-backend redis-server celery-worker celery-beat brasg-frontend; do
  sudo systemctl enable $service
done

echo "Tous les services ont été installés et activés au démarrage."
