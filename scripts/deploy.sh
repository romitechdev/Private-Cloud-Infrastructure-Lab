#!/bin/bash
set -e

PROJECT_DIR="/home/romi/private-cloud-infrastructure-lab"
cd "$PROJECT_DIR"

echo "[+] Memulai proses deployment..."

# 1. Pull perubahan code terbaru dari Git repository
git pull origin main

# 2. Re-build dan update container backend/frontend yang berubah saja
docker compose up -d --build --no-deps backend nginx

# 3. Bersihkan dangling image yang tidak terpakai untuk hemat disk
docker image prune -f

echo "[✓] Deployment selesai dan service telah terupdate!"
