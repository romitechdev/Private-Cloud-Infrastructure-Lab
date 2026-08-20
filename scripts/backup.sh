#!/bin/bash
set -e

BACKUP_DIR="/home/romi/private-cloud-infrastructure-lab/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/infradb_backup_${TIMESTAMP}.sql"

# Buat direktori jika belum ada
mkdir -p "${BACKUP_DIR}"

echo "[+] Memulai backup database PostgreSQL..."

# Jalankan pg_dump langsung dari dalam container tanpa expose password mentah
docker exec -e PGPASSWORD=pancurhitz infra-postgres \
    pg_dump -U infrauser -d infradb > "${BACKUP_FILE}"

# Kompresi file backup untuk menghemat disk
gzip "${BACKUP_FILE}"

echo "[✓] Backup selesai: ${BACKUP_FILE}.gz"

# Retention Policy: Hapus backup yang lebih lama dari 7 hari
find "${BACKUP_DIR}" -type f -name "infradb_backup_*.sql.gz" -mtime +7 -delete
