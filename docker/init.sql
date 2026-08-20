CREATE TABLE IF NOT EXISTS server_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hostname VARCHAR(100),
    uptime_hours NUMERIC(6, 2),
    ram_used_mb INT,
    ram_total_mb INT,
    load_1m NUMERIC(5, 2)
);
