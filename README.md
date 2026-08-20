# Private Cloud Infrastructure Lab

Self-hosted monitoring stack running on a single Docker host.

## Services

| Service       | Port | Purpose                          |
|---------------|------|----------------------------------|
| Nginx         | 80   | Dashboard + reverse proxy        |
| Backend       | —    | Python API, writes metrics to DB |
| PostgreSQL 16 | —    | Stores metric snapshots          |
| Prometheus    | 9090 | Metrics scraping & storage       |
| Grafana       | 3001 | Dashboards & log exploration     |
| Loki          | —    | Log storage                      |
| Promtail      | —    | Log collector                    |
| Node Exporter | —    | Host metrics for Prometheus      |

## Stack

- **Dashboard** — static HTML served by Nginx, polls `/api/metrics` and `/api/history` every 3s
- **Backend** — Python stdlib HTTP server (`app/backend/main.py`), reads `/proc` for host stats, inserts snapshots into PostgreSQL
- **Database** — PostgreSQL 16, schema initialized from `docker/init.sql`
- **Monitoring** — Prometheus scrapes Node Exporter; Promtail ships container logs to Loki; Grafana connects to both

## Layout

```
app/
  backend/    Python API (main.py, Dockerfile)
  frontend/   Dashboard (index.html)
ansible/      Host provisioning playbook
docker/       nginx.conf, init.sql
monitoring/   prometheus.yml, promtail config
scripts/      deploy.sh, backup.sh
backups/      pg_dump output (7-day retention)
```

## Usage

```bash
# Configure environment
cp .env.example .env
# edit .env and set POSTGRES_PASSWORD

# Start all services
docker compose up -d

# Rebuild after code changes
scripts/deploy.sh

# Backup database
scripts/backup.sh
```

## Endpoints

| URL          | Returns                              |
|--------------|--------------------------------------|
| `/api/metrics` | Current host stats (also writes a DB snapshot) |
| `/api/history` | Last 10 metric rows from PostgreSQL  |

## Notes

- Backend mounts `/proc` read-only to read host uptime, load, and memory
- Node Exporter mounts `/proc`, `/sys`, and `/` read-only for host metrics
- Backup retention: 7 days, managed by `backup.sh`
