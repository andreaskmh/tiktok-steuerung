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


# 16.11.2026: Postbarkeit schon beim Stock-Holen prüfen (Texte wie in post_mensch.py), nur LESEN, nie tippen.
STATUS = {}
NV_TEXTE = ("artikel nicht verfügbar", "artikel nicht verfugbar", "produkt nicht verfügbar", "produkt nicht verfugbar",
            "nicht mehr verfügbar", "nicht mehr verfugbar")
AUSV_TEXTE = ("nicht vorrätig", "nicht vorratig", "ausverkauft")
NEUKUNDE_TEXTE = ("neukunden-angebot", "neukundenangebot", "angebot für neukund", "neukund*innen", "neukund:innen",
                  "neukundinnen", "für neukunden")


class NichtVerfuegbar(Exception):
    pass


def status_neu():
    return {"provision": None, "vorraetig": None, "neukunden": None, "hinweis": ""}


def status_lesen(st, tx):
    """Reine Funktion: Texte der Produktseite → Status-Felder ergänzen (einmal erkannt = bleibt; nichts antippen)."""
    t = " ".join(x[0].lower() for x in tx)
    hinw = []
    if "provisionsberechtigt" in t and ("nicht provisionsberechtigt" in t or "nicht provisions" in t):
        st["provision"] = False; hinw.append("nicht provisionsberechtigt")
    elif "pro verkau" in t or ("verdiene" in t and "€" in t):
        if st["provision"] is None:
            st["provision"] = True
    if any(w in t for w in NV_TEXTE):
        st["vorraetig"] = False; hinw.append("Artikel nicht verfügbar")
    elif any(w in t for w in AUSV_TEXTE):
        st["vorraetig"] = False; hinw.append("ausverkauft/nicht vorrätig")
    if any(w in t for w in NEUKUNDE_TEXTE):
        st["neukunden"] = True; hinw.append("Neukunden-Angebot")
    for h in hinw:
        if h not in st["hinweis"]:
            st["hinweis"] = (st["hinweis"] + ", " + h).strip(", ")
    return st


def _norm(s):
    import re, unicodedata
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("ß", "ss")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def name_passt(produkt, zeilen):
    """Reine Funktion: steht das Produkt auf der Social1-Seite? Social1 kürzt Titel mit „…“ – Treffer, wenn
    (a) eine Zeile (ohne „…“, ≥ 8 Zeichen) der Anfang des Namens ist bzw. der Name der Anfang der Zeile, oder
    (b) die ersten zwei Namenswörter (≥ 3 Zeichen, Akzente egal) in EINER Zeile stehen, das zweite darf dort angeschnitten
    sein (≥ 3 Zeichen). Ein einzelnes Wort irgendwo reicht nur bei einwortigen Namen → kein altes Produkt rutscht durch."""
    n = _norm(produkt)
    if not n:
        return True
    w = [x for x in n.split() if len(x) >= 3] or n.split()
    for z in zeilen:
        roh = z.replace("…", " ").replace("...", " ")
        l = _norm(roh)
        if len(l) >= 8 and (n.startswith(l) or l.startswith(n)):
            return True
        lw = [x for x in l.split() if len(x) >= 3] or l.split()
        if len(w) == 1:
            if w[0] in lw or (len(w[0]) >= 5 and w[0] in l):
                return True
            continue
        for i in range(len(lw) - 1):
            if lw[i] == w[0] and (lw[i + 1] == w[1] or (len(lw[i + 1]) >= 3 and w[1].startswith(lw[i + 1]))
                                  or lw[i + 1].startswith(w[1])):
                return True
    return False


def status_zeile(st):
    if not st:
        return ""
    w, info = [], ""
    if st.get("neukunden"):                                      # Neukunden-Preis auf der Seite = kein Hindernis, nur Info
        info = " (Neukunden-Angebot)"
    if st.get("provision") is False:
        w.append("nicht provisionsberechtigt")
    if st.get("vorraetig") is False:
        w.append("nicht vorrätig/verfügbar")
    if st.get("provision") is None and st.get("vorraetig") is not False:
        w.append("Provision unklar")
    return ((" ⚠ " + ", ".join(w)) if w else "") + info


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
    for _ in range(20):                                          # auch Social1 zeigt kurz noch das alte Produkt
        s1 = [t for t, _, _ in seh.lesen()]
        if name_passt(produkt, s1):
            break
        time.sleep(1)
    else:
        raise Stopp(f"Social1 zeigt nicht das Produkt „{produkt}“")
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
        if any(w in txt for w in NV_TEXTE):                      # Seite „Produkt nicht verfügbar“ → keine Galerie
            st = status_neu(); status_lesen(st, tx); STATUS.update(st)
            raise NichtVerfuegbar(st["hinweis"] or "Produkt nicht verfügbar")
        if any(g in txt for g in ("kasse", "jetzt kaufen", "verdiene")) and (not shop or any(w in txt for w in shop)):
            break
        time.sleep(0.5)
    else:
        raise Stopp(f"TikTok-Produktseite von {sorted(shop)} nicht erreicht (alte Seite offen?)")
    log("Produktseite passt (Shop gefunden)")
    st = status_neu()
    for _ in range(8):                                           # Badge „Verdiene … pro Verkauf“ lädt verzögert (~1–3 s)
        status_lesen(st, tx)
        if st["provision"] is not None:
            break
        time.sleep(0.4); tx = seh.lesen()
    ziehe_hoch(450, 110)                                         # Vorschaukarte zur vollen Seite hochziehen
    time.sleep(1.0)
    tx2 = seh.lesen()
    status_lesen(st, tx2)                                        # volle Seite: Neukunden-Angebot, Vorrat (nur LESEN)
    belege = [t for t, _, _ in tx + tx2 if any(w in t.lower() for w in ("neukund", "provision", "pro verkau", "vorrät",
                                                                         "ausverkauft", "verfügbar"))]
    if belege:
        log(f"Status-Belege: {sorted(set(belege))}")
    if st["vorraetig"] is None and st["provision"] is not None:
        st["vorraetig"] = True                                   # Seite geladen, kein Ausverkauft-Hinweis
    STATUS.update(st)
    log(f"Status: {st}")
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
               "bilder": bilder, "anzahl_laut_galerie": n, "quelle": "kabel", "status": STATUS or status_neu()},
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
            try:
                st = json.loads((ziel / "produkt.json").read_text()).get("status")
            except Exception:
                st = None
            print(f"{i}/{len(liste)} ✓ {e['name']}: {n} Bilder, {time.time() - t:.0f} s{status_zeile(st)}", flush=True)
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
    tts = f"https://shop.tiktok.com/view/product/{pid}"
    s1 = f"https://www.social1.ai/products/{pid}"
    try:
        zur_galerie(pid, produkt)
    except Stopp as e:
        sys.exit(f"STOPP: {e}")
    except NichtVerfuegbar as e:                                 # keine Galerie → produkt.json nur mit Status (Stapel: „schon da“)
        import datetime, json
        for d in [PROJ / "uebergabe" / "ausgang" / name] + ([ziel] if ziel else []):
            d.mkdir(parents=True, exist_ok=True)
            json.dump({"version": 1, "produkt": produkt, "social1_link": s1, "tts_link": tts,
                       "geholt_am": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                       "bilder": [], "anzahl_laut_galerie": 0, "quelle": "kabel", "status": STATUS},
                      open(d / "produkt.json", "w"), ensure_ascii=False, indent=2)
        log(f"⚠ {e} – keine Bilder, nur Status gespeichert")
        return
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
