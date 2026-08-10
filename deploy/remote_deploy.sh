#!/usr/bin/env bash
# Ejecutar en el Droplet tras `git pull`.
# Uso: bash deploy/remote_deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/recetario-backend}"
APP_USER="${APP_USER:-recetario}"
APP_GROUP="${APP_GROUP:-www-data}"

cd "$APP_DIR"

echo "==> Ownership"
chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"

echo "==> Install dependencies"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -e ".[prod]" --quiet

echo "==> Migrate"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" manage.py migrate --noinput

echo "==> Collectstatic"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" manage.py collectstatic --noinput

echo "==> Restart services"
systemctl restart recetario-api recetario-worker
systemctl is-active --quiet recetario-api
systemctl is-active --quiet recetario-worker

echo "==> Health check"
sleep 2
curl -fsS -H "Host: petralicious.sk" http://127.0.0.1/health/ >/dev/null
echo "Deploy OK"
