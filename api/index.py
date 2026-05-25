from http.server import BaseHTTPRequestHandler
import json
import math

DATA = [
    {"region":"apac","service":"analytics","latency_ms":213.35,"uptime_pct":98.529,"timestamp":20250301},
    {"region":"apac","service":"payments","latency_ms":153.26,"uptime_pct":97.904,"timestamp":20250302},
    {"region":"apac","service":"checkout","latency_ms":104.09,"uptime_pct":97.268,"timestamp":20250303},
    {"region":"apac","service":"payments","latency_ms":219.79,"uptime_pct":97.147,"timestamp":20250304},
    {"region":"apac","service":"checkout","latency_ms":164.7,"uptime_pct":97.494,"timestamp":20250305},
    {"region":"apac","service":"analytics","latency_ms":235.63,"uptime_pct":97.238,"timestamp":20250306},
    {"region":"apac","service":"support","latency_ms":166.5,"uptime_pct":97.744,"timestamp":20250307},
    {"region":"apac","service":"support","latency_ms":151.28,"uptime_pct":97.945,"timestamp":20250308},
    {"region":"apac","service":"recommendations","latency_ms":155.24,"uptime_pct":97.906,"timestamp":20250309},
    {"region":"apac","service":"payments","latency_ms":208.86,"uptime_pct":97.379,"timestamp":20250310},
    {"region":"apac","service":"catalog","latency_ms":158.52,"uptime_pct":97.764,"timestamp":20250311},
    {"region":"apac","service":"analytics","latency_ms":140.95,"uptime_pct":98.104,"timestamp":20250312},
    {"region":"emea","service":"payments","latency_ms":133.97,"uptime_pct":99.18,"timestamp":20250301},
    {"region":"emea","service":"recommendations","latency_ms":137.69,"uptime_pct":99.138,"timestamp":20250302},
    {"region":"emea","service":"support","latency_ms":189.22,"uptime_pct":97.904,"timestamp":20250303},
    {"region":"emea","service":"recommendations","latency_ms":144.68,"uptime_pct":99.098,"timestamp":20250304},
    {"region":"emea","service":"analytics","latency_ms":212,"uptime_pct":98.359,"timestamp":20250305},
    {"region":"emea","service":"payments","latency_ms":146.17,"uptime_pct":99.218,"timestamp":20250306},
    {"region":"emea","service":"checkout","latency_ms":148.09,"uptime_pct":99.033,"timestamp":20250307},
    {"region":"emea","service":"catalog","latency_ms":122.93,"uptime_pct":98.901,"timestamp":20250308},
    {"region":"emea","service":"catalog","latency_ms":159.21,"uptime_pct":98.384,"timestamp":20250309},
    {"region":"emea","service":"support","latency_ms":128.76,"uptime_pct":99.403,"timestamp":20250310},
    {"region":"emea","service":"support","latency_ms":235.9,"uptime_pct":97.445,"timestamp":20250311},
    {"region":"emea","service":"checkout","latency_ms":103.77,"uptime_pct":98.245,"timestamp":20250312},
    {"region":"amer","service":"catalog","latency_ms":126.6,"uptime_pct":98.367,"timestamp":20250301},
    {"region":"amer","service":"support","latency_ms":113.98,"uptime_pct":98.843,"timestamp":20250302},
    {"region":"amer","service":"catalog","latency_ms":131.97,"uptime_pct":97.186,"timestamp":20250303},
    {"region":"amer","service":"analytics","latency_ms":195.19,"uptime_pct":97.423,"timestamp":20250304},
    {"region":"amer","service":"checkout","latency_ms":200.48,"uptime_pct":99.227,"timestamp":20250305},
    {"region":"amer","service":"analytics","latency_ms":117.42,"uptime_pct":98.095,"timestamp":20250306},
    {"region":"amer","service":"checkout","latency_ms":221.42,"uptime_pct":97.575,"timestamp":20250307},
    {"region":"amer","service":"analytics","latency_ms":171.93,"uptime_pct":98.234,"timestamp":20250308},
    {"region":"amer","service":"catalog","latency_ms":188.77,"uptime_pct":97.148,"timestamp":20250309},
    {"region":"amer","service":"recommendations","latency_ms":132.17,"uptime_pct":98.908,"timestamp":20250310},
    {"region":"amer","service":"payments","latency_ms":171.47,"uptime_pct":97.893,"timestamp":20250311},
    {"region":"amer","service":"payments","latency_ms":189.75,"uptime_pct":98.551,"timestamp":20250312},
]

def percentile(values, p):
    values = sorted(values)
    pos = (len(values) - 1) * p
    lower = math.floor(pos)
    upper = math.ceil(pos)
    if lower == upper:
        return values[int(pos)]
    return values[lower] + (values[upper] - values[lower]) * (pos - lower)

def calculate(regions, threshold):
    results = []
    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        results.append({
            "region": region,
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": percentile(latencies, 0.95),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(1 for x in latencies if x > threshold)
        })
    return {"results": results}

class handler(BaseHTTPRequestHandler):
    def _headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Expose-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._headers(200)
        self.wfile.write(b"{}")

    def do_GET(self):
        self._headers(200)
        self.wfile.write(json.dumps({"message": "POST endpoint is running"}).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}

            regions = body.get("regions", [])
            threshold = body.get("threshold_ms", 0)

            response = calculate(regions, threshold)
            self._headers(200)
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self._headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())