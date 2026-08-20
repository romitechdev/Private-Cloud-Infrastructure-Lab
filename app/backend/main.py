import http.server
import json
import os
import socketserver
import time
import psycopg2

PORT = 8000

DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB", "infradb"),
    "user": os.environ.get("POSTGRES_USER", "infrauser"),
    "password": os.environ.get("POSTGRES_PASSWORD", ""),
    "host": os.environ.get("DB_HOST", "postgres"),
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

class MetricHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/metrics':
            hostname = os.uname().nodename
            kernel = os.uname().release

            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])

            load_1, load_5, load_15 = os.getloadavg()

            meminfo = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        meminfo[parts[0].strip()] = int(parts[1].split()[0])

            total_ram_mb = meminfo.get('MemTotal', 0) // 1024
            free_ram_mb = meminfo.get('MemAvailable', 0) // 1024
            used_ram_mb = total_ram_mb - free_ram_mb
            uptime_hrs = round(uptime_seconds / 3600, 2)

            # Insert ke database PostgreSQL
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO server_metrics (hostname, uptime_hours, ram_used_mb, ram_total_mb, load_1m)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (hostname, uptime_hrs, used_ram_mb, total_ram_mb, load_1)
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"[!] Database Insert Error: {e}")

            payload = {
                "hostname": hostname,
                "kernel": kernel,
                "uptime_hours": uptime_hrs,
                "load_avg": {"1m": load_1, "5m": load_5, "15m": load_15},
                "ram": {"total_mb": total_ram_mb, "used_mb": used_ram_mb, "free_mb": free_ram_mb},
                "timestamp": int(time.time())
            }

            self._send_json(payload)

        elif self.path == '/api/history':
            history = []
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT timestamp, ram_used_mb, ram_total_mb, load_1m 
                    FROM server_metrics 
                    ORDER BY id DESC LIMIT 10
                    """
                )
                rows = cur.fetchall()
                for row in rows:
                    history.append({
                        "timestamp": row[0].strftime("%H:%M:%S"),
                        "ram_used_mb": row[1],
                        "ram_total_mb": row[2],
                        "load_1m": float(row[3])
                    })
                cur.close()
                conn.close()
            except Exception as e:
                print(f"[!] Database Fetch Error: {e}")

            self._send_json({"history": history})

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def _send_json(self, data):
        response_data = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_data)

with socketserver.TCPServer(("0.0.0.0", PORT), MetricHandler) as httpd:
    print(f"[+] Server with DB running on port {PORT}...")
    httpd.serve_forever()
