from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import random
import threading
import time

LOCK = threading.Lock()
METRICS = {
    "cotizaciones": {"auto": 12, "moto": 8, "vida": 5},
    "polizas_emitidas": 9,
    "latencia_ms": 42.5,
}

def get_memory_bytes():
    try:
        with open("/proc/self/statm", "r") as f:
            pages = int(f.read().split()[1])
            return pages * os.sysconf("SC_PAGE_SIZE")
    except Exception:
        return 34603008

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        if self.path.startswith("/cotizar"):
            inicio = time.time()
            tipo = random.choice(["auto", "moto", "vida"])
            prima = round(random.uniform(3200.0, 14800.0), 2)
            time.sleep(random.uniform(0.015, 0.065))
            duracion = round((time.time() - inicio) * 1000, 2)
            with LOCK:
                METRICS["cotizaciones"][tipo] += 1
                METRICS["latencia_ms"] = duracion
                if random.random() > 0.35:
                    METRICS["polizas_emitidas"] += 1
            body = json.dumps({
                "servicio": "cotizador-service",
                "tipo_poliza": tipo,
                "prima_anual_mxn": prima,
                "latencia_ms": duracion
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/metrics":
            with LOCK:
                c_auto = METRICS["cotizaciones"]["auto"]
                c_moto = METRICS["cotizaciones"]["moto"]
                c_vida = METRICS["cotizaciones"]["vida"]
                polizas = METRICS["polizas_emitidas"]
                latencia = METRICS["latencia_ms"]
            mem = get_memory_bytes()
            lines = [
                "# HELP aseguratech_cotizaciones_total Total de cotizaciones procesadas por tipo de poliza",
                "# TYPE aseguratech_cotizaciones_total counter",
                f'aseguratech_cotizaciones_total{{tipo_poliza="auto"}} {c_auto}',
                f'aseguratech_cotizaciones_total{{tipo_poliza="moto"}} {c_moto}',
                f'aseguratech_cotizaciones_total{{tipo_poliza="vida"}} {c_vida}',
                "# HELP aseguratech_polizas_emitidas_total Total de polizas emitidas exitosamente",
                "# TYPE aseguratech_polizas_emitidas_total counter",
                f"aseguratech_polizas_emitidas_total {polizas}",
                "# HELP aseguratech_cotizacion_latencia_ms Latencia de calculo de cotizacion en milisegundos",
                "# TYPE aseguratech_cotizacion_latencia_ms gauge",
                f"aseguratech_cotizacion_latencia_ms {latencia}",
                "# HELP aseguratech_memoria_proceso_bytes Memoria residente del proceso en bytes",
                "# TYPE aseguratech_memoria_proceso_bytes gauge",
                f"aseguratech_memoria_proceso_bytes {mem}",
                "# HELP aseguratech_servicio_up Estado operativo del microservicio (1=activo)",
                "# TYPE aseguratech_servicio_up gauge",
                "aseguratech_servicio_up 1",
            ]
            payload = ("\n".join(lines) + "\n").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"app":"AseguraTech Core","endpoints":["/health","/cotizar","/metrics"]}')

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8081), Handler)
    server.serve_forever()
