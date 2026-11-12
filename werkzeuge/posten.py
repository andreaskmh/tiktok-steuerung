#!/usr/bin/env python3
"""Ganzer Post am Stück – sieht selbst per Texterkennung (seh.py), Claude muss nicht zwischendurch schauen.

  python3 werkzeuge/posten.py <stapel.json> [nr ...]     # alle (oder nur die genannten Nummern, ab 1)

stapel.json:
  {"account": "artur.official",
   "videos": [{"datei": "/…/Video … - 15 Rock Shorts - V4.MP4",
               "kachel": "KEIN ROCK",              # Text auf dem Vorschaubild (Galerie + Profil)
               "produkt": "HOSENROCK",             # Teil des Namens im Showcase
               "tts_id": "1729926696937953544",
               "button": "Wenige auf Lager",       # ≤ 20 Zeichen, keine Emojis
               "text": "Beschreibung #hashtags ",  # ohne Emojis, ohne Preis
               "brand": "Seamless Fashion",        # Suchwort bei @ Erwähnung
               "handle": "seamlessfashion",        # genauer Nutzername in der Trefferliste
               "ausverkauft": false}]}             # true → ohne Link, nur als Entwurf speichern

Jeder Schritt wird per Texterkennung geprüft. Passt etwas nicht, bricht das Skript sofort ab (STOPP …) und
tippt nichts mehr – dann schaut Claude per Foto nach. Kein Abstand zwischen Posts, Like + Speichern ohne Kontrolle.
Produkt im Showcase ausverkauft (oder ausverkauft: true) → Video mit Text + Brand als ENTWURF, ohne Link.
Vorher: Videos in der iPhone-Galerie (Fotos), iPhone entsperrt (Kabel: open-iphone-use serve, docs/KABEL.md).
"""
import datetime, json, pathlib, random, re, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh, tap as T

PROJ = HIER.parent


class Stopp(Exception):
    pass


def taps(*a):
    T.main([str(x) for x in a])


def K():
    return seh.kabel()


_MAC_TASTEN = {51: "backspace", 36: "return", 53: "escape", 48: "tab", 117: "delete"}


def oben(y):
    """TikTok-Kopfbereich: per Kabel liegt alles ~35 Pkt höher als im alten Fenster (gemessen 12.11.2026: X/Zurück 92 → 57)."""
    return y - 35 if K() else y


def front():
    if K():
        return
    subprocess.run(["open", "-b", "com.apple.ScreenContinuity"]); time.sleep(0.2)


def key(code, n=1):
    if K():
        if code == 51:
            return K().loeschen(n)
        for _ in range(n):
            K().taste(_MAC_TASTEN[code])
        return
    front()
    subprocess.run(["osascript", "-e",
        f'tell application "System Events" to repeat {n} times\nkey code {code}\ndelay 0.02\nend repeat'])


def schnell(text):
    """Auf einen Schlag (Adressleiste, Suche am iPhone). Langsam tippen nur in TikTok (tippe)."""
    if K():
        return K().text(text)
    front()
    esc = text.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{esc}"'])


def tippe(text):
    """Zeichen einzeln wie ein schneller Mensch (45–140 ms, selten kurze Denkpause). Keine Emojis."""
    if K():
        return K().text(text, menschlich=True)
    front()
    for ch in text:
        esc = ch.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{esc}"'])
        time.sleep(random.uniform(0.045, 0.14) + (random.uniform(0.2, 0.5) if random.random() < 0.04 else 0))


def muss(f, was):
    if not f:
        raise Stopp(was)
    return f


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- Schritte

def profil(account):
    taps(306, 681, "w1.8")
    if seh.finde("Nicht erlauben"):
        x, y = seh.finde("Nicht erlauben"); taps(x, y, "w1.2")
    if not seh.warte("@" + account, 4):
        raise Stopp(f"Profil zeigt nicht @{account} – Account wechseln (Name oben antippen)")


def hochladen(kachel):
    taps(167, 681, "w1.8")
    if seh.finde("Kamera") and seh.finde("OK", genau=True):     # Hinweis „Kamera nicht verfügbar“ (Kabel: Kamera läuft)
        muss(seh.finde("OK", genau=True), "Kamera-Hinweis ohne OK-Knopf")
        x, y = seh.finde("OK", genau=True); taps(x, y, "w0.8")
    taps(30, 672, "w1.8")                                       # Galerie unten links
    treffer = [t for t in seh.alle(kachel) if 140 < t[2] < 660]
    if len(treffer) != 1:
        raise Stopp(f"Kachel „{kachel}“ {len(treffer)}× in der Galerie gefunden")
    _, x, y = treffer[0]
    spalte = min(2, max(0, int((x - 8) // 107.5)))
    taps(8 + 107.5 * (spalte + 1) - 12, y - 18, "w1.0")       # Auswahlkreis oben rechts der Kachel
    muss(seh.warte("Weiter", 3, unter=650), "Video nicht ausgewählt (kein Weiter)")
    taps(242, 680, "safe", "w2.5")                              # Weiter → Editor (nur EINMAL)
    if not seh.finde("Link hinzufügen"):
        muss(seh.warte("Deine Story", 4), "Editor nicht erreicht")
        taps(242, 680, "safe", "w2.5")                          # Weiter → Beitragsseite (nur EINMAL)
    muss(seh.warte("Link hinzufügen", 4), "Beitragsseite nicht erreicht")


def verlinken(produkt, button):
    _, y = muss(seh.finde("Link hinzufügen"), "Link hinzufügen fehlt")
    taps(110, y, "w1.3")
    x, y = muss(seh.warte("Produkt", 3, genau=True, unter=450), "Auswahl Produkt fehlt")
    taps(90, y, "w2.2")
    for _ in range(10):
        tx = seh.lesen()
        if seh.finde("verstanden", tx):
            x, y = seh.finde("verstanden", tx); taps(x, y, "w1.2"); continue
        if seh.finde("Dein Showcase", tx):
            break
        time.sleep(0.4)
    tx = seh.lesen()
    _, _, ny = muss((seh.alle(produkt, [t for t in tx if t[2] > 180]) or [None])[0],
                    f"„{produkt}“ nicht oben im Showcase → Einkaufswagen-Weg")
    zeile = " | ".join(t for t, _, y in tx if ny - 5 <= y <= ny + 120)
    by = seh.finde("Hinzufügen", tx, genau=True, unter=ny, ueber=ny + 120)
    if AUSVERKAUFT.search(zeile) or not by:
        log(f"AUSVERKAUFT? „{zeile}“ → Entwurf ohne Link")
        taps(25, oben(90), "w1.5")                              # zurück aus der Showcase-Liste
        muss(seh.warte("Veröffentlichen", 3, unter=640), "nach Zurück nicht auf der Beitragsseite")
        return False
    _, by = by
    taps(264, by, "w2.0")
    tx = seh.lesen()
    d = seh.finde("zum Video", tx)
    if d:
        _, y = muss(seh.finde("Hinzufügen", tx, genau=True, unter=d[1]), "Dialog ohne Hinzufügen")
        taps(167, y, "w2.0")
    muss(seh.warte("Produkt umbenennen", 3), "Seite Produkt umbenennen fehlt")
    key(51, 32)                                                 # Feld ist schon aktiv: sofort löschen
    tippe(button)
    time.sleep(0.4)
    muss(seh.aehnlich(button), f"Button-Text „{button}“ nicht im Feld")
    taps(167, 678, "safe", "w2.2")
    muss(seh.warte("Veröffentlichen", 3, unter=640), "nach Hinzufügen nicht auf der Beitragsseite")
    muss(seh.aehnlich(button), "Produkt-Link fehlt auf der Beitragsseite")
    return True


def beschreiben(text, brand, handle):
    taps(110, oben(128), "w0.5")
    tippe(text)
    time.sleep(0.5)
    x, y = muss(seh.finde("Erwähnung"), "@ Erwähnung fehlt")
    taps(x, y, "w1.3", 160, 166, "w0.4")
    tippe(brand)
    if handle:
        f = seh.warte(handle, 4, genau=True, unter=180)
    else:                                                       # ohne Nutzername: Shop-Name muss eindeutig sein
        time.sleep(2.0)
        tr = seh.alle(brand, [t for t in seh.lesen() if t[2] > 180], genau=True)
        if len(tr) > 1:
            raise Stopp(f"„{brand}“ {len(tr)}× in der Trefferliste – Nutzername (handle) angeben")
        f = (tr[0][1], tr[0][2] + 9) if tr else None           # Name-Zeile liegt ~18 über der Nutzername-Zeile
    if not f:
        namen = [t for t, _, _ in seh.lesen()][:25]
        raise Stopp(f"@{handle} nicht in der Trefferliste: {namen}")
    taps(140, f[1] - 9, "w1.4", "safe")
    tx = seh.lesen()
    muss(seh.finde("Veröffentlichen", tx, unter=640), "nach Brand-Wahl nicht auf der Beitragsseite")
    muss(seh.finde("@", tx, ueber=250), "Brand-Markierung fehlt in der Beschreibung")


AUSVERKAUFT = re.compile(r"ausverkauft|nicht verfügbar|nicht vorrätig|(^|[^\d.,])0 auf Lager", re.I)


def entwurf_speichern():
    x, y = muss(seh.finde("Entwürfe", unter=640, ueber=720), "Knopf Entwürfe fehlt")
    muss(x < 167, "Entwürfe nicht links – Abbruch (Veröffentlichen-Gefahr)")
    taps(x, y, "w2.5")
    if seh.finde("Veröffentlichen", unter=640):
        raise Stopp("Entwurf nicht gespeichert – Beitragsseite noch offen")


def veroeffentlichen():
    taps(242, 680, "safe", "w3.0")
    for _ in range(3):
        tx = seh.lesen()
        z = seh.finde("zustimmen", tx)
        if z:
            taps(z[0], z[1], "w1.5")
            if seh.finde("Veröffentlichen", unter=640):
                taps(242, 680, "safe", "w3.0")
            continue
        if not seh.finde("Veröffentlichen", tx, unter=640):
            return
        time.sleep(1)
    raise Stopp("Beitragsseite noch offen – nicht veröffentlicht?")


def liken(account, kachel):
    profil(account)
    if seh.finde("Neueste", genau=True):                        # Sortiermenü offen → schließen
        x, y = seh.finde("Neueste", genau=True); taps(x, y, "w0.8")
    else:
        taps(36, 310, "w1.2")                                   # Video-Reiter
        if seh.finde("Neueste", genau=True):
            x, y = seh.finde("Neueste", genau=True); taps(x, y, "w0.8")
    f = seh.finde(kachel, unter=330, ueber=660)
    if not f:
        raise Stopp(f"neues Video „{kachel}“ im Profil nicht gefunden – Like/Speichern fehlt")
    taps(f[0], f[1] + 20, "w2.0")
    _, ty = muss(seh.warte("Teilen", 3, genau=True, unter=400), "Video nicht offen – Like/Speichern fehlt")
    taps(302, ty - 171, "w0.6", 302, ty - 69, "w0.8", 23, 92, "w0.8")   # Herz, Lesezeichen, zurück


# ---------------------------------------------------------------- Ablauf

def eintragen_log(account, v, start):
    tag = datetime.date.today().isoformat()
    p = PROJ / "uebergabe" / "ausgang" / f"posts-{tag}.json"
    d = json.loads(p.read_text()) if p.exists() else {"datum": tag, "posts": [], "zaehler": {}}
    d["posts"].append({"zeit": time.strftime("%H:%M"), "account": account, "datei": pathlib.Path(v["datei"]).name,
                       "produkt": v["produkt"], "tts_link": f"https://shop.tiktok.com/view/product/{v.get('tts_id', '?')}",
                       "brand": "@" + v["handle"], "button": v["button"], "dauer_s": round(time.time() - start)})
    z = d["zaehler"].get(account, 0)
    d["zaehler"][account] = z + 1 if isinstance(z, int) else z
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1))


def ein_post(account, v):
    start = time.time()
    r = subprocess.run(["zsh", str(HIER / "gepostet.sh"), "pruefen", v["datei"]], capture_output=True, text=True)
    if r.returncode != 0:
        raise Stopp(f"Doppel-Schutz: {r.stdout.strip()}")
    profil(account);                     log("Account ok")
    hochladen(v["kachel"]);              log("Beitragsseite")
    verlinkt = False if v.get("ausverkauft") else verlinken(v["produkt"], v["button"])
    log("Produkt verlinkt" if verlinkt else "OHNE Link (ausverkauft)")
    beschreiben(v["text"], v["brand"], v["handle"]); log("Text + Brand")
    if not verlinkt:
        entwurf_speichern(); log("ALS ENTWURF GESPEICHERT (ausverkauft)")
        eintragen_log(account, dict(v, button="– (Entwurf, ausverkauft)"), start)
        return "entwurf"
    veroeffentlichen();                  log("VERÖFFENTLICHT")
    subprocess.run(["zsh", str(HIER / "gepostet.sh"), "eintragen", v["datei"], account])
    eintragen_log(account, v, start)
    try:
        liken(account, v["kachel"]);     log("geliked + gespeichert")
    except Stopp as e:
        log(f"Hinweis: {e}")             # Post ist trotzdem fertig
    log(f"fertig in {time.time() - start:.0f} s")
    return "gepostet"


def main(a):
    if not a:
        sys.exit(__doc__)
    s = json.loads(pathlib.Path(a[0]).read_text())
    nummern = [int(n) for n in a[1:]] or range(1, len(s["videos"]) + 1)
    front()
    if not K() and seh.finde("gesperrt"):
        sys.exit("STOPP iPhone-Synchronisierung gesperrt – Artur: Touch ID")
    for n in nummern:
        v = s["videos"][n - 1]
        log(f"── {n}: {pathlib.Path(v['datei']).name}")
        try:
            ein_post(s["account"], v)
        except Stopp as e:
            print(f"STOPP bei {n}: {e}", flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
