#!/usr/bin/env bash
# Cron diario: expiración de AccessGrant (el acceso ya se niega en tiempo real vía expires_at).
# Instalar: sudo cp deploy/expire_access.cron /etc/cron.d/recetario-expire-access
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/recetario-backend}"
cd "$APP_DIR"
set -a
# shellcheck disable=SC1091
source "$APP_DIR/.env"
set +a
exec "$APP_DIR/.venv/bin/celery" -A config call content.expire_access_grants
