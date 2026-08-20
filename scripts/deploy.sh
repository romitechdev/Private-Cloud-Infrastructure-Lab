#!/bin/bash
set -e

PROJECT_DIR="/home/romi/private-cloud-infrastructure-lab"
cd "$PROJECT_DIR"

echo "[+] Memulai proses deployment..."

git pull origin main

docker compose up -d --build --no-deps backend nginx

docker image prune -f

echo "[✓] Deployment selesai dan service telah terupdate!"
