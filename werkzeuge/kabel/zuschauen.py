#!/usr/bin/env python3
"""Zuschau-Link fürs iPhone im WLAN (Artur 18.11.2026: „von allen anderen Geräten im WLAN zuschauen“, „permanenten Link“).

Nur ZUSCHAUEN: leitet ausschließlich das Livebild (MJPEG) des open-iphone-use-Servers (127.0.0.1:27893) weiter.
Kein Tippen, keine Steuerung, keine anderen Server-Seiten: alles außer GET / und GET /stream gibt 403/404.
Gerät wird bei jedem Abruf neu ermittelt → Link bleibt gleich, auch wenn der Server neu startet.

Link: http://<LocalHostName>.local:27894 oder http://<IP>:27894   (Autostart: zuschauen.sh an)
"""
import http.server, json, socketserver, urllib.request

QUELLE = "http://127.0.0.1:27893"
PORT = 27894

SEITE = """<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>iPhone live</title>
<style>html,body{margin:0;height:100%;background:#111;color:#bbb;font:15px -apple-system,sans-serif}
body{display:flex;align-items:center;justify-content:center}
img{max-height:100vh;max-width:100vw;object-fit:contain}#m{position:fixed;top:8px;left:0;right:0;text-align:center}</style>
<div id="m">verbinde …</div><img id="b" alt="">
<script>
const b=document.getElementById('b'),m=document.getElementById('m');
function los(){b.src='/stream?'+Date.now();}
b.onload=()=>{m.textContent='';};
b.onerror=()=>{m.textContent='iPhone gerade nicht verbunden – neuer Versuch …';setTimeout(los,3000);};
los();
</script></html>""".encode()


def geraet():
    with urllib.request.urlopen(QUELLE + "/api/devices", timeout=5) as r:
        liste = json.load(r)
    return liste[0]["device_id"] if liste else None


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        pfad = self.path.split("?")[0]
        if pfad == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(SEITE)
            return
        if pfad != "/stream":
            self.send_error(404)
            return
        try:
            d = geraet()
            if not d:
                raise RuntimeError("kein Gerät")
            q = urllib.request.urlopen(f"{QUELLE}/api/devices/{d}/stream", timeout=15)
        except Exception:
            self.send_error(503, "iPhone nicht verbunden")
            return
        self.send_response(200)
        self.send_header("Content-Type", q.headers.get("Content-Type", "multipart/x-mixed-replace; boundary=frame"))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                stueck = q.read1(65536)
                if not stueck:
                    break
                self.wfile.write(stueck)
        except Exception:
            pass
        finally:
            q.close()

    def _verboten(self):
        self.send_error(403, "nur zuschauen")

    do_POST = do_PUT = do_DELETE = do_PATCH = _verboten


class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    S(("0.0.0.0", PORT), H).serve_forever()
