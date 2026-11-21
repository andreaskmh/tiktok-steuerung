#!/usr/bin/env python3
"""Ranglisten-Seite im WLAN (Artur 20.11.2026): http://<Mac>.local:8080 auf jedem Handy, ohne Anmeldung.

Liefert ~/.tiktok-research/seite/ (index.html, daten-de.json, daten-us.json – legt research.py `rangliste` dort ab)
und die gemeinsamen Haken: GET /haken → {video_id: "gemacht"|"nein"}, POST /haken {"v": id, "wert": "gemacht"|"nein"|null}
(alt: {"v": id, "an": bool}; gespeichertes true = gemacht). research.py filtern lässt ✓ und X weg (Artur 21.11.).
Kategorie-Korrekturen: GET /kategorie → {video_id: art}, POST /kategorie {"v": id, "art": "BOF"|…|null} → seite-kategorie.json;
research.py filtern übernimmt sie in <land>-sortiert.json (Artur 21.11.).
Haken liegen in ~/.tiktok-research/seite-haken.json (nur für Artur/Andreas, nichts mit Social1/gemacht.json).
Liegt außerhalb von ~/Documents, weil der Dauer-Start (launchd) dort nicht lesen darf (macOS-Schutz).
Start: werkzeuge/ranglisten-server-installieren.sh
"""
import http.server, json, pathlib, re, threading

HEIM = pathlib.Path.home() / ".tiktok-research"
SEITE = HEIM / "seite"
HAKEN = HEIM / "seite-haken.json"
KATEGORIE = HEIM / "seite-kategorie.json"
# Pfad → (Datei, Schlüssel im POST, erlaubte Werte)
SPEICHER = {"/haken": (HAKEN, "wert", ("gemacht", "nein")),
            "/kategorie": (KATEGORIE, "art", ("BOF", "REACTIONS", "SLIDES", "BOF+SLIDES", "QUALITY"))}
SPERRE = threading.Lock()
DATEIEN = {"/": "index.html", "/index.html": "index.html", "/daten-de.json": "daten-de.json", "/daten-us.json": "daten-us.json"}


def lesen(datei):
    try:
        return json.loads(datei.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Handler(http.server.BaseHTTPRequestHandler):
    def senden(self, code, body, typ):
        self.send_response(code)
        self.send_header("Content-Type", typ)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        pfad = self.path.split("?")[0]
        if pfad in SPEICHER:
            return self.senden(200, json.dumps(lesen(SPEICHER[pfad][0])).encode(), "application/json")
        name = DATEIEN.get(pfad)
        if not name or not (SEITE / name).exists():
            return self.senden(404, b"nicht gefunden", "text/plain; charset=utf-8")
        body = (SEITE / name).read_bytes()
        if name.endswith(".html"):                              # wie claude.ai: Grundgerüst + Handy-Breite (sonst 980px breit)
            body = (b'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" '
                    b'content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="apple-mobile-web-app-capable" '
                    b'content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black"></head><body>' + body + b"</body></html>")
        self.senden(200, body, "text/html; charset=utf-8" if name.endswith(".html") else "application/json")

    def do_POST(self):
        if self.path not in SPEICHER:
            return self.senden(404, b"", "text/plain")
        datei, schluessel, erlaubt = SPEICHER[self.path]
        try:
            d = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 1000)))
            v = str(d["v"])
            assert re.fullmatch(r"\d{5,25}", v)                 # nur Video-IDs, sonst nichts speichern
            wert = d[schluessel] if schluessel in d else ("gemacht" if d.get("an") else None)   # "an" = altes Haken-Format
            assert wert is None or wert in erlaubt
        except Exception:
            return self.senden(400, b"", "text/plain")
        with SPERRE:
            h = lesen(datei)
            if wert:
                h[v] = wert
            else:
                h.pop(v, None)
            tmp = datei.with_suffix(".tmp")
            tmp.write_text(json.dumps(h))
            tmp.replace(datei)
        self.senden(200, b"{}", "application/json")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
