#!/usr/bin/env python3
"""statsKMH auf Knopfdruck aktualisieren (Artur 20.11.2026: nur manuell, nichts automatisch).

  python3 werkzeuge/analyse/aktualisieren.py --wache     # Dienst: wartet auf den Knopf in der App (läuft per launchd)
  python3 werkzeuge/analyse/aktualisieren.py schnell     # direkt: Heute + Gestern + Guthaben (~2 Min./Account)
  python3 werkzeuge/analyse/aktualisieren.py voll        # direkt: 30 Tage + Video-Listen + Export + Prämien (~7 Min./Account)

Knopf in statsKMH → iCloud Drive/statsKMH/auftrag.json {"art": "schnell"|"voll"} → dieser Dienst arbeitet die Accounts ab und
schreibt laufend statsKMH/status.json (Schritt, Fortschritt, Restzeit). Danach app_daten.py → provision.json (App lädt neu).
Die Web-Version (Artifact) veröffentlicht nur Claude – sie wird beim nächsten Gespräch aktualisiert.
Geschätzte Zeiten lernen mit (dauer.json). Accounts eines Handys, das nicht erreichbar ist, werden übersprungen."""
import json, os, sys, time, subprocess, pathlib, urllib.request, datetime as D

HIER = pathlib.Path(__file__).resolve().parent
ICLOUD = pathlib.Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/statsKMH"
AUFTRAG, STATUS, DAUER, LOG = ICLOUD / "auftrag.json", ICLOUD / "status.json", HIER / "dauer.json", HIER / "aktualisieren.log"
KONTEN = ["anduri.official", "ella_robinson2", "artur.official", "andreasfastlane", "andreas.testet", "andrucha.official"]
# Stand 20.11.2026: auf jedem Handy sind alle Accounts angemeldet (iPhone 11 / iPhone 15 Pro Max)
GERAETE = [("00008030-00096C8621C3402E", list(KONTEN)), ("00008130-00163088368A001C", list(KONTEN))]
def zusatz_konten():
    """In der App hinzugefügte Accounts (statsKMH/konten.json: [{"name", "udid"}]) an die feste Liste anhängen."""
    try:
        for z in json.load(open(ICLOUD / "konten.json")).get("konten", []):
            n, u = z["name"].strip().lstrip("@"), z["udid"]
            if not n or any(n in ks for _, ks in GERAETE):
                continue
            ziel = next((ks for g, ks in GERAETE if g == u), None)
            if ziel is None:
                GERAETE.append((u, [n]))
            else:
                ziel.append(n)
    except Exception:
        pass


zusatz_konten()
SCHRITTE = {   # (Name, Befehl mit {k} = Konto)
    "schnell": [("Zahlen", ["daten_holen.py", "{k}", "--tage", "2", "--vtage", "0"]), ("Guthaben", ["export_holen.py", "--guthaben", "{k}"])],
    "voll": [("Zahlen + Videos", ["daten_holen.py", "{k}"]), ("Export", ["export_holen.py", "{k}"]),
             ("Prämien", ["export_holen.py", "--praemien", "{k}"])],
}
START_SEK = {"schnell": 120, "voll": 420}   # Startwert Sekunden pro Account, wird aus echten Läufen nachgeführt


def schreibe(pfad, daten):
    tmp = pfad.with_name("." + pfad.name + ".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False)); os.replace(tmp, pfad)   # nie halbe Datei in iCloud


def log(t):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + t + "\n")


def bild_da(udid):
    try:
        geraete = json.load(urllib.request.urlopen("http://127.0.0.1:27893/api/devices", timeout=10))
        return any(g["udid"] == udid and (g.get("age_ms") or 99999) < 5000 for g in geraete)
    except Exception:
        return False


def tippen_geht(udid):
    """Probe-Eingabe (Home-Taste – der Lauf startet ohnehin auf dem Home-Bildschirm)."""
    r = subprocess.run([sys.executable, "-c", "import kabel; kabel.taste('home')"], cwd=HIER.parent,
                       env=dict(os.environ, TS_IPHONE_UDID=udid, TS_WLAN="1"), capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stderr.strip().splitlines() or [""])[-1]


def server_neu():
    """21.11.2026: Server lieferte noch Bilder, aber jede Eingabe übers WLAN endete mit „No route to host“ → Neustart half."""
    subprocess.run(["pkill", "-f", "oiu.cli serve"], capture_output=True)
    time.sleep(3)
    subprocess.run([sys.executable, str(HIER.parent / "kabel" / "waechter.py"), "einmal"], capture_output=True, timeout=120)


def erreichbar(udid):
    """Steuer-Server läuft (sonst starten), das Handy liefert ein frisches Bild und nimmt Eingaben an (sonst Server neu starten)."""
    subprocess.run([sys.executable, str(HIER.parent / "kabel.py"), "status"], env=dict(os.environ, TS_IPHONE_UDID=udid, TS_WLAN="1"),
                   capture_output=True, timeout=90)
    if not bild_da(udid):
        return False
    ok, msg = tippen_geht(udid)
    if ok:
        return True
    log(f"Eingabe geht nicht ({msg[:120]}) – starte Steuer-Server neu")
    server_neu()
    geraet_hinzufuegen(udid)
    for _ in range(24):
        time.sleep(5)
        if bild_da(udid):
            break
    ok, msg = tippen_geht(udid)
    if not ok:
        log(f"Eingabe geht auch nach Neustart nicht: {msg[:160]}")
    return ok


def sek_pro_konto(art):
    try:
        return json.load(open(DAUER))[art]
    except Exception:
        return START_SEK[art]


def schaetzung():
    """Geschätzte Gesamtdauer je Art in Sekunden (für die Knöpfe in der App)."""
    n = len(ALLE_KONTEN)
    return {a: round(n * sek_pro_konto(a) + 20) for a in SCHRITTE}


ALLE_KONTEN = list(dict.fromkeys(k for _, ks in GERAETE for k in ks))   # jeder Account einmal


def geraet_hinzufuegen(udid):
    """Neues Handy (Entwicklermodus, im WLAN) beim Steuer-Server anmelden, falls noch nicht geschehen."""
    try:
        geraete = json.load(urllib.request.urlopen("http://127.0.0.1:27893/api/devices", timeout=10))
        if not any(g["udid"] == udid for g in geraete):
            req = urllib.request.Request("http://127.0.0.1:27893/api/devices", data=json.dumps({"udid": udid}).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=60)
    except Exception as e:
        log(f"Handy {udid} nicht anmeldbar: {e}")


def geraet_entfernen(udid):
    try:
        geraete = json.load(urllib.request.urlopen("http://127.0.0.1:27893/api/devices", timeout=10))
        for g in geraete:
            if g["udid"] == udid:
                urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:27893/api/devices/{g['device_id']}", method="DELETE"), timeout=30)
    except Exception as e:
        log(f"Handy {udid} nicht freigegeben: {e}")


def verstaendlich(z, k):
    """Technische Meldung → kurzer deutscher Satz für die App."""
    z = z.split(" (Foto ")[0]
    if "No route to host" in z or "Connection refused" in z or "timed out" in z.lower():
        return f"{k}: Handy nicht erreichbar – Kabel anstecken oder WLAN prüfen (Handy entsperrt?)"
    if "nicht in der Liste" in z:
        return z
    return z if z.startswith("STOPP") or z.startswith(k) else f"{k}: {z}"


def spiegel(udid):
    """iPhone-Spiegel für das gerade bediente Handy öffnen (app/spiegel, URL iphonespiegel://geraet/<udid>)."""
    subprocess.run(["open", "-g", f"iphonespiegel://geraet/{udid}"], capture_output=True)


def lauf(art, udid=None):
    schritte = SCHRITTE[art]
    if udid:   # gewähltes Handy: bekannte Accounts dieses Handys, sonst alle versuchen (fehlende werden übersprungen)
        geraet_hinzufuegen(udid)
        plan = [(udid, k) for k in next((ks for u, ks in GERAETE if u == udid), ALLE_KONTEN)]
    else:
        erstes = {}   # ohne Handy-Wahl: jeden Account nur einmal lesen, auf dem ersten Handy, das ihn hat
        for u, konten in GERAETE:
            for k in konten:
                erstes.setdefault(k, u)
        plan = [(u, k) for k, u in erstes.items()]
    pro_schritt = sek_pro_konto(art) / len(schritte)
    gesamt = len(plan) * len(schritte) + 1                      # +1 = App-Daten bauen
    start = time.time(); erledigt = 0; fehler = []; geschaetzt_fertig = 0.0
    st = {"laeuft": True, "art": art, "start": D.datetime.now().isoformat(timespec="seconds"),
          "geschaetzt_sek": round(len(plan) * sek_pro_konto(art) + 20), "fehler": [], "schaetzung": schaetzung()}

    def melde(text, konto=""):
        vergangen = time.time() - start
        faktor = vergangen / geschaetzt_fertig if geschaetzt_fertig > 60 else 1.0   # echtes Tempo vs. Schätzung
        rest = max(0, (len(plan) * len(schritte) - erledigt) * pro_schritt * faktor + 20)
        schreibe(STATUS, dict(st, schritt=text, konto=konto, fertig=erledigt, gesamt=gesamt, rest_sek=round(rest),
                              jetzt=D.datetime.now().isoformat(timespec="seconds"), fehler=fehler))

    log(f"Start {art}: {len(plan)} Accounts")
    ok_geraete = {}
    for udid, k in plan:
        if udid not in ok_geraete:
            melde(f"Handy wird verbunden …", k)
            ok_geraete[udid] = erreichbar(udid)
            if ok_geraete[udid]:
                spiegel(udid)
        for name, befehl in schritte:
            if not ok_geraete[udid]:
                if name == schritte[0][0]:
                    fehler.append(f"{k}: Handy nicht erreichbar (entsperrt, am Kabel/WLAN?)")
                erledigt += 1; geschaetzt_fertig += pro_schritt; melde("übersprungen", k); continue
            melde(name, k)
            r = subprocess.run([sys.executable, str(HIER / befehl[0])] + [b.replace("{k}", k) for b in befehl[1:]],
                               cwd=HIER, env=dict(os.environ, TS_IPHONE_UDID=udid, TS_WLAN="1"), capture_output=True, text=True)
            zeilen = [z for z in (r.stdout + r.stderr).splitlines() if z.strip()]
            stopp = [verstaendlich(z, k) for z in zeilen if z.startswith("STOPP")]
            if any("Traceback" in z for z in zeilen):                 # letzte Zeile = eigentlicher Fehler
                stopp.append(verstaendlich(zeilen[-1], k))
            if any("nicht in der Liste" in z for z in stopp):          # Account ist auf diesem Handy nicht angemeldet
                erledigt += len(schritte) - [n for n, _ in schritte].index(name) - 1
                geschaetzt_fertig += pro_schritt * (len(schritte) - [n for n, _ in schritte].index(name) - 1)
                fehler.append(f"{k}: nicht auf diesem Handy – übersprungen")
                erledigt += 1; geschaetzt_fertig += pro_schritt; melde("übersprungen", k)
                break
            if stopp:
                fehler.append(stopp[0][:160]); log(stopp[0]); log("  roh: " + " | ".join(zeilen[-3:])[:400])   # echte Meldung für die Fehlersuche
            erledigt += 1; geschaetzt_fertig += pro_schritt
            melde(name + " fertig", k)
    melde("App-Daten werden gebaut")
    if art == "voll":
        subprocess.run([sys.executable, str(HIER / "baue.py")], cwd=HIER, capture_output=True)
    subprocess.run([sys.executable, str(HIER / "app_daten.py")], cwd=HIER, capture_output=True)
    subprocess.run([sys.executable, str(HIER / "web.py")], cwd=HIER, capture_output=True)
    dauer = time.time() - start
    try:
        d = json.load(open(DAUER))
    except Exception:
        d = dict(START_SEK)
    d[art] = round(0.5 * d.get(art, START_SEK[art]) + 0.5 * dauer / len(plan))   # lernen: Mittel aus alt und neu
    json.dump(d, open(DAUER, "w"))
    st["schaetzung"] = schaetzung()
    schreibe(STATUS, dict(st, laeuft=False, ende=D.datetime.now().isoformat(timespec="seconds"), dauer_sek=round(dauer),
                          fertig=gesamt, gesamt=gesamt, rest_sek=0, schritt="fertig", fehler=fehler))
    log(f"Ende {art}: {round(dauer)} s, Fehler: {fehler}")
    for u in ok_geraete:   # Handys außer dem Daten-iPhone 11 wieder freigeben (sonst bleibt deren Kamera schwarz, Artur 21.11.)
        if u != GERAETE[0][0]:
            geraet_entfernen(u)


def wache():
    """Wartet auf auftrag.json (vom Knopf in der App). Nur auf Knopfdruck – kein Zeitplan."""
    ICLOUD.mkdir(parents=True, exist_ok=True)
    log("Dienst gestartet")
    try:
        alt = json.load(open(STATUS))
    except Exception:
        alt = {"laeuft": False, "schritt": "bereit"}
    if alt.get("laeuft"):                                         # Mac/Dienst war mittendrin weg → nicht ewig „läuft“
        alt.update(laeuft=False, schritt="abgebrochen (Dienst neu gestartet)")
    schreibe(STATUS, dict(alt, schaetzung=schaetzung()))
    while True:
        platzhalter = ICLOUD / ".auftrag.json.icloud"            # noch nicht aus iCloud geladen → anstoßen
        if platzhalter.exists():
            subprocess.run(["brctl", "download", str(AUFTRAG)], capture_output=True)
        if AUFTRAG.exists():
            try:
                j = json.load(open(AUFTRAG)); art, udid = j.get("art", "schnell"), j.get("udid")
            except Exception:
                time.sleep(2); continue                           # noch nicht fertig synchronisiert
            AUFTRAG.unlink()
            if art in SCHRITTE:
                try:
                    lauf(art, udid)
                except Exception as e:                            # Dienst läuft weiter, Fehler sichtbar in der App
                    log(f"Fehler: {e}")
                    schreibe(STATUS, {"laeuft": False, "art": art, "schritt": "abgebrochen", "fehler": [str(e)[:200]],
                                      "ende": D.datetime.now().isoformat(timespec="seconds")})
        time.sleep(3)


MODELLE = {"iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max", "iPhone13,2": "iPhone 12",
           "iPhone14,5": "iPhone 13", "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro",
           "iPhone15,3": "iPhone 14 Pro Max", "iPhone15,4": "iPhone 15", "iPhone16,1": "iPhone 15 Pro",
           "iPhone16,2": "iPhone 15 Pro Max", "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max", "iPhone17,3": "iPhone 16"}


def geraete():
    """Handys für die Auswahl in der App → statsKMH/geraete.json: erreichbare (Entwicklermodus, USB/WLAN, Steuer-Server
    /api/candidates) und dem Mac bekannte, gerade nicht erreichbare (devicectl, gekoppelt) – jeweils mit iPhone-Namen."""
    try:
        liste = json.load(urllib.request.urlopen("http://127.0.0.1:27893/api/candidates", timeout=15))
    except Exception:
        liste = []
    konten = {u: ks for u, ks in GERAETE}
    out = [{"udid": g["udid"], "name": g.get("name") or "iPhone", "modell": MODELLE.get(g.get("model"), g.get("model") or ""),
            "verbindung": "WLAN" if "Wi" in (g.get("connection") or "") else "Kabel", "erreichbar": True,
            "konten": konten.get(g["udid"], [])} for g in liste]
    tmp = HIER / ".geraete.json"
    try:   # bekannte, gekoppelte iPhones (auch wenn gerade aus/nicht im WLAN)
        subprocess.run(["xcrun", "devicectl", "list", "devices", "--json-output", str(tmp)], capture_output=True, timeout=30)
        for x in json.load(open(tmp))["result"]["devices"]:
            hw, cp = x.get("hardwareProperties", {}), x.get("connectionProperties", {})
            u = hw.get("udid")
            if not u or hw.get("reality") == "simulated" or cp.get("pairingState") != "paired" or any(o["udid"] == u for o in out):
                continue
            out.append({"udid": u, "name": x.get("deviceProperties", {}).get("name") or "iPhone",
                        "modell": MODELLE.get(hw.get("productType"), hw.get("productType") or ""), "verbindung": "nicht erreichbar",
                        "erreichbar": False, "konten": konten.get(u, [])})
    except Exception:
        pass
    finally:
        tmp.unlink(missing_ok=True)
    schreibe(ICLOUD / "geraete.json", {"stand": D.datetime.now().isoformat(timespec="seconds"), "geraete": out})


if __name__ == "__main__":
    a = sys.argv[1:] or ["--wache"]
    if a[0] == "--wache":
        wache()
    elif a[0] == "--geraete":
        geraete()
    elif a[0] in SCHRITTE:
        lauf(a[0], a[a.index("--udid") + 1] if "--udid" in a else None)
    else:
        print(__doc__)
