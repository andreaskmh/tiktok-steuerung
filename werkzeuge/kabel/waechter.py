#!/usr/bin/env python3
"""Hält den iPhone-Server (open-iphone-use) automatisch am Laufen – läuft als Autostart (LaunchAgent) beim Anmelden.

  python3 werkzeuge/kabel/waechter.py            # Dauerschleife (macht der Autostart)
  python3 werkzeuge/kabel/waechter.py einmal     # eine Prüfung, z. B. zum Testen

Alle 20 s:
  - Server antwortet nicht → starten (nach Mac-Neustart, Absturz).
  - iPhone hängt am Kabel, Server nutzt aber WLAN → Server neu starten (er wechselt nicht von selbst auf USB).
  - Server läuft, iPhone noch nicht eingebunden → einbinden.
Protokoll (nur Änderungen): ~/Library/Logs/ts-iphone-waechter.log
Einrichten/Entfernen: zsh werkzeuge/kabel/autostart.sh an|aus
"""
import json, os, pathlib, subprocess, sys, time, urllib.request

OIU = str(pathlib.Path.home() / ".local/bin/open-iphone-use")
PMD = str(pathlib.Path.home() / ".local/share/open-iphone-use/runtime/venv/bin/pymobiledevice3")
URL = "http://127.0.0.1:27893"
UDID = os.environ.get("TS_IPHONE_UDID", "00008030-00096C8621C3402E")
LOG = pathlib.Path.home() / "Library/Logs/ts-iphone-waechter.log"
_letzte = None


def log(msg):
    global _letzte
    if msg == _letzte:
        return
    _letzte = msg
    with open(LOG, "a") as f:
        f.write(time.strftime("%d.%m. %H:%M:%S ") + msg + "\n")
    if LOG.stat().st_size > 200_000:                    # klein halten
        LOG.write_text("\n".join(LOG.read_text().splitlines()[-500:]) + "\n")


def get(pfad, timeout=3):
    with urllib.request.urlopen(URL + pfad, timeout=timeout) as r:
        return json.loads(r.read())


def usb_da():
    try:
        out = subprocess.run([PMD, "usbmux", "list"], capture_output=True, text=True, timeout=15).stdout
        return any(d.get("Identifier") == UDID and d.get("ConnectionType") == "USB" for d in json.loads(out or "[]"))
    except Exception:
        return False


def starten(grund):
    log(f"starte Server ({grund})")
    subprocess.run([OIU, "serve"], capture_output=True, timeout=60)


def neustart(grund):
    log(f"Neustart ({grund})")
    subprocess.run([OIU, "stop"], capture_output=True, timeout=30)
    time.sleep(4)
    subprocess.run(["pkill", "-f", "open-iphone-use serve"], capture_output=True)
    time.sleep(1)
    starten(grund)


def pruefen():
    try:
        geraete = get("/api/devices")
    except Exception:
        return starten("lief nicht")
    d = next((g for g in geraete if g.get("udid") == UDID), None)
    if d is None:
        try:
            kand = [c for c in json.loads(subprocess.run([OIU, "candidates"], capture_output=True, text=True, timeout=30).stdout or "[]")
                    if c.get("udid") == UDID]
        except Exception:
            kand = []
        if kand:
            log("binde iPhone ein")
            subprocess.run([OIU, "new", "--udid", UDID], capture_output=True, timeout=60)
        else:
            log("iPhone nicht in Reichweite (Kabel/WLAN?)")
        return
    try:
        st = get(f"/api/devices/{d['device_id']}/status", timeout=5)["backend"]["status"]
    except Exception:
        st = {}
    if st.get("connection") == "Wi-Fi" and usb_da():
        return neustart("Kabel eingesteckt, Server war auf WLAN")
    log(f"ok: {st.get('connection')} bild={st.get('captureActive')}")


if __name__ == "__main__":
    if sys.argv[1:] == ["einmal"]:
        pruefen(); print(LOG.read_text().splitlines()[-1] if LOG.exists() else "")
        sys.exit(0)
    log("Wächter gestartet")
    while True:
        try:
            pruefen()
        except Exception as e:                              # nie aussteigen
            log(f"Fehler: {e}")
        time.sleep(20)
