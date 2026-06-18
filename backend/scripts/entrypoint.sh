#!/bin/sh
set -e

cd /app

if [ "$1" = "migrate" ]; then
  echo "Running database migrations..."
  exec alembic upgrade head
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting: $*"
exec "$@"
