#!/usr/bin/env python3
"""Stock-Bilder eines TikTok-Shop-Produkts vollautomatisch holen (über Social1, nie über die TikTok-Suche).

  python3 werkzeuge/stock.py <produkt-id> <ordnername> ["Produktname"] [zielordner]
  python3 werkzeuge/stock.py --stapel liste.json     # viele Produkte, eine Zeile je Produkt, Fertige übersprungen

Ablauf am iPhone: Home → Safari → social1.ai/products/<id> → „View on TikTok Shop“ → Produktbild antippen
→ Vollbild-Galerie → galerie.sh holt alle Bilder nach uebergabe/ausgang/<ordnername>/.
Mit [zielordner] (z. B. „…/Editing System 1.1/Videos/Video 140/Belege/<produkt>“) werden die Bilder zusätzlich
dorthin kopiert. Bei Unklarem: STOPP, nichts blind antippen (nie in die Nähe von Kasse/Jetzt kaufen/Einkaufswagen).
"""
import pathlib, shutil, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh
from posten import taps, schnell, key, Stopp, muss, log

PROJ = HIER.parent
GEFAHR = ("kasse", "jetzt kaufen", "einkaufswagen", "kaufen")


def home():
    if seh.kabel():
        seh.kabel().taste("home"); time.sleep(0.6)
        seh.kabel().taste("home"); time.sleep(0.8)              # 2× = sicher auf Seite 1
        return
    subprocess.run(["osascript", "-e", 'tell application "System Events" to tell (first process whose bundle identifier '
                    'is "com.apple.ScreenContinuity") to click menu item "Home-Bildschirm" of menu "Darstellung" of menu bar 1'],
                   capture_output=True)
    time.sleep(1.0)


def sicher_tippen(x, y, abstand=45):
    """Nur tippen, wenn kein Kauf-Knopf in der Nähe steht."""
    for t, tx, ty in seh.lesen():
        if abs(ty - y) < abstand and any(g in t.lower() for g in GEFAHR):
            raise Stopp(f"„{t}“ liegt zu nah am Tipp-Punkt ({x:.0f},{y:.0f})")
    taps(x, y)


def zur_galerie(pid, produkt=None):
    home()
    _, y = muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2")
    schnell("Safari")
    time.sleep(1.2)
    f = muss(seh.warte("Safari", 3, genau=True, ueber=300), "Safari nicht in der Suche")
    taps(f[0], f[1] - 20 if seh.kabel() else 145, "w2.0")         # Toptreffer (Kabel: Symbol über dem Namen)
    # Adressleiste unten antippen
    if seh.kabel():                                              # Kabel: ⌘L = Adressleiste, kein Tipp neben das Mikrofon
        seh.kabel().taste("cmd+l"); time.sleep(0.8)
    else:
        tx = seh.lesen()
        leiste = [t for t in tx if t[2] > 640 and ("." in t[0] or "suchen" in t[0].lower())]
        muss(leiste, "Safari-Adressleiste nicht gefunden")
        taps(167, leiste[0][2], "w1.0")
                                                                 # iOS markiert die alte Adresse selbst
    schnell(f"social1.ai/products/{pid}")
    key(36)                                                      # Return
    f = muss(seh.warte("View on TikTok Shop", 15), "Social1-Seite ohne „View on TikTok Shop“ (Login? Artur)")
    # 12.11.2026: TikTok zeigte noch die ALTE Produktseite (Düfte aus Video 139 unter „Roborock“) → erst weiter,
    # wenn der Shopname von der Social1-Seite (Zeilen zwischen „Promote S1“ und „View on TikTok Shop“) auch in TikTok steht.
    import re
    pw = re.findall(r"[a-zäöüß0-9]{4,}", (produkt or "").lower())[:2]   # auch Social1 zeigt kurz noch das alte Produkt
    for _ in range(20):
        s1 = [t for t, _, _ in seh.lesen()]
        if not pw or any(w in " ".join(s1).lower() for w in pw):
            break
        time.sleep(1)
    else:
        raise Stopp(f"Social1 zeigt nicht das Produkt {pw}")
    f = seh.finde("View on TikTok Shop") or f
    try:
        kopf = s1[s1.index("Promote S1") + 1: s1.index("View on TikTok Shop")]
    except ValueError:
        kopf = []
    shop = {w for t in kopf if "..." not in t and "…" not in t for w in re.findall(r"[a-z0-9äöü]{4,}", t.lower())}
    log(f"Shop laut Social1: {sorted(shop) or '?'}")
    taps(f[0], f[1], "w3.0")
    for _ in range(40):                                          # evtl. „In TikTok öffnen?“, TikTok lädt manchmal > 10 s
        tx = seh.lesen()
        o = seh.finde("Öffnen", tx, genau=True)
        if o:
            taps(o[0], o[1], "w2.5"); continue
        txt = " ".join(t.lower() for t, _, _ in tx)
        if any(g in txt for g in ("kasse", "jetzt kaufen", "verdiene")) and (not shop or any(w in txt for w in shop)):
            break
        time.sleep(0.5)
    else:
        raise Stopp(f"TikTok-Produktseite von {sorted(shop)} nicht erreicht (alte Seite offen?)")
    log("Produktseite passt (Shop gefunden)")
    time.sleep(1.5)
    ziehe_hoch(450, 110)                                         # Vorschaukarte zur vollen Seite hochziehen
    time.sleep(1.5)
    for versuch in range(2):                                     # Tipp kommt oft erst beim 2. Mal an
        sicher_tippen(167, 300)                                  # Produktbild
        time.sleep(1.8)
        z = zaehler()
        if z:
            log(f"Galerie offen: {z[0]}/{z[1]}"); return
    raise Stopp("Vollbild-Galerie nicht offen (kein Zähler)")


def zaehler(p=None):
    """Galerie-Zähler oben rechts (z. B. 3/12) → (3, 12) oder None."""
    p = p or f"{seh.TMP}/z.png"
    seh.aufnahme(p)
    zz = subprocess.run([str(HIER / "bin" / "zaehler"), p], capture_output=True, text=True)
    if zz.returncode:
        return None
    a = zz.stdout.split()
    return int(a[0]), int(a[1])


def galerie_kabel(name, produkt, s1, tts):
    """Wie galerie.sh, aber per Kabel: verlustfreie Bilder, echtes Wischen. Ergebnis wie galerie.sh."""
    import datetime, json
    K = seh.kabel()
    out = PROJ / "uebergabe" / "ausgang" / name
    out.mkdir(parents=True, exist_ok=True)
    y = K.hoehe() * 0.42

    def schritt(richtung):                                      # +1 = nächstes Bild (Finger nach links)
        a, b = (280, 54) if richtung > 0 else (54, 280)
        K.ziehe(a, y, b, y, 0.12); time.sleep(0.45)                # schnell: Galerie muss nicht menschlich wirken (Artur 12.11.)

    z = muss(zaehler(), "Kein Galerie-Zähler zu sehen – ist die Vollbild-Galerie offen?")
    n = z[1]; log(f"Galerie: {z[0]}/{n}")
    v = 0
    while z[0] > 1:
        schritt(-1); z = muss(zaehler(), "Zähler weg beim Zurückwischen")
        v += 1
        if v > n + 3:
            raise Stopp("Zurück auf Bild 1 klappt nicht")
    bilder = []
    for i in range(1, n + 1):
        f = out / f"bild-{i:02d}.png"
        z = None
        for _ in range(6):                                      # Bild kurz ruhen lassen, dann Zähler prüfen (schnell, dafür öfter)
            time.sleep(0.15)
            z = zaehler(str(f))
            if z and z[0] == i:
                break
        if not z or z[0] != i:
            raise Stopp(f"Erwartet Bild {i}, Zähler zeigt {z}")
        bilder.append(f.name); log(f"✓ {f.name}")
        if i < n:
            schritt(+1)
    json.dump({"version": 1, "produkt": produkt, "social1_link": s1, "tts_link": tts,
               "geholt_am": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "bilder": bilder, "anzahl_laut_galerie": n, "quelle": "kabel"},
              open(out / "produkt.json", "w"), ensure_ascii=False, indent=2)
    log(f"Fertig: {n} Bilder in {out}")


def ziehe_hoch(von_y, nach_y, x=167):
    """Echter Wisch nach oben (Kabel) bzw. mit der virtuellen Maus (Fensterpunkte)."""
    if seh.kabel():
        seh.kabel().ziehe(x, von_y, x, nach_y, 0.35); time.sleep(1.2)
        if seh.finde("Bestellungen", ueber=220):
            seh.kabel().ziehe(x, von_y, x, nach_y - 60, 0.5); time.sleep(1.2)
        return
    out = subprocess.run([str(HIER / "bin" / "fenster")], capture_output=True, text=True).stdout.split()
    fx, fy = int(out[1]), int(out[2])
    subprocess.run([sys.executable, str(HIER / "ziehen.py"), str(fx + x), str(fy + von_y), str(fx + x), str(fy + nach_y)],
                   capture_output=True)
    time.sleep(1.2)
    if not seh.finde("Bestellungen", ueber=220):                 # Kopfzeile weg → Karte ist oben
        return
    # Reserve (2. MacBook, 09.11.2026): Ziehen wirkt dort nicht, Mausrad schon – mind. ~10 Rasten, sonst passiert nichts.
    # Richtung hängt an „Natürliches Scrollen“: aus (0) → negativ schiebt den Inhalt hoch.
    nat = subprocess.run(["defaults", "read", "-g", "com.apple.swipescrolldirection"], capture_output=True, text=True).stdout.strip()
    erst = -10 if nat == "0" else 10
    for dy in (erst, -erst):
        subprocess.run([str(HIER / "bin" / "zeiger"), "rel", "0.5", "0.55"], capture_output=True)
        subprocess.run([sys.executable, str(PROJ / "geraet" / "geraet.py"), "MOVE 4 0", "MOVE -4 0", f"SCROLL 0 {dy} 15 15"],
                       capture_output=True)
        time.sleep(1.5)
        if not seh.finde("Bestellungen", ueber=220):
            log(f"Karte per Mausrad hochgeschoben (SCROLL 0 {dy})"); return


def stapel(liste_pfad):
    """Viele Produkte am Stück: JSON-Liste [{"id": "...", "name": "kurzname", "produkt": "Produktname", "ziel": "…/Belege/x"}].
    Schon geholte (ziel/produkt.json vorhanden) werden übersprungen → nach Abbruch einfach neu starten.
    Eine Zeile pro Produkt; ein Fehler stoppt nicht den ganzen Stapel. Am Ende: Liste der Fehler."""
    import json
    liste = json.loads(pathlib.Path(liste_pfad).read_text())
    fehler = []
    t0 = time.time()
    for i, e in enumerate(liste, 1):
        ziel = pathlib.Path(e["ziel"]) if e.get("ziel") else PROJ / "uebergabe" / "ausgang" / e["name"]
        if (ziel / "produkt.json").exists():
            print(f"{i}/{len(liste)} = {e['name']} (schon da)", flush=True); continue
        t = time.time()
        r = subprocess.run([sys.executable, __file__, e["id"], e["name"], e.get("produkt", e["name"])] + ([str(ziel)] if e.get("ziel") else []),
                           capture_output=True, text=True)
        n = len(list(ziel.glob("bild-*.png"))) if ziel.exists() else 0
        if r.returncode:
            grund = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["?"])[-1]
            fehler.append((e["name"], grund)); print(f"{i}/{len(liste)} ✗ {e['name']}: {grund}", flush=True)
        else:
            print(f"{i}/{len(liste)} ✓ {e['name']}: {n} Bilder, {time.time() - t:.0f} s", flush=True)
    print(f"FERTIG {len(liste) - len(fehler)}/{len(liste)} in {(time.time() - t0) / 60:.1f} min" +
          ("".join(f"\n  ✗ {n}: {g}" for n, g in fehler)), flush=True)
    sys.exit(1 if fehler else 0)


def main(a):
    if a[:1] == ["--stapel"] and len(a) == 2:
        return stapel(a[1])
    if len(a) < 2:
        sys.exit(__doc__)
    pid, name = a[0], a[1]
    produkt = a[2] if len(a) > 2 else name
    ziel = pathlib.Path(a[3]) if len(a) > 3 else None
    try:
        zur_galerie(pid, produkt)
    except Stopp as e:
        sys.exit(f"STOPP: {e}")
    tts = f"https://shop.tiktok.com/view/product/{pid}"
    s1 = f"https://www.social1.ai/products/{pid}"
    if seh.kabel():
        try:
            galerie_kabel(name, produkt, s1, tts)
        except Stopp as e:
            sys.exit(f"STOPP: {e}")
    else:
        r = subprocess.run(["zsh", str(HIER / "galerie.sh"), name, produkt, s1, tts])
        if r.returncode:
            sys.exit("STOPP: galerie.sh abgebrochen")
    quelle = PROJ / "uebergabe" / "ausgang" / name
    if ziel:
        ziel.mkdir(parents=True, exist_ok=True)
        for f in quelle.iterdir():
            shutil.copy2(f, ziel / f.name)
        log(f"kopiert nach {ziel}")
    taps(23, 57 if seh.kabel() else 92, "w0.5")                 # Galerie schließen (oben links)


if __name__ == "__main__":
    main(sys.argv[1:])
