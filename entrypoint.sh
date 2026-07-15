#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}
BACKEND_PORT=${BACKEND_PORT:-8000}
export BACKEND_PORT

groupadd -g "$PGID" deckvault 2>/dev/null || true
useradd -u "$PUID" -g "$PGID" -M -s /bin/false deckvault 2>/dev/null || true

chown -R "$PUID:$PGID" /app/backend/data

chmod o+w /dev/stdout /dev/stderr

echo "Running database migrations..."
cd /app/backend
gosu deckvault alembic upgrade head

echo "Starting DeckVault (frontend :4367, backend 127.0.0.1:${BACKEND_PORT})..."
exec gosu deckvault /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
