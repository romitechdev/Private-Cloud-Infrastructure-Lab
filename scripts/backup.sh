#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "${PROJECT_DIR}/.env"

BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/infradb_backup_${TIMESTAMP}.sql"

mkdir -p "${BACKUP_DIR}"

echo "[+] Memulai backup database PostgreSQL..."

docker exec -e PGPASSWORD="${POSTGRES_PASSWORD}" infra-postgres \
    pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > "${BACKUP_FILE}"

gzip "${BACKUP_FILE}"

echo "[✓] Backup selesai: ${BACKUP_FILE}.gz"

find "${BACKUP_DIR}" -type f -name "infradb_backup_*.sql.gz" -mtime +7 -delete
