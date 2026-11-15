#!/usr/bin/env python3
"""Posten wie Artur (Bildschirmaufnahmen 12.11.2026, Editing System eigene/POSTEN-ABLAUF.md) – per Kabel, Schritt für Schritt
per Text-Label auf dem Bildschirm (seh.lesen), mit Gefahren-Sperre und menschlichen Pausen.

  python3 werkzeuge/post_mensch.py <eingang.json> [--entwurf] [--ohne-airdrop] [--ohne-aufraeumen]
  python3 werkzeuge/post_mensch.py --stapel <stapel> [--entwurf] [--ohne-airdrop]   # alle „freigegeben“, Account für Account
  python3 werkzeuge/post_mensch.py --aufraeumen <eingang.json>                      # nur Social1-Lesezeichen + Fotos
  python3 werkzeuge/post_mensch.py --fotos <stapel>                                 # Gepostete des Stapels aus Fotos löschen löschen

Pro Video:  (Account prüfen/wechseln) → Safari social1.ai/products/<id> → „View on TikTok Shop“ → (Banner „ÖFFNEN“) →
            Showcase über „… pro Verkauf“, sonst Einkaufswagen (verfügbare Variante) → Produktseite zu → „+“ → Galerie →
            Video (Hook-Titel) → Auswählen → Weiter → Weiter → Beschreibung menschlich tippen → Link → Produkt →
            Showcase oben bzw. Weitere Produkte → Einkaufswagen → Hinzufügen → (@Brand, nur wenn Konto da) →
            Veröffentlichen (--entwurf: „Entwürfe“) → Social1-Lesezeichen am Mac abhaken; am Stapel-Ende alle Videos in Fotos löschen.
Gefahren-Sperre: nie in der Nähe von Kasse, Jetzt kaufen, LIVE, Konto hinzufügen, Delete; CAPTCHA → STOPP.
Ausgabe: eine Zeile pro Schritt mit Sekunden, am Ende „✓ <datei> 84 s“ bzw. „STOPP …“ (dann Foto: kabel.py foto).
"""
import re
import datetime, json, os, pathlib, random, re, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh, tap as T

PROJ = HIER.parent
EIN = PROJ / "uebergabe" / "eingang"
AUS = PROJ / "uebergabe" / "ausgang"
PFLICHT = ["#tiktokshopblackfriday", "#superdeals", "#livedeals"]      # bis 30.11.2026 (Artur)
PILOT = {"andreas.testet": 3}                                          # Shopping-Videos pro Tag
REIHENFOLGE = ["anduri.official", "ella_robinson2", "andreas.testet", "artur.official", "andreasfastlane"]
T0 = time.time()


class Stopp(Exception):
    pass


def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {time.time() - T0:5.0f}s {msg}", flush=True)


def K():
    k = seh.kabel()
    if not k:
        raise Stopp("Kabel-Steuerung nicht aktiv (open-iphone-use serve, iPhone entsperrt?)")
    return k


def muss(f, was):
    if not f:
        raise Stopp(was)
    return f


def ruhe(a, b=None):
    """Menschliche Pause: a..b Sekunden (b fehlt → a ± 25 %)."""
    b = b if b is not None else a * 1.25
    time.sleep(random.uniform(a * 0.8 if b == a * 1.25 else a, b))


# ---------------------------------------------------------------- Sehen + Gefahren-Sperre

CAPTCHA = ("puzzle", "schieberegler", "captcha", "verifizier", "ziehe den", "drag the slider", "sicherheitsüberprüfung",
           "bestätige, dass du", "bist du ein mensch")


def _gefahr(t):
    s = t.lower().strip()
    if any(w in s for w in ("kasse", "jetzt kaufen", "konto hinzufügen", "live gehen", "live-event", "live event",
                            "live-aufnahme", "go live")):
        return True
    if re.fullmatch(r"[^a-z0-9]{0,2}[lıiç1|]{1,2}[i1l|]?v[e3]?", s) or re.fullmatch(r"l[i1]ve.{0,3}", s):
        return True                                              # „LIVE“-Symbol (OCR: „ÇIVE“, „LIV“ …)
    return s in ("delete", "kaufen", "registrieren", "abmelden", "event erstellen")


FEED = ("für dich", "gefolgt", "in der nähe", "entdecken")


def _feed(tx):
    """TikTok-Feed: oben links liegt das LIVE-Symbol → dort nie tippen."""
    return any(f in t.lower() for t, _, y in tx if y < 100 for f in FEED)


def _captcha(tx):
    alles = " ".join(t.lower() for t, _, _ in tx)
    alles = re.sub(r"verifiziert\w*", "", alles)   # „Von TikTok verifiziert“ (Shop-Abzeichen) ist kein CAPTCHA
    return next((w for w in CAPTCHA if w in alles), None)


def _melden(text):
    try:
        subprocess.run(["osascript", "-e", f'display notification "{text}" with title "TikTok-Posten" sound name "Glass"'],
                       timeout=10)
    except Exception:
        pass


def _bild_aktuell(tx):
    """Artur 15.11.2026: eingefrorenes Bild → Tipps landeten auf LIVE. iPhone-Uhr oben links mit Mac-Uhr vergleichen."""
    uhr = [t[0].strip() for t in tx if t[2] < 30 and t[1] < 80 and re.fullmatch(r"\d{1,2}:\d{2}", t[0].strip())]
    if not uhr:
        return True
    h, m = map(int, uhr[0].split(":"))
    jetzt = datetime.datetime.now()
    ist = (h % 12) * 60 + m
    soll = (jetzt.hour % 12) * 60 + jetzt.minute
    d = min((ist - soll) % 720, (soll - ist) % 720)
    return d <= 1


def lesen():
    """CAPTCHA: nie selbst lösen, aber auch nicht abbrechen (Artur 13.11.2026: „soll automatisiert gehen“) –
    melden, warten bis Artur es gelöst hat, dann am aktuellen Bildschirm weitermachen."""
    tx = seh.lesen()
    if not _bild_aktuell(tx):
        time.sleep(3); tx = seh.lesen()
        if not _bild_aktuell(tx):
            raise Stopp("iPhone-Bild eingefroren (Uhr im Bild ≠ jetzt) – nichts getippt")
    w = _captcha(tx)
    if not w:
        return tx
    print(f"CAPTCHA/Prüfung am Bildschirm („{w}“) – warte, bis Artur sie gelöst hat …", flush=True)
    _melden("CAPTCHA am iPhone – bitte lösen, danach geht es von selbst weiter")
    start = time.time(); letzte = start
    while time.time() - start < 45 * 60:
        time.sleep(8)
        tx = seh.lesen()
        if not _captcha(tx):
            print(f"CAPTCHA gelöst nach {time.time() - start:.0f} s – weiter", flush=True)
            ruhe(2)
            return seh.lesen()
        if time.time() - letzte > 5 * 60:
            _melden("CAPTCHA wartet noch – bitte am iPhone lösen"); letzte = time.time()
    raise Stopp(f"CAPTCHA/Prüfung („{w}“) seit 45 min ungelöst – Artur, bitte lösen, dann neu starten")


def tipp(x, y, tx=None, was="", abstand=38, zitter=3):
    """Ein Tipp mit Gefahren-Sperre (kein Gefahren-Label im Umkreis) und leicht zufälligem Punkt."""
    tx = lesen() if tx is None else tx
    jetzt = lesen()                                             # 15.11.: vor jedem Tipp frisches Bild (Uhr-Prüfung in lesen)
    if x < 70 and y < 110 and (_feed(tx) or _feed(jetzt)):
        raise Stopp(f"Gefahren-Sperre: oben links im Feed liegt LIVE – {was or 'Tipp'} nicht getippt")
    for t, gx, gy in tx:
        if _gefahr(t) and ((gx - x) ** 2 + (gy - y) ** 2) ** 0.5 < abstand:
            raise Stopp(f"Gefahren-Sperre: „{t}“ zu nah an {was or 'Tipp'} ({x:.0f},{y:.0f}) – nichts getippt")
    T.main([str(round(x + random.uniform(-zitter, zitter), 1)), str(round(y + random.uniform(-zitter / 2, zitter / 2), 1))])


def finde(muster, tx=None, **kw):
    return seh.finde(muster, lesen() if tx is None else tx, **kw)


NEU_LADEN = ("Erneut versuchen", "Tippe, um es erneut", "Tippen zum Neuladen", "Neu laden", "Wiederholen", "Aktualisieren")


def neu_laden_tippen(tx):
    """Artur 13.11.2026: Showcase/Shop lädt mit Fehler → Neu-laden-Knopf antippen statt warten."""
    for m in NEU_LADEN:
        r = seh.finde(m, tx)
        if r:
            K().tipp(r[0], r[1]); log(f"Ladefehler → „{m}“ angetippt"); time.sleep(1.5)
            return True
    return False


def warte(muster, sek=6.0, **kw):
    """Wartet auf ein Label → (x, y, texte) oder None."""
    ende = time.time() + sek
    while True:
        tx = lesen()
        f = seh.finde(muster, tx, **kw)
        if f:
            return f[0], f[1], tx
        if neu_laden_tippen(tx):
            ende += 3; continue
        if time.time() > ende:
            return None
        time.sleep(0.25)


def tippe_label(muster, sek=6.0, was=None, dx=0, dy=0, **kw):
    f = muss(warte(muster, sek, **kw), f"„{muster}“ nicht gefunden")
    tipp(f[0] + dx, f[1] + dy, f[2], was or muster)
    return f


def schnell(text):
    """Suchfelder/Adressleiste: erst leeren, dann auf einmal (nicht in TikTok)."""
    k = K()
    k.taste("cmd+a"); time.sleep(0.12); k.taste("backspace"); time.sleep(0.12)
    k.text(text)


def menschlich(text):
    K().text(text, menschlich=True)


# ---------------------------------------------------------------- Apps (kein App-Umschalter übers Kabel)

def home():
    k = K()
    k.taste("home"); time.sleep(0.5)
    k.taste("home"); time.sleep(0.7)


def _ist_app(name, tx=None):
    """Grob erkennen, ob die App schon vorn ist (13.11.: nicht jedes Mal über die Suche neu öffnen)."""
    tx = tx or lesen()
    if name == "TikTok":
        return _tabs(tx) or bool(seh.finde("Link hinzufügen", tx) or seh.finde("Kasse", tx, unter=600))
    if name == "Safari":
        return bool(seh.finde("social1", tx) or seh.finde("View on TikTok Shop", tx) or seh.finde("Saved Videos", tx))
    return False


def app(name):
    """App nach vorn. Artur 13.11.: schon vorn → bleiben; sonst Wisch an der unteren Kante (vorige App), sonst Suche."""
    if _ist_app(name):
        return
    tx = seh.lesen()                                             # 15.11.2026: nach AirDrop offene Fotos-Ansicht →
    z = [t for t in tx if t[2] < 42 and t[1] < 110 and name.lower() in t[0].lower()]   # Statusleisten-Link „◂ TikTok“
    if z:
        T.main([str(round(z[0][1], 1)), str(round(z[0][2], 1))]); ruhe(1.4)
        if _ist_app(name):
            log(f"{name} per Zurück-Link oben links"); return
    if name in ("TikTok", "Safari"):
        for _ in range(2):                                       # untere Kante nach rechts = zuletzt benutzte App
            K().ziehe(40, 731, 300, 731, 0.25); ruhe(0.9)
            if _ist_app(name):
                log(f"{name} per Wisch"); return
    home()
    s = muss(warte("Suchen", 3, unter=550), "Home-Bildschirm nicht erreicht (Suchen fehlt)")
    tipp(167, s[1], s[2], "Suche")
    ruhe(0.9)
    schnell(name)
    f = warte(name, 4, genau=True, ueber=330)
    if not f:                                                    # 13.11.: Text kam mal nicht an → noch einmal
        schnell(name); f = warte(name, 4, genau=True, ueber=330)
    f = muss(f, f"{name} nicht in der Suche")
    tipp(f[0], f[1] - 20, f[2], name)                            # Symbol über dem Namen
    ruhe(1.4)


# ---------------------------------------------------------------- 1) Account

PROFIL = (300, 681)                                              # untere TikTok-Leiste hat nur Symbole (keine Labels)


def farben(*punkte):
    """RGB an Punkten (334×735) im zuletzt gelesenen Bild (seh.lesen speichert es) – bin/pixel."""
    arg = [f"{v / (334.0 if i % 2 == 0 else 735.0):.4f}" for pt in punkte for i, v in enumerate(pt)]
    out = subprocess.run([str(HIER / "bin" / "pixel"), os.path.join(seh.TMP, "f.png"), *arg], capture_output=True, text=True).stdout
    return [tuple(map(int, z.split())) for z in out.splitlines()]


def kraeftig_rot(x, y):
    """Knopf kräftig rot (aktiv) statt blass rosa (lädt/inaktiv) – im zuletzt gelesenen Bild. Gemessen: aktiv 253/44/84."""
    f = farben((x, y))
    return bool(f) and f[0][0] > 225 and f[0][1] < 110 and f[0][2] < 150


def _tabs(tx=None):
    """TikTok-Hauptseite = „+“ mittig unten mit türkisem Rand links und pinkem rechts (Leiste mal schwarz, mal weiß).
    OCR liest das „+“ nicht immer → Farben im zuletzt gelesenen Bild."""
    xs = list(range(143, 158, 2)) + list(range(177, 192, 2))
    f = farben(*[(x, 681) for x in xs])
    if len(f) != len(xs):
        return False
    tuerkis = any(r < 150 and g > 170 and b > 190 for r, g, b in f[:8])
    pink = any(r > 200 and g < 150 and b > 90 for r, g, b in f[8:])
    return tuerkis and pink


def beitrag_abbrechen():
    """Artur 15.11.2026: halbfertiger Beitrag blieb offen → nächstes Video kam nicht zur Startseite (Kette von Fehlern).
    Schritt für Schritt zurück bis „Verwerfen“. Oben links nur tippen, wenn die Seite sicher KEIN Feed ist (LIVE!)."""
    for _ in range(10):
        tx = lesen()
        if _tabs(tx):
            return True
        v = seh.finde("Verwerfen", tx) or seh.finde("Neu beginnen", tx)
        if v:
            tipp(v[0], v[1], tx, "Verwerfen"); ruhe(1.5); continue
        if seh.finde("bewerben?", tx):                           # Blatt „Wie möchtest du …“ → X oben rechts (nie „LIVE gehen“)
            tipp(308, 85, tx, "Blatt zu (X)", abstand=25); ruhe(1.2); continue
        if seh.finde("Informationen zur Werbeaktion", tx):
            K().ziehe(167, 120, 167, 740, 0.35); ruhe(1.2); continue
        if _feed(tx):
            return False
        liste = seh.finde("Aus dem Showcase", tx) or seh.finde("Produktlinks hinzufügen", tx) \
            or (seh.finde("Einkaufswagen", tx, ueber=80) and seh.finde("Produkte suchen", tx))
        beitrag = seh.finde("Veröffentlichen", tx, unter=600) and seh.finde("Entwürfe", tx, unter=600)
        editor = seh.finde("AutoCut", tx) or seh.finde("Deine Story", tx)
        umben = seh.finde("Produkt umbenennen", tx)
        if liste or beitrag or editor or umben:
            tipp(18, 57, tx, "Zurück (Beitrag abbrechen)", abstand=20); ruhe(1.4); continue
        if seh.finde("Produkte bewerben", tx) or seh.finde("bewerben?", tx) or seh.finde("Informationen zur Werbeaktion", tx):
            K().ziehe(167, 120, 167, 740, 0.35); ruhe(1.2); continue   # Blatt nach unten wegwischen
        x = seh.finde("Sound hinzufügen", tx)
        if x:                                                    # Kamera → X oben links
            tipp(24, x[1], tx, "Kamera zu"); ruhe(1.4); continue
        if seh.finde("Mehrere auswählen", tx):                   # Galerie → X oben links
            tipp(28, 74, tx, "Galerie zu"); ruhe(1.2); continue
        return False
    return _tabs(lesen())


def tiktok_hauptseite():
    """TikTok vorn mit unterer Leiste (Startseite … Profil). Unbekannte Seite → X/Zurück oben links, max. 4×."""
    app("TikTok")
    if beitrag_abbrechen():                                      # 15.11.: offenen Beitrag erst sauber verwerfen
        return lesen()
    for i in range(6):
        tx = lesen()
        if _tabs(tx):
            return tx
        vv = seh.finde("verstanden", tx)
        if vv:
            tipp(vv[0], vv[1], tx, "OK, verstanden"); ruhe(0.8); continue
        if seh.finde("nicht verfügbar", tx) or seh.finde("nicht verfugbar", tx):   # Artur 15.11.: Fehlerseite → zurück
            K().ziehe(3, 400, 220, 400, 0.3); ruhe(1.2); continue
        o = seh.finde("OK", tx, genau=True)
        if o and seh.finde("Kamera", tx):
            tipp(o[0], o[1], tx, "OK"); ruhe(0.8); continue
        snd = seh.finde("Sound hinzufügen", tx)
        if snd:                                                  # Kamera-Seite → X oben links
            tipp(24, snd[1], tx, "Kamera zu"); ruhe(1.2); continue
        if seh.finde("Kasse", tx, unter=630) or seh.finde("nicht vorrätig", tx):   # 15.11.: Produktblatt offen →
            K().ziehe(167, 260, 167, 720, 0.35); ruhe(1.2); continue               # nach unten wegwischen (nie „Kasse“ tippen)
        # Artur 15.11.2026: NIE oben links „Zurück“ tippen (dort liegt LIVE) → Wisch vom linken Rand = Zurück
        if i < 4:
            K().ziehe(3, 400, 220, 400, 0.3); ruhe(1.2); continue
        app("TikTok")
    raise Stopp("TikTok-Hauptseite nicht erreicht")


_LETZTE_KACHEL = ""


def upload_abwarten(max_s=120):
    """Profil → Reiter Videos: warten, bis die Kachel des zuletzt geposteten Videos im Raster steht."""
    tipp(34, 287, None, "Reiter Videos"); ruhe(1.2)
    ende = time.time() + max_s
    while time.time() < ende:
        tx = lesen()
        if not _LETZTE_KACHEL or [t for t in tx if t[2] > 290 and _passt(_LETZTE_KACHEL, t[0])]:
            log("letztes Video ist im Profil – weiter"); return
        time.sleep(3)
    log("Upload-Warten: Zeit um – versuche trotzdem")


def konto(account):
    """Profil-Tab → @account prüfen, sonst Name ▾ oben links → Account (nie „Konto hinzufügen“)."""
    tx = tiktok_hauptseite()
    tipp(*PROFIL, tx, "Profil"); ruhe(1.5)
    for _ in range(3):
        f = warte("@" + account, 2.5)
        tx = lesen()
        kopf = [t for t in tx if t[2] < 80 and _kn(account) in _kn(t[0])]   # 15.11.: Name in der Kopfzeile = aktives Konto
        if f or kopf:
            log(f"Account {account} ✓"); return
        if seh.finde("Entwürfe", tx) or seh.finde("Angepinnt", tx):   # Profil gescrollt → hoch, dann neu prüfen
            K().ziehe(167, 250, 167, 600, 0.3); ruhe(1.0); continue
        if seh.finde("Nicht erlauben", tx):
            n = seh.finde("Nicht erlauben", tx); tipp(n[0], n[1], tx, "Nicht erlauben"); ruhe(1); continue
        if [t for t in tx if t[0].startswith("@") and t[2] < 220]:
            break
        if _tabs(tx):
            tipp(*PROFIL, tx, "Profil"); ruhe(1.5)
    tx = lesen()
    def _profil(tx):                                             # 15.11.: Profil leicht gescrollt → „Follower“ fehlt
        return seh.finde("Follower", tx) or (seh.finde("TikTok Studio", tx) and seh.finde("Showcase", tx))
    for _ in range(3):                                           # 13.11.: Tipp landete auf „Freund*innen“ → erst Profilseite sicherstellen
        if _profil(tx):
            break
        if seh.finde("Entwürfe", tx) or seh.finde("Angepinnt", tx):   # Artur 15.11.: Profil gescrollt → selbst hochscrollen
            K().ziehe(167, 250, 167, 600, 0.3); ruhe(1.0); tx = lesen(); continue
        tipp(*PROFIL, None, "Profil"); ruhe(1.5); tx = lesen()
    muss(_profil(tx), "Profilseite nicht offen")
    name = [t for t in tx if 40 < t[2] < 145 and t[1] < 230 and "@" not in t[0] and len(t[0].strip()) > 3
            and "safari" not in t[0].lower()]                      # „◂ Safari“ oben links ist kein Kontoname (12.11.)
    n = muss(name, "Account-Name oben links nicht gefunden")[0]
    breite = len(n[0].strip().rstrip("▾▼v ").strip()) * 11.5      # 13.11.: direkt aufs ▾ rechts neben dem Namen (Name-Tipp öffnet oft nicht)
    x0 = min(n[1] + breite / 2 + 10, 230)
    for dx in (0, -18, 18, -36):                                 # Pfeil-Lage schwankt je Name → ein paar Punkte probieren
        tipp(x0 + dx, n[2], None, "Konto-Pfeil ▾")
        if warte("Konto wechseln", 2):
            break
    muss(warte("Konto wechseln", 4), "„Konto wechseln“ öffnet sich nicht")
    z = vorher = None
    for _ in range(12):                                          # Liste fährt animiert auf → erst tippen, wenn sie ruht
        time.sleep(0.45)
        tx = lesen()
        z = seh.finde(account, tx, unter=300)
        if z and vorher and abs(z[1] - vorher[1]) < 3:
            break
        vorher, z = z, None
    z = muss(z, f"{account} nicht in „Konto wechseln“")
    tipp(z[0], z[1], tx, account, abstand=34)
    for _ in range(12):                                          # 13.11.: während Upload kein Kontowechsel → bestätigen, warten, nochmal
        tx = lesen()
        if seh.finde("@" + account, tx):
            break
        if seh.finde("momentan ein Video", tx):
            bs = seh.finde("Bestätigen", tx)
            if bs:
                tipp(bs[0], bs[1], tx, "Bestätigen (Upload läuft)"); ruhe(0.8)
            upload_abwarten()                                    # Artur 13.11.: im Profil schauen, ob das Video schon oben ist
            return konto(account)
        time.sleep(0.8)
    muss(warte("@" + account, 3), f"Wechsel zu {account} hat nicht geklappt")
    log(f"Account gewechselt: {account}")


# ---------------------------------------------------------------- 2) Produkt über Social1 → TikTok

def produktseite_da(tx):
    return bool(seh.finde("Kasse", tx, unter=600) and seh.finde("Einkaufswagen", tx, unter=600))


def zum_produkt(pid, produkt):
    app("Safari")
    K().taste("cmd+l"); time.sleep(0.6)                          # Adressleiste (Tipp traf dort mal das Mikrofon)
    schnell(f"social1.ai/products/{pid}"); time.sleep(0.3)
    K().taste("return")
    f = warte("View on TikTok Shop", 15)
    if not f:                                                    # 13.11.: Social1 hakt manchmal kurz → einmal neu laden
        K().taste("cmd+r"); f = warte("View on TikTok Shop", 20)
    if not f:
        raise Stopp("Social1-Seite ohne „View on TikTok Shop“ (Login? Artur)")
    worte = re.findall(r"[a-zäöüß0-9]{4,}", (produkt or "").lower())[:3]
    for _ in range(12):                                          # Social1 zeigt kurz noch das alte Produkt
        tx = lesen()
        txt = " ".join(t.lower() for t, _, _ in tx)
        if not worte or any(w in txt for w in worte):
            break
        time.sleep(0.6)
    else:
        raise Stopp(f"Social1 zeigt nicht „{produkt}“")
    s1 = [t for t, _, _ in tx]
    try:
        kopf = s1[s1.index("Promote S1") + 1: s1.index("View on TikTok Shop")]
    except ValueError:
        kopf = []
    shop = {w for t in kopf if "..." not in t and "…" not in t for w in re.findall(r"[a-z0-9äöü]{4,}", t.lower())}
    f = seh.finde("View on TikTok Shop", tx)
    tipp(f[0], f[1], tx, "View on TikTok Shop")
    ruhe(2.0)
    getippt = 0
    for i in range(70):                                          # bis ~35 s: Banner/Dialoge, TikTok lädt das Produkt
        tx = lesen()
        if seh.finde("nicht mehr verfügbar", tx) or seh.finde("Produkt nicht verfügbar", tx) \
           or seh.finde("Artikel nicht verfügbar", tx) or seh.finde("Artikel nicht verfugbar", tx):
            # Artur 14.11.2026: Seite „Produkt nicht verfügbar“ → Entwurf ohne Link (nicht überspringen)
            raise Stopp("Produkt nicht verfügbar – nicht vorrätig → Entwurf ohne Link")
        if produktseite_da(tx):
            txt = " ".join(t.lower() for t, _, _ in tx)
            if not shop or any(w in txt for w in shop) or any(w in txt for w in worte) or i > 24:
                return tx
        for lab in ("TikTok öffnen", "Öffnen", "ÖFFNEN", "App öffnen"):
            o = seh.finde(lab, tx, genau=True) or (seh.finde(lab, tx) if lab == "TikTok öffnen" else None)
            if o:
                tipp(o[0], o[1], tx, lab); getippt += 1; ruhe(2.5 if lab != "TikTok öffnen" else 1.5); break
        else:
            v = seh.finde("View on TikTok Shop", tx)
            if v and i % 10 == 9:                                # Tipp kam nicht an
                tipp(v[0], v[1], tx, "View on TikTok Shop"); ruhe(2.5)
            time.sleep(0.5)
    raise Stopp("TikTok-Produktseite nicht erreicht")


# ---------------------------------------------------------------- 3) Showcase oder Einkaufswagen

def showcase_oder_wagen(tx):
    # Artur 13.11.2026: „Ausverkauft“ steht unten auf der Produktseite → Showcase ja, Einkaufswagen nein, Video als Entwurf
    ausv = bool(seh.finde("Ausverkauft", tx, unter=560) or seh.finde("Nicht vorrätig", tx, unter=560))
    if ausv:
        log("Produktseite: Ausverkauft")
    v = seh.finde("pro Verkauf", tx)
    if v:
        tipp(v[0], v[1], tx, "pro Verkauf"); ruhe(1.6)
        for _ in range(12):
            tx = lesen()
            if seh.finde("verstanden", tx) and (seh.finde("nicht verfügbar", tx) or seh.finde("nicht hinzugefügt", tx)):
                vv = seh.finde("verstanden", tx); tipp(vv[0], vv[1], tx, "OK, verstanden"); ruhe(0.8)
                log("Produkt nicht verfügbar (gesperrt) → Entwurf ohne Link"); return "ausverkauft"   # Artur 13.11.
            z = seh.finde("Showcase hinzufügen", tx)
            if z:
                tipp(z[0], z[1], tx, "Zum Showcase hinzufügen"); ruhe(1.6)
                log("ins Showcase gelegt")
                return "ausverkauft" if ausv else "showcase"
            if seh.finde("Mehr erkunden", tx) or seh.finde("im Showcase", tx) or seh.finde("Jetzt erstellen", tx):
                break                                            # Artur 13.11.: „Jetzt erstellen“ = schon im Showcase
            time.sleep(0.3)
        if ausv:
            log("schon im Showcase, ausverkauft → kein Einkaufswagen"); return "ausverkauft"
        # Artur 13.11.2026 16:30: schon im Showcase → IMMER Einkaufswagen und Link aus dem Einkaufswagen (nie im Showcase suchen)
        log("schon im Showcase → Einkaufswagen")
        wa = seh.finde("Werbeaktion", lesen())
        if wa:                                                   # Blatt schließen: nach unten wischen
            K().ziehe(167, wa[1] + 10, 167, wa[1] + 420, 0.3); ruhe(1.2)
        in_wagen(lesen())
        return "wagen"
    else:
        log("kein „pro Verkauf“ → Einkaufswagen")
    in_wagen(tx)
    return "wagen"


def in_wagen(tx):
    w = muss(seh.finde("Einkaufswagen", tx, unter=600), "Einkaufswagen-Knopf fehlt")
    k = seh.finde("Kasse", tx, unter=600)
    muss(w[0] < 167 and (not k or k[0] > w[0] + 80), "Einkaufswagen nicht links neben Kasse – Lage unklar")
    tipp(w[0], w[1], tx, "Einkaufswagen (grau)"); ruhe(1.4)
    versucht = set()
    for runde in range(3):                                       # Artur 13.11.: irgendeine Variante/Größe, Hauptsache schnell
      if _wagen_runde(versucht):
          return
    raise Stopp("nicht in den Einkaufswagen gelegt")


def _wagen_runde(versucht):
    for _ in range(14):                                          # „Bitte auswählen“: erste nicht probierte Option
        tx = lesen()
        b = seh.finde("Bitte auswählen", tx)
        if not b:
            break
        opt = [t for t in tx if b[1] + 15 < t[2] < b[1] + 140 and t[0].strip() and "tabelle" not in t[0].lower()
               and (round(t[1]), round(t[2])) not in versucht]
        o = min(muss(opt, "keine wählbare Variante"), key=lambda t: (round(t[2] / 10), t[1]))
        versucht.add((round(o[1]), round(o[2])))
        tipp(o[1], o[2], tx, "Variante"); ruhe(0.5)
    probiert = set()
    for _ in range(16):                                          # „nicht vorrätig“ → andere Option der untersten Gruppe
        tx = lesen()
        if not seh.finde("nicht vorrätig", tx):
            break
        gr = seh.finde("Größe", tx) or seh.finde("Farbe", tx)
        opt = [t for t in tx if gr and gr[1] + 15 < t[2] < gr[1] + 110 and t[0].strip()
               and (round(t[1]), round(t[2])) not in probiert] if gr else []
        o = min(muss(opt, "Artikel nicht vorrätig, keine weitere Variante"), key=lambda t: (round(t[2] / 10), t[1]))
        probiert.add((round(o[1]), round(o[2])))
        tipp(o[1], o[2], tx, "Variante"); ruhe(0.9)
    tx = lesen()
    muss(not seh.finde("nicht vorrätig", tx), "Artikel nicht vorrätig (keine vorrätige Variante)")
    btn = [t for t in tx if t[2] > 600 and t[0].strip() == "Einkaufswagen"]
    muss(btn, "rotes „Einkaufswagen“ im Varianten-Blatt fehlt")
    tipp(btn[0][1], btn[0][2], tx, "Einkaufswagen (rot)"); ruhe(1.0)
    for i in range(12):
        tx = lesen()
        if seh.finde("hinzugefügt", tx) or seh.finde("Zur Kasse (", tx):
            log("im Einkaufswagen"); return True
        if seh.finde("Option pro Artikel", tx) or seh.finde("für Neukund", tx):   # Artur 12.11.: liegt schon im Wagen
            global _NEUKUNDE
            _NEUKUNDE = True
            log("schon im Einkaufswagen (Neukunden-Hinweis)"); ruhe(2.5); return True
        if seh.finde("Bitte auswählen", tx):
            log("noch eine Auswahl offen → nächste Variante"); return False
        if not seh.finde("Bitte auswählen", tx) and not [t for t in tx if t[2] > 600 and t[0].strip() == "Einkaufswagen"] and i >= 2:
            log("im Einkaufswagen (Blatt zu)"); return True      # Artur 13.11.: nicht extra in den Warenkorb gehen
        time.sleep(0.3)
    return False


# ---------------------------------------------------------------- 4) Produktseite zu → „+“ → Video

def zum_plus():
    for i in range(6):
        tx = lesen()
        if _tabs(tx):
            tipp(167, 681, tx, "+"); ruhe(1.6)
            return
        if i == 4:
            tiktok_hauptseite(); continue
        wa = seh.finde("Werbeaktion", tx) or seh.finde("Bitte auswählen", tx)
        if wa:                                                   # Blatt offen → runterwischen
            K().ziehe(167, wa[1] + 10, 167, wa[1] + 420, 0.3); ruhe(1.0); continue
        if _feed(tx):                                            # Produktkarte nur halb offen → Karte runterwischen
            K().ziehe(167, 330, 167, 720, 0.3); ruhe(1.0); continue
        K().ziehe(3, 400, 220, 400, 0.3); ruhe(1.3)            # 15.11.: nie oben links tippen (LIVE)
    raise Stopp("„+“ nicht erreicht")


_KYR = str.maketrans("ЗОАЕТСВМНКРХІ×", "3OAETCBMHKPXIX")   # 15.11.: OCR liest „З0-TEILIGES“ (kyrillisch)


def _kn(t):
    import unicodedata
    t = t.upper().translate(_KYR).replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", t))


def _passt(kachel, ocr):
    k, o = _kn(kachel), _kn(ocr)
    return bool(k) and (o.startswith(k[:max(6, len(k) - 2)]) or (len(o) >= 6 and k.startswith(o)))


_FF = str(pathlib.Path.home() / "Documents/Coding/Editing System 1.1/tools/bin") + "/"


def frisch_datiert(v):
    """Artur 14.11.2026 (Doppel-Post Nike): Fotos sortiert nach Aufnahmedatum IN der Datei, nicht nach AirDrop-Zeit →
    Kopie mit Aufnahmedatum = jetzt, damit das gesendete Video wirklich die letzte Kachel ist."""
    import tempfile
    ziel = pathlib.Path(tempfile.mkdtemp(prefix="airdrop-frisch-")) / pathlib.Path(v).name
    jetzt = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    lokal = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    subprocess.run([_FF + "ffmpeg", "-y", "-loglevel", "error", "-i", str(v), "-map", "0", "-c", "copy",
                    "-metadata", f"creation_time={jetzt}", "-metadata", f"com.apple.quicktime.creationdate={lokal}",
                    "-movflags", "use_metadata_tags", str(ziel)], check=True, timeout=300)
    return ziel


def dauer_text(v):
    """Dauer wie in der iPhone-Galerie („0:23“), gerundet."""
    r = subprocess.run([_FF + "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                       capture_output=True, text=True, timeout=60)
    return float(r.stdout.strip())


_SOLL_DAUER = None   # Sekunden des Videos, das gerade gepostet wird


def cover_pruefen(kachel):
    """Artur 15.11.2026: falsches Video = Verstoß/Kontosperre. Zweite, unabhängige Prüfung auf der Beitragsseite:
    Hook-Text im Cover (oben rechts) muss zum Video passen – sonst STOPP, bevor getippt/verlinkt/gespeichert wird."""
    for _ in range(8):
        tx = lesen()
        cover = [t for t in tx if t[1] > 200 and t[2] < 200 and not re.search(r"cover|bearbeiten", t[0], re.I)]
        if any(_passt(kachel, t[0]) for t in cover):
            log(f"Cover passt: {kachel}"); return
        time.sleep(0.5)
    raise Stopp(f"Cover zeigt nicht „{kachel}“ ({[t[0] for t in cover][:3]}) – falsches Video, NICHT gepostet")


_NEUKUNDE = False


def erstellen_route():
    """Artur 15.11.2026: Neukunden-Angebot → Produkt lässt sich nicht (neu) in den Einkaufswagen legen und steht in der
    Liste nicht oben. NUR dann: Produktseite → „pro Verkauf“ → „Jetzt erstellen“ → „Lade ein Video hoch“ → Produktname
    umbenennen → Hinzufügen → Kamera → Galerie unten rechts. Produkt ist damit schon verlinkt."""
    if not seh.finde("Lade ein Video hoch", lesen()):           # 15.11.: steht das Blatt schon offen → dort weiter
        for _ in range(4):                                       # Varianten-/Werbeblatt zu
            tx = lesen()
            if seh.finde("pro Verkau", tx, unter=520):
                break
            K().ziehe(167, 130, 167, 720, 0.35); ruhe(1.2)
        v = muss(seh.finde("pro Verkau", lesen(), unter=520), "„pro Verkauf“ auf der Produktseite fehlt")
        tipp(v[0], v[1], None, "pro Verkauf"); ruhe(1.6)
        j = muss(warte("Jetzt erstellen", 5), "„Jetzt erstellen“ fehlt")
        tipp(j[0], j[1], j[2], "Jetzt erstellen"); ruhe(2.5)
    h = muss(warte("Lade ein Video hoch", 8), "„Videos – Lade ein Video hoch“ fehlt")
    tipp(h[0], h[1], h[2], "Videos hochladen"); ruhe(2.5)
    muss(warte("Produkt umbenennen", 8), "„Produkt umbenennen“ fehlt")
    muss(warte("/30", 12) or warte("Produktname", 4, genau=True), "Produktname-Feld lädt nicht")        # 15.11.: erst tippen, wenn das Feld geladen ist
    ruhe(0.8)
    for versuch in range(2):
        tx = lesen()
        lab = muss(seh.finde("Produktname", tx, genau=True), "Feld „Produktname“ fehlt")
        tipp(200, lab[1] + 59, tx, "Produktname-Feld"); ruhe(0.8)
        K().taste("cmd+a"); ruhe(0.2); K().loeschen(1); K().loeschen(60); ruhe(0.4)
        menschlich(_BUTTON); ruhe(0.8)
        tx = lesen()
        if [t for t in tx if lab[1] + 40 < t[2] < lab[1] + 90 and _kn(t[0]) == _kn(_BUTTON)]:
            break
        log("Produktname nicht sauber – nochmal")
    else:
        raise Stopp(f"Produktname nicht „{_BUTTON}“")
    log(f"umbenannt: {_BUTTON}")
    K().taste("return"); ruhe(1.2)
    hz = muss(warte("Hinzufügen", 4, unter=600), "„Hinzufügen“ fehlt")
    tipp(hz[0], hz[1], hz[2], "Hinzufügen"); ruhe(3.0)
    muss(warte("KAMERA", 8) or warte("Sound hinzufügen", 4), "Kamera nicht offen")
    log("Produkt über „Jetzt erstellen“ verlinkt")


def video_waehlen(kachel, galerie=None):
    for _ in range(3):
        tx = lesen()
        if seh.finde("Kamera", tx) and seh.finde("OK", tx, genau=True):
            o = seh.finde("OK", tx, genau=True); tipp(o[0], o[1], tx, "OK"); ruhe(0.8); continue
        break
    if galerie:                                                  # 15.11.: Kamera aus „Jetzt erstellen“ → Galerie unten rechts
        tipp(galerie[0], galerie[1], tx, "Galerie unten rechts"); ruhe(2.0)
    else:
        tipp(30, 672, tx, "Galerie unten links", abstand=60); ruhe(1.6)
    v = None if os.environ.get("TS_EINZELN") else seh.finde("Videos", lesen(), genau=True, ueber=160)
    if v:                                                        # Artur 13.11.: im Einzel-Modus kein Reiterwechsel (neuestes steht in „Alle“)
        tipp(v[0], v[1], None, "Reiter Videos"); ruhe(1.0)
    treffer = None
    if os.environ.get("TS_EINZELN"):                             # Artur 13.11.2026: nicht nach Thumbnails suchen –
        # Video kam gerade per AirDrop = neuestes = letzte Kachel. Artur 13.11.: nicht langsam scrollen → schnelle Wischer ans Ende
        ruhe(0.3)                                                # Artur 13.11.: Galerie öffnet unten beim neuesten → kein Scrollen
        # Artur 14.11.2026: AirDrop meldet „fertig“, bevor das Video in Fotos liegt → bis 75 s warten, bis die
        # letzte Kachel die Länge des gesendeten Videos hat; sonst NICHT posten (Doppel-Post Nike)
        bis = time.time() + 75
        while True:
            tx = lesen()
            dauern = [t for t in tx if 120 < t[2] < 650 and re.fullmatch(r"\d{1,2}:\d{2}", t[0].strip())]
            muss(dauern, "keine Video-Kachel gefunden")
            def _sek(t):
                m, sk = t[0].strip().split(":"); return int(m) * 60 + int(sk)
            def _hook_ok(t):                                     # Hook-Text unter der Kachel muss passen (falls lesbar)
                unter = [u for u in tx if abs(u[1] - t[1] + 40) < 60 and 25 < t[2] - u[2] < 95
                         and not re.fullmatch(r"\d{1,2}:\d{2}", u[0].strip())]
                return any(_passt(kachel, u[0]) for u in unter)   # 15.11.: Pflicht (Steckschlüssel/Nike beide 0:18)
            # Artur 14.11.2026: Fotos sortiert AirDrops nicht zuverlässig ans Ende → neueste Kachel mit passender Länge + Hook
            if _SOLL_DAUER is None:
                passend = dauern
            else:
                passend = [t for t in dauern if abs(_sek(t) - _SOLL_DAUER) <= 1.1 and _hook_ok(t)]
            if passend:
                letzte = max(passend, key=lambda t: (round(t[2] / 20), t[1]))
                break
            letzte = max(dauern, key=lambda t: (round(t[2] / 20), t[1]))
            if time.time() > bis:
                raise Stopp(f"gesendetes Video nicht in der Galerie (letzte Kachel {letzte[0].strip()}, gesucht "
                            f"{int(_SOLL_DAUER // 60)}:{int(round(_SOLL_DAUER % 60)):02d}) – NICHT gepostet")
            log(f"keine Kachel mit {_SOLL_DAUER:.0f} s + passendem Hook – Video noch nicht in Fotos, warte")
            time.sleep(5)
        treffer = (letzte[0], letzte[1] - 40, letzte[2] - 50)
        log(f"neuestes Video (letzte Kachel) bei {treffer[1]:.0f},{treffer[2]:.0f}, Dauer {letzte[0].strip()} ✓")
    # Artur 12.11.2026: neue Videos liegen oft ganz UNTEN; große schnelle Wische nach oben schießen drüber.
    # Erst kleine, langsame Schritte nach unten (bis sich nichts mehr ändert), dann genauso langsam nach oben.
    def such():
        tx = lesen()
        tr = [t for t in tx if 140 < t[2] < 650 and _passt(kachel, t[0])]
        return tx, (min(tr, key=lambda t: (t[2], t[1])) if tr else None)
    for richtung in ((+1, -1) if not treffer else ()):
        alt = None
        for _ in range(40):
            tx, treffer = such()
            if treffer:
                break
            sig = " ".join(t[0] for t in tx)
            if sig == alt:                                       # Ende der Liste erreicht
                break
            alt = sig
            if richtung > 0:
                K().ziehe(167, 480, 167, 330, 0.6)               # Finger hoch = weiter nach unten
            else:
                K().ziehe(167, 330, 167, 480, 0.6)
            ruhe(0.9)
        if treffer:
            break
    _, x, y = muss(treffer, f"Video „{kachel}“ nicht in der Galerie")
    tipp(x, y + (0 if os.environ.get("TS_EINZELN") else 25), tx, "Video-Kachel")
    ruhe(1.4)
    a = warte("Auswählen", 4)
    if a:                                                        # Vorschau: Hook-Titel prüfen, dann Auswählen
        ok = [t for t in a[2] if _passt(kachel, t[0])] or seh.finde(kachel[:6], a[2])
        if not ok:                                               # 13.11.: Hook-Titel blendet nach ~1,5 s aus → Kachel-Treffer zählt
            log(f"Vorschau ohne Hook-Titel – Kachel „{kachel}“ war eindeutig, weiter")
        tipp(a[0], a[1], a[2], "Auswählen"); ruhe(0.9)
    w = muss(warte("Weiter", 4, unter=600), "Video nicht ausgewählt (kein Weiter)")
    muss(w[0] > 167, "„Weiter“ nicht rechts – AutoCut-Gefahr")       # 13.11.: links liegt AutoCut (Vorlage + Musik)
    tipp(w[0], w[1], w[2], "Weiter"); ruhe(2.2)
    for _ in range(3):                                           # Editor → Weiter (nicht AutoCut/Story/Sound)
        tx = lesen()
        if seh.finde("Beschreibung", tx) or seh.finde("Link hinzufügen", tx):
            return
        w = seh.finde("Weiter", tx, unter=600)
        if w and w[0] > 167:
            tipp(w[0], w[1], tx, "Weiter (Editor)"); ruhe(2.0)
        else:
            time.sleep(0.8)
    tx = muss(warte("Link hinzufügen", 4), "Beitragsseite nicht erreicht")[2]
    muss(not seh.finde("Vorlage", tx), "Vorlage/AutoCut am Video (Musik!) – Abbruch, nicht posten")   # Artur 13.11. (Sturmhaube)
    vorschau = [t for t in tx if t[1] > 220 and t[2] < 230 and _passt(kachel, t[0])]
    if not vorschau and os.environ.get("TS_EINZELN"):
        log(f"Vorschau-Text nicht gelesen („{kachel}“) – Einzel-Modus: neuestes Video, weiter")
    else:
        muss(vorschau, f"Vorschaubild zeigt nicht „{kachel}“ – falsches Video? Abbruch vor dem Posten")


# ---------------------------------------------------------------- 5) Beitrag

def tippbar(t):
    """Nur Zeichen, die das Kabel tippen kann: é→e usw., Emojis raus, Umlaute bleiben."""
    import unicodedata
    raus = []
    for c in t:
        if c in "äöüÄÖÜß" or (ord(c) < 128):
            raus.append(c)
        else:
            raus.append(unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode())
    return " ".join("".join(raus).split()).strip()


VERBOTEN = (r"\d+[.,]?\d*\s*(€|euro|eur\b|cent|ct\b)", r"€", r"\beuro\b", r"\bcent\b", r"gratis", r"kostenlos", r"geschenkt",
            r"nur heute", r"vergriffen", r"auf lager", r"ausverkauf", r"garantier", r"rabatt", r"\bsale\b", r"\bdeal\b",
            r"angebot", r"spar", r"günstig", r"billig", r"\bunter\s+\d", r"\bab\s+\d", r"prozent", r"%", r"\bmore\b",
            r"reduziert", r"preis", r"wie nie", r"verkauft", r"black friday", r"\bfür\s+\d", r"\bnur\s+\d", r"bestseller",
            r"\bbeste[nrs]?\b", r"wirkt", r"heilt", r"abnehm",
            r"krass", r"wahnsinn", r"unglaublich", r"nie wieder", r"sofort", r"\b100\b", r"schluss mit", r"must.?have",
            r"geheim", r"trick", r"hack", r"viral", r"jeder braucht", r"musst du", r"lohnt", r"teurer", r"fehler",
            r"schnell", r"letzte chance", r"limitiert", r"exklusiv", r"wow", r"!")


def sauber(t):
    """Artur 14.11.2026 (Verstoß): KEINE Preise, KEINE Versprechen in Beschreibung und Produktname."""
    t = re.sub(r"\b(für|um|ab|unter|nur|statt)\s+(unter\s+)?\d+[.,]?\d*\s*(€|euro|eur|cent|ct)\b\.?", " ", t, flags=re.I)
    t = re.sub(r"\d+[.,]?\d*\s*(€|euro|eur|cent|ct)\b", " ", t, flags=re.I)
    t = re.sub(r"(?i)\b(gratis|kostenlos|nur heute|bald vergriffen|wenige auf lager|günstig|billig)\b", " ", t)
    return " ".join(t.replace("€", " ").split()).strip(" -–,.!?")


def pruefe_verboten(text, was, marke=""):
    s = text.lower()
    if marke and "more" in marke.lower():
        s = s.replace("#more", "").replace(marke.lower(), "")
    for v in VERBOTEN:
        if v == r"\bmore\b" and "more" in (marke or "").lower():
            continue                                             # More-Video darf „More“ heißen
        if re.search(v, s):
            raise Stopp(f"{was} enthält Verbotenes („{v}“): {text!r} – nicht gepostet (Artur 14.11.: kein Preis, keine Versprechen)")


def produktname(d, kurz=True):
    """Neutraler Produktname (≤ 20 Zeichen) aus dem Dateinamen, z. B. „Nike Air Max Plus“ – nie „Bald vergriffen“."""
    n = re.sub(r"^Video \d+ - \d+\s*", "", pathlib.Path(d["datei"]).stem)
    n = sauber(re.sub(r"\s*-\s*V\d+$", "", n))
    if kurz and len(n) > 20:
        n = n[:20].rsplit(" ", 1)[0]
    return n


MARKEN_BEKANNT = ["nike", "airmax", "adidas", "redbull", "apple", "iphone", "samsung", "galaxy", "galaxybuds", "nivea", "garnier",
                  "esn", "more", "morenutrition", "ninja", "makita", "wmf", "htc", "fanttik", "gillette", "halara", "haribo",
                  "milka", "lego", "dyson", "shark", "kärcher", "tonies", "mac", "loreal", "maybelline", "starwars"]


def beschreibung_text(d):
    """Kurz (Artur): optional 1–2 Wörter + 1 Produkt-Hashtag + die 3 Pflicht-Hashtags (bis 30.11.2026), Reihenfolge wechselt."""
    if d.get("beschreibung"):
        return d["beschreibung"].strip() + " "
    pfl = PFLICHT[:] if datetime.date.today() <= datetime.date(2026, 11, 30) else []
    random.shuffle(pfl)
    eigen = [h for h in d.get("hashtags", []) if h.lower() not in PFLICHT and h.lower() not in ("#tiktokshop", "#fyp", "#foryou")]
    # Artur 15.11.2026: KEINE Marken-Hashtags (Nike, Red Bull … geschützt) → Marke, Shop-Name, erstes Wort der Produktnamen raus
    marken = {_kn(w) for w in [d.get("brand", ""), (d.get("produkt") or " ").split()[0], produktname(d, kurz=False).split()[0]] if w}
    marken |= {_kn(w) for w in re.findall(r"[A-Za-zÄÖÜäöü]{3,}", d.get("brand", ""))}
    eigen = [h for h in eigen if not any(m and (_kn(h[1:]).startswith(m) or m.startswith(_kn(h[1:]))) for m in marken)
             and _kn(h[1:]) not in {_kn(x) for x in MARKEN_BEKANNT}]
    tag = eigen[0].lower() if eigen else ""
    teile = pfl[:]
    if tag:
        teile.insert(random.choice([0, len(teile)]), tag)
    wort = ""                                                    # Artur 15.11.2026: KEIN Produktname, nur Hashtags
    t = " ".join(([wort] if wort else []) + teile)
    if not pfl:
        t = " ".join(([wort] if wort else []) + [h.lower() for h in eigen[:3]])
    return t + " "


def beschreiben(text):
    b = warte("Beschreibung", 4, ueber=330)
    if b:
        tipp(b[0], b[1], b[2], "Beschreibung")
    else:                                                        # 15.11.: Feld hat schon Text (Beitrag fortsetzen)
        tx = lesen()
        alt = muss([t for t in tx if t[1] < 230 and 60 < t[2] < 225], "Beschreibungsfeld nicht gefunden")
        tipp(alt[0][1], alt[0][2], tx, "Beschreibung (vorhandener Text)")
    ruhe(0.7)
    # Artur 13.11.2026: Text einfügen statt tippen (spart ~15 s); kommt die Zwischenablage nicht an → tippen
    # Artur 14.11.2026 (Verstoß): Einfügen holte eine alte More-Beschreibung aus der iPhone-Zwischenablage → IMMER tippen,
    # vorher Feld leeren
    for versuch in range(2):
        K().taste("cmd+a"); ruhe(0.2); K().loeschen(1); K().loeschen(len(text) + 40)
        menschlich(text)
        ruhe(0.6)
        if beschreibung_stimmt(text):
            break
        log("Beschreibung am Bildschirm stimmt nicht – Feld leeren, neu tippen")
    else:
        raise Stopp("Beschreibung am Bildschirm stimmt nicht mit der geplanten überein – NICHT gepostet")
    tastatur_zu()
    log(f"Beschreibung getippt: {text.strip()}")


def beschreibung_stimmt(text):
    """Artur 15.11.2026: falsche Beschreibung/Hashtags = Verstoß. Getippten Text am Bildschirm lesen:
    alle geplanten Wörter + Hashtags da, kein fremder Hashtag, keine Zahl/€ die nicht geplant ist."""
    tx = lesen()
    feld = " ".join(t[0] for t in tx if t[1] < 230 and 60 < t[2] < 225).lower()
    soll = [w.lower() for w in text.split()]
    fehlt = [w for w in soll if _kn(w) and _kn(w) not in _kn(feld)]
    tags = re.findall(r"#[\wäöüß]+", feld)
    fremd = [h for h in tags if not any(_kn(h) == _kn(w) or _kn(w).startswith(_kn(h)) for w in soll if w.startswith("#"))]
    preis = re.search(r"\d+[.,]\d+|€|euro", feld) and not re.search(r"\d+[.,]\d+|€|euro", text.lower())
    sollk = _kn(" ".join(soll))
    extra = [w for w in re.findall(r"[a-zäöüß]{4,}", feld) if _kn(w) not in sollk]   # fremder Text (alte Beschreibung)
    if fehlt or fremd or preis or len(extra) > 1:
        fremd = fremd + extra
        log(f"Feld: {feld[:120]!r} | fehlt {fehlt[:3]} | fremd {fremd[:3]} | preis {bool(preis)}")
        return False
    return True


def tastatur_zu():
    tx = lesen()
    for lab in ("Fertig", "OK"):
        f = seh.finde(lab, tx, genau=True, ueber=200)
        if f:
            tipp(f[0], f[1], tx, lab); ruhe(0.8); return


def verlinken(weg, produkt, kurz=""):
    """Artur 13.11.2026: hakt etwas, am aktuellen Bildschirm weitermachen (nicht neu anfangen).
    Jede Runde: Bildschirm lesen → passenden nächsten Schritt machen. Max. ~60 s."""
    # Artur 14.11.2026: Handschuhe – ein allgemeines Wort reicht nicht (falsches Produkt aus dem Showcase).
    # Treffer = mind. 2 Wörter aus dem echten Shop-Namen (Social1/TikTok-Link), bei nur einem Wort dieses eine.
    worte = list(dict.fromkeys(re.findall(r"[a-zäöüß0-9]{4,}", produkt.lower())))
    noetig = min(1, len(worte))
    def passt(block):                                            # 15.11.: Umlaute egal (OCR liest „Vitalitat“)
        return not worte or sum(_kn(w) in _kn(block) for w in worte) >= noetig
    gesucht = False; gesucht_um = 0.0
    def oben(tx):
        hin = sorted([t for t in tx if t[0].strip().startswith("Hinzuf") and 180 < t[2] < 700], key=lambda t: t[2])
        if not hin:
            return None, ""
        hy = hin[0][2]
        return hin, " ".join(t[0] for t in tx if hy - 110 <= t[2] <= hy + 10).lower()
    ende = time.time() + 60
    while time.time() < ende:
        tx = lesen()
        if seh.finde("verstanden", tx):
            v = seh.finde("verstanden", tx); tipp(v[0], v[1], tx, "Verstanden"); ruhe(0.8)
            if seh.finde("nicht verfügbar", tx) or seh.finde("nicht verfugbar", tx) or seh.finde("nicht vorrätig", tx) \
               or seh.finde("nicht hinzugefügt", tx):
                raise Stopp("Produkt beim Verlinken nicht vorrätig/verfügbar → Entwurf")
            continue
        if seh.finde("zum Video", tx) or seh.finde("umbenennen", tx) or seh.finde("zustimmen", tx):
            nach_hinzufuegen(weg); return
        wagen_liste = bool(seh.finde("Einkaufswagen", tx, ueber=80) and seh.finde("Produkte suchen", tx))
        showcase_liste = bool(seh.finde("Dein Showcase", tx) or seh.finde("Aus dem Showcase", tx))
        if (weg == "wagen" and wagen_liste) or (weg != "wagen" and showcase_liste):
            hin, block = oben(tx)
            if not hin:
                neu_laden_tippen(tx); time.sleep(0.4); continue
            # Artur 14.11.2026: NIE in TikTok nach Produkten suchen – immer über Social1. Das gerade über den
            # Social1-Link hinzugefügte Produkt steht oben; passt es nicht, warten (lädt) und dann STOPP statt suchen.
            ziel = hin[0]
            # Artur 15.11.2026: NIE in der Liste scrollen, NIE suchen. Das gerade über Social1 hinzugefügte Produkt
            # steht oben → oberstes nehmen, wenn mind. 1 Wort des Shop-Namens passt (Umlaute egal); sonst warten/STOPP.
            if not passt(block):
                if time.time() > ende - 30:
                    raise Stopp(f"oberstes Produkt passt nicht zu „{produkt}“ ({block[:60]!r}) – nicht verlinkt")
                time.sleep(0.6); continue
            tipp(ziel[1], ziel[2], tx, "Hinzufügen"); ruhe(1.4)
            nach_hinzufuegen(weg); return
        if weg == "wagen" and showcase_liste:
            w = seh.finde("Weitere Produkte", tx)
            if w:
                tipp(w[0], w[1], tx, "Weitere Produkte hinzufügen"); ruhe(1.2); continue
        if weg == "wagen":
            e = seh.finde("Einkaufswagen", tx, unter=500)
            if e and not wagen_liste:
                tipp(e[0], e[1], tx, "Einkaufswagen (Liste)"); ruhe(1.4); continue
        pr = seh.finde("Produkt", tx, genau=True, unter=380)
        if pr and not showcase_liste and not wagen_liste:
            tipp(pr[0], pr[1], tx, "Produkt", abstand=30); ruhe(1.4); continue
        l = seh.finde("Link hinzufügen", tx)
        if l and not showcase_liste and not wagen_liste:
            tipp(l[0], l[1], tx, "Link hinzufügen"); ruhe(1.0); continue
        if neu_laden_tippen(tx):
            continue
        time.sleep(0.4)
    raise Stopp("Verlinken kam nicht weiter (60 s)")


_BUTTON = ""
_umbenannt = False


def nach_hinzufuegen(weg):
    for _ in range(30):
        tx = lesen()
        if seh.finde("zum Video", tx):                           # Dialog „Produkt zum Video hinzufügen?“
            d = seh.finde("zum Video", tx)
            h = muss(seh.finde("Hinzufügen", tx, genau=True, unter=d[1]), "Dialog ohne Hinzufügen")
            tipp(h[0], h[1], tx, "Hinzufügen (Dialog)"); ruhe(1.4); continue
        if seh.finde("umbenennen", tx):
            r = re.search(r"noch (\d+) von (\d+)", " ".join(t for t, _, _ in tx))
            if r:
                log(f"Pilot: noch {r.group(1)} von {r.group(2)}")
            if not kraeftig_rot(80, 678):                        # erst blass (lädt), dann kräftig rot
                time.sleep(0.4); continue
            global _umbenannt
            if _BUTTON and not _umbenannt:                       # Artur 13.11.: Produktname IMMER umbenennen (≤ 20 Zeichen)
                tipp(300, 300, tx, "Produktname-Feld"); ruhe(0.6)
                K().taste("cmd+a"); ruhe(0.2); K().loeschen(1); K().loeschen(120)   # Artur 13.11.: Makita – alter Name blieb stehen
                menschlich(_BUTTON); ruhe(0.5)
                feld = [t[0] for t in lesen() if 240 < t[2] < 360 and len(t[0].strip()) > 3]
                if not any(_kn(f) == _kn(_BUTTON) for f in feld):
                    log(f"Produktname nicht sauber ({feld[:2]}) – nochmal leeren")
                    K().taste("cmd+a"); ruhe(0.2); K().loeschen(140); menschlich(_BUTTON); ruhe(0.5)
                _umbenannt = True; log(f"umbenannt: {_BUTTON}")
            tipp(167, 678, None, "Hinzufügen (rot)"); ruhe(1.6); continue
        if seh.finde("zustimmen", tx):
            z = seh.finde("zustimmen", tx); tipp(z[0], z[1], tx, "Posten zustimmen"); ruhe(1.2); continue
        if seh.finde("Veröffentlichen", tx, unter=600) or seh.finde("Entwürfe", tx, unter=600):
            log(f"Produkt verlinkt ({weg})"); return
        time.sleep(0.4)
    raise Stopp("nach dem Verlinken nicht zurück auf der Beitragsseite")


def brand(name, handle):
    """@Brand nur, wenn das Shop-Konto genau so existiert (handle). Sonst ohne – nicht nachfragen."""
    if not handle:
        return False
    cache = AUS / "brand-konten.json"                            # Brands ohne TikTok-Konto merken → nicht jedes Mal suchen
    bk = json.loads(cache.read_text()) if cache.exists() else {}
    if bk.get(handle.lower()) is False:
        log(f"@{handle}: kein Konto (gemerkt) – ohne Brand"); return False
    e = warte("Erwähnung", 3)
    if not e:
        log("kein „@ Erwähnung“ – ohne Brand"); return False
    tipp(e[0], e[1], e[2], "@ Erwähnung"); ruhe(1.1)
    sf = warte("suchen", 3)                                      # 13.11.: erst ins Suchfeld tippen, sonst geht der Text ins Leere
    if sf:
        tipp(sf[0], sf[1], sf[2], "Nutzer suchen"); ruhe(0.6)
    menschlich(handle)
    f = warte(handle, 5, genau=True, unter=160)
    if not f:
        f = warte("@" + handle, 1, genau=True, unter=160)
    if not f and name:                                           # Artur 13.11.: sonst den stimmigsten Treffer (Name = Shop/Marke)
        tx = lesen()
        n = re.sub(r"[^a-z0-9]", "", name.lower())
        tr = [t for t in tx if 160 < t[2] < 700 and n and re.sub(r"[^a-z0-9]", "", t[0].lower()) == n]
        f = (tr[0][1], tr[0][2] + 9, tx) if tr else None
    if not f:
        log(f"@{handle} nicht gefunden – ohne Brand")
        bk[handle.lower()] = False; cache.write_text(json.dumps(bk, ensure_ascii=False, indent=1))
        zurueck_beitrag()
        return False
    tipp(f[0], f[1] - 9, f[2], "Brand"); ruhe(1.1)
    if not warte("Veröffentlichen", 3, unter=600):
        zurueck_beitrag()
    bk[handle.lower()] = True; cache.write_text(json.dumps(bk, ensure_ascii=False, indent=1))
    log(f"@{handle} markiert")
    return True


def zurueck_beitrag():
    for _ in range(3):
        tx = lesen()
        if seh.finde("Veröffentlichen", tx, unter=600):
            return
        ab = seh.finde("Abbrechen", tx, genau=True)
        tipp(ab[0], ab[1], tx, "Abbrechen") if ab else tipp(22, 57, tx, "Zurück")
        ruhe(1.0)
    muss(seh.finde("Veröffentlichen", lesen(), unter=600), "nicht zurück auf der Beitragsseite")


def abschluss(entwurf):
    tx = lesen()
    if entwurf:
        e = muss(seh.finde("Entwürfe", tx, unter=600), "Knopf „Entwürfe“ fehlt")
        muss(e[0] < 167, "„Entwürfe“ nicht links – Abbruch (Veröffentlichen-Gefahr)")
        tipp(e[0], e[1], tx, "Entwürfe"); ruhe(2.0)
        muss(not seh.finde("Veröffentlichen", lesen(), unter=600), "Entwurf nicht gespeichert – Beitragsseite noch offen")
        log("ALS ENTWURF GESPEICHERT"); return
    ruhe(1.0, 1.8)                                               # Knopf wird erst nach dem Laden kräftig rot
    for _ in range(8):
        tx = lesen()
        z = seh.finde("zustimmen", tx)
        if z:
            tipp(z[0], z[1], tx, "Posten zustimmen"); ruhe(1.2); continue
        kn = [t for t in tx if t[0].strip().endswith("Veröffentlichen") and t[1] > 167 and t[2] > 600]
        v = (kn[0][1], kn[0][2]) if kn else None
        if not v and not seh.finde("Entwürfe", tx, unter=600):
            log("VERÖFFENTLICHT"); return
        muss(v, "„Veröffentlichen“-Knopf rechts unten nicht gefunden")
        if not kraeftig_rot(v[0] + 40, v[1]) and _ < 3:          # 13.11.: nach 3 Versuchen trotzdem tippen
            time.sleep(0.8); continue
        tipp(v[0], v[1], tx, "Veröffentlichen"); ruhe(2.5)
    raise Stopp("Beitragsseite noch offen – nicht veröffentlicht?")


# ---------------------------------------------------------------- 6) Aufräumen

def social1_abhaken(pid, liste_id=None):
    """Mac-Safari (Artur eingeloggt): auf der Social1-Liste die Karte des Produkts → Lesezeichen → Liste abhaken → Done.
    Nie „Delete“ (löscht die ganze Liste). Ohne offene Liste im Mac-Safari: Hinweis, kein Stopp."""
    js = r"""(()=>{const u=location.href; const m=u.match(/saved-videos\/([0-9a-f]+)/); if(!m) return 'keine-liste';
const lid=m[1]; const k=[...document.querySelectorAll('[data-slot=card]')].find(k=>{const p=k.querySelector('img[src*="/products/"]');return p&&p.src.includes('PID')});
if(!k) return 'nicht-in-liste'; k.querySelector('button[title="Save to list"]').click(); return 'auf:'+lid})()""".replace("PID", pid)
    r = _safari(js)
    if not r.startswith("auf:"):
        return r
    time.sleep(1.2)
    lid = r[4:]
    js2 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'kein-dialog';
const c=d.querySelector('button[role=checkbox][id="LID"]'); if(!c) return 'keine-checkbox';
if(c.getAttribute('aria-checked')=='true') c.click(); return 'ok'})()""".replace("LID", lid)
    r2 = _safari(js2)
    time.sleep(0.8)
    js3 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'zu';
const c=d.querySelector('button[role=checkbox][id="LID"]'); const ok=c&&c.getAttribute('aria-checked')=='false';
const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==(ok?'Done':'Close')); if(b) b.click(); return ok?'abgehakt':'nicht-abgehakt'})()""".replace("LID", lid)
    return _safari(js3) if r2 == "ok" else r2


def _safari(js):
    esc = js.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    r = subprocess.run(["osascript", "-e", 'tell application "Safari"\nrepeat with d in documents\n'
                        'if URL of d contains "social1.ai/saved-videos/" then return do JavaScript "' + esc + '" in d\n'
                        'end repeat\nreturn "keine-liste"\nend tell'], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip()[:120])


def _mediathek(tx):
    return bool(seh.finde("Mediathek", tx, unter=650) and seh.finde("Sammlungen", tx, unter=650))


def fotos_loeschen(kachel, oeffnen=True):
    """Fotos → Mediathek → Kachel mit dem Hook-Titel (im Raster lesbar) → Vollbild prüfen → Mülleimer → „Video löschen“
    (bleibt 30 Tage in „Zuletzt gelöscht“). Getestet 12.11.2026: Mülleimer 289/684, 1. Tipp kommt oft nicht an."""
    if oeffnen:
        app("Fotos")
    for _ in range(4):                                           # Fotos öffnet auf der letzten Seite → zurück zur Mediathek
        tx = lesen()
        if _mediathek(tx):
            break
        z = seh.finde("<", tx, ueber=80)
        tipp(z[0], z[1], tx, "Zurück") if z else tipp(30, 57, tx, "Zurück")
        ruhe(1.0)
    muss(_mediathek(lesen()), "Fotos: Mediathek nicht erreicht")
    treffer = None
    for _ in range(4):                                           # neueste unten; sonst etwas hochwischen
        tx = lesen()
        tr = [t for t in tx if 100 < t[2] < 660 and _passt(kachel, t[0])]
        if tr:
            treffer = max(tr, key=lambda t: t[2]); break
        K().ziehe(167, 250, 167, 560, 0.35); ruhe(1.0)
    _, x, y = muss(treffer, f"„{kachel}“ nicht in der Mediathek")
    tipp(x, y + 20, tx, "Video in Fotos"); ruhe(1.3)
    tx = lesen()
    muss(not _mediathek(tx) and [t for t in tx if _passt(kachel, t[0])], "Vollbild zeigt nicht das Video – nicht gelöscht")
    for _ in range(4):
        tipp(289, 684, tx, "Mülleimer"); ruhe(1.0)
        l = warte("Video löschen", 1.5)
        if l:
            muss([t for t in l[2] if _passt(kachel, t[0])], "beim Löschen anderes Video offen – abgebrochen")
            tipp(l[0], l[1], l[2], "Video löschen"); ruhe(1.0)
            muss(not seh.finde("Video löschen", lesen()), "„Video löschen“ hat nicht gewirkt")
            log("Video in Fotos gelöscht"); return
        tx = lesen()
    raise Stopp("Mülleimer in Fotos reagiert nicht")


def aufraeumen(d, fotos=True):
    """Social1 (Mac, ~3 s) gleich nach dem Post; Fotos gesammelt am Stapel-Ende (fotos_aufraeumen), außer fotos=True."""
    pid = d.get("tts_link", "").rstrip("/").split("/")[-1]
    log(f"Social1: {social1_abhaken(pid)}")
    if fotos:
        fotos_aufraeumen([d["kachel"]])


def fotos_aufraeumen(kacheln):
    for i, k in enumerate(kacheln):
        try:
            fotos_loeschen(k, oeffnen=(i == 0))
        except Stopp as e:
            log(f"Hinweis Fotos ({k}): {e}")


# ---------------------------------------------------------------- Ablauf

def heute_gepostet(account):
    p = AUS / f"posts-{datetime.date.today().isoformat()}.json"
    if not p.exists():
        return 0
    z = json.loads(p.read_text()).get("zaehler", {}).get(account, 0)
    return z if isinstance(z, int) else 0


def eintragen(d, dauer, weg, entwurf):
    tag = datetime.date.today().isoformat()
    p = AUS / f"posts-{tag}.json"
    j = json.loads(p.read_text()) if p.exists() else {"datum": tag, "posts": [], "zaehler": {}}
    j["posts"].append({"zeit": time.strftime("%H:%M"), "account": d["account"], "datei": d["datei"], "produkt": d["produkt"],
                       "tts_link": d.get("tts_link"), "weg": weg, "entwurf": entwurf, "dauer_s": round(dauer),
                       "werkzeug": "post_mensch"})
    if not entwurf:
        j["zaehler"][d["account"]] = heute_gepostet(d["account"]) + 1
    p.write_text(json.dumps(j, ensure_ascii=False, indent=1))


def schreibe(p, d, status, info):
    d["status"] = status
    d.setdefault("verlauf", []).append({"zeit": datetime.datetime.now().isoformat(timespec="seconds"), "status": status, "info": info})
    if status == "gepostet":
        d["gepostet_um"] = d["verlauf"][-1]["zeit"]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


_konto = None


def ein_video(p, d, entwurf=False, aufr=True):
    global _konto
    global _BUTTON, _umbenannt, _LETZTE_KACHEL
    # Artur 15.11.2026: Produktname wieder wie üblich („Wenige verfügbar“, „Fast ausverkauft“ …, Liste ACCOUNTS.md),
    # aber NIE ein Preis darin
    _BUTTON, _umbenannt = ((d.get("button") or "")[:20] or produktname(d)), False
    if re.search(r"\d|€|euro|cent|gratis|kostenlos", _BUTTON.lower()):
        raise Stopp(f"Produktname „{_BUTTON}“ enthält Preis/Zahl – nicht gepostet")
    start = time.time()
    datei = EIN / d["datei"]
    if not entwurf:
        r = subprocess.run(["zsh", str(HIER / "gepostet.sh"), "pruefen", str(datei)], capture_output=True, text=True)
        if r.returncode:
            raise Stopp(f"Doppel-Schutz: {r.stdout.strip()}")
        lim = PILOT.get(d["account"])
        if lim and heute_gepostet(d["account"]) >= lim:
            raise Stopp(f"{d['account']}: Tageslimit {lim} erreicht")
    pid = muss(d.get("tts_link", "").rstrip("/").split("/")[-1], "keine Produkt-ID (tts_link)")
    if _konto != d["account"]:
        konto(d["account"]); _konto = d["account"]
    aus = bool(d.get("ausverkauft"))                             # ausverkauft → Entwurf mit Text, ohne Link (Artur 08.11.)
    if aus:
        weg = "ohne Link"; tiktok_hauptseite()
    else:
        globals()["_NEUKUNDE"] = False
        tx = zum_produkt(pid, d["produkt"]);   log("Produktseite")
        if not seh.finde("pro Verkau", tx):                      # Artur 15.11.: nichts angezeigt → runterwischen (neu laden),
            K().ziehe(167, 200, 167, 560, 0.4); ruhe(2.5); tx = lesen()   # sonst Produktlink neu öffnen
            if not seh.finde("pro Verkau", tx):
                log("„pro Verkauf“ fehlt → Produktlink neu öffnen")
                tx = zum_produkt(pid, d["produkt"]); log("Produktseite (neu)")
        weg = "wagen" if d.get("weg") == "wagen" else showcase_oder_wagen(tx)
        if weg == "ausverkauft":
            aus = True; weg = "ohne Link"
    global _NEUKUNDE
    if weg == "wagen" and _NEUKUNDE:                             # Artur 15.11.: nur wenn der Einkaufswagen nicht geht
        _NEUKUNDE = False
        erstellen_route(); weg = "erstellen"
        video_waehlen(d["kachel"], galerie=(264, 583)); log("Beitragsseite")
    else:
        zum_plus();                            log("„+“")
        video_waehlen(d["kachel"]);            log("Beitragsseite")
    cover_pruefen(d["kachel"])
    _bt = beschreibung_text(d); pruefe_verboten(_bt, "Beschreibung", d.get("brand", ""))
    beschreiben(_bt)
    if weg == "erstellen":
        muss(seh.finde(_BUTTON, lesen()), f"Produkt „{_BUTTON}“ nicht am Beitrag – nicht gepostet")
    elif not aus:
        try:
            verlinken(weg, d["produkt"], produktname(d, kurz=False))
        except Stopp as e:
            if "→ Entwurf" not in str(e):
                raise
            for _ in range(5):                                   # zurück auf die Beitragsseite, dann als Entwurf
                tx = lesen()
                if seh.finde("Entwürfe", tx, unter=600):
                    break
                K().ziehe(3, 400, 220, 400, 0.3); ruhe(1.0)   # 15.11.: nie oben links tippen (LIVE)
            log("Produkt nicht verfügbar → Entwurf ohne Link"); aus = True
    # Artur 13.11.2026: Brand-Markierung abgeschaltet (dauert zu lange)
    abschluss(entwurf or aus)
    entwurf = entwurf or aus
    dauer = time.time() - start
    if not entwurf:
        subprocess.run(["zsh", str(HIER / "gepostet.sh"), "eintragen", str(datei), d["account"]], capture_output=True)
        schreibe(p, d, "gepostet", f"post_mensch ({weg}), {dauer:.0f} s")
        _LETZTE_KACHEL = d.get("kachel", "")
    elif aus:
        schreibe(p, d, "entwurf", "ausverkauft – als Entwurf ohne Link gespeichert")
    eintragen(d, dauer, weg, entwurf)
    print(f"✓ {d['datei']} → {d['account']} ({weg}{', Entwurf' if entwurf else ''}) {dauer:.0f} s", flush=True)
    if aufr and not entwurf:
        aufraeumen(d, fotos=False)
    return dauer


def lade(pfad):
    p = pathlib.Path(pfad)
    if not p.exists():
        p = EIN / pfad
    return p, json.loads(p.read_text(encoding="utf-8"))


def main(a):
    if not a:
        sys.exit(__doc__)
    entwurf = "--entwurf" in a
    aufr = "--ohne-aufraeumen" not in a
    if "--ohne-airdrop" in a:
        os.environ["TS_OHNE_AIRDROP"] = "1"
    rest = [x for x in a if not x.startswith("--")]
    import eingang as EG
    try:
        if a[0] == "--aufraeumen":
            p, d = lade(rest[0]); aufraeumen(d); return
        if a[0] == "--fotos":                                    # alle heute geposteten Videos des Stapels aus Fotos
            fotos_aufraeumen([d["kachel"] for _, d in EG.alle() if d["stapel"] == rest[0] and d["status"] in ("gepostet", "entwurf")]); return
        if a[0] == "--stapel":
            liste = [(p, d) for p, d in EG.alle() if d["status"] == "freigegeben" and d["stapel"] == rest[0]]
            if not liste:
                sys.exit("nichts freigegeben")
            liste.sort(key=lambda x: (REIHENFOLGE.index(x[1]["account"]) if x[1]["account"] in REIHENFOLGE else 99, x[1]["datei"]))
        else:
            liste = [lade(rest[0])]
        try:
            if not os.environ.get("TS_EINZELN"):
                EG.aufs_iphone([EIN / d["datei"] for _, d in liste])
        except Exception as e:                                   # posten.Stopp / airdrop.Stopp
            if type(e).__name__ != "Stopp":
                raise
            raise Stopp(f"AirDrop: {e} (Videos schon am iPhone? → --ohne-airdrop)")
        zeiten, aus, fertig, nochmal = [], [], [], []
        for eintrag in liste + [(None, None)]:                   # 15.11.: [None] ließ sich nicht entpacken → Absturz am Ende
            p, d = eintrag
            if p is None:                                        # Ende: übersprungene einmal nachholen
                if True:                                         # Artur 13.11.: nicht am Ende nachholen – Schritte warten selbst
                    break
                os.environ["_NACHHOLEN"] = "1"; log(f"── nachholen: {len(nochmal)} Video(s)")
                liste2 = nochmal; nochmal = []
                for p2, d2 in liste2:
                    d2["status"] = "freigegeben"
                    log(f"── nachholen: {d2['datei']} → {d2['account']}")
                    try:
                        if os.environ.get("TS_EINZELN"):
                            EG.aufs_iphone([EIN / d2["datei"]])
                            (PROJ / "uebergabe" / "ausgang" / "letztes-airdrop.txt").write_text(d2["datei"])
                        zeiten.append(ein_video(p2, d2, entwurf, aufr)); fertig.append(d2["kachel"])
                    except Stopp as e2:
                        if not entwurf:
                            schreibe(p2, d2, "fehler", str(e2))
                        print(f"✗ {d2['datei']}: {e2} (auch beim 2. Versuch)", flush=True)
                        try:
                            tiktok_hauptseite()
                        except Exception:
                            pass
                break
            lim = PILOT.get(d["account"])
            if not entwurf and lim and heute_gepostet(d["account"]) >= lim:
                aus.append(d["datei"]); log(f"übersprungen (Limit {d['account']}): {d['datei']}"); continue
            log(f"── {d['datei']} → {d['account']}")
            try:
                if os.environ.get("TS_EINZELN"):                 # Artur 13.11.2026: Video direkt vor dem Post aufs iPhone
                    merk = PROJ / "uebergabe" / "ausgang" / "letztes-airdrop.txt"
                    alle = PROJ / "uebergabe" / "ausgang" / f"airdrop-{d['stapel']}.txt"   # Artur 15.11.: nie doppelt AirDrop
                    schon = alle.read_text().split("\n") if alle.exists() else []
                    if d["datei"] in schon:
                        log("schon am iPhone (früher per AirDrop) – kein zweites AirDrop")
                    elif merk.exists() and merk.read_text().strip() == d["datei"]:
                        log("schon am iPhone (letztes AirDrop) – kein zweites AirDrop")   # Artur 13.11.: nach Neustart nicht doppelt
                    else:
                        EG.aufs_iphone([frisch_datiert(EIN / d["datei"])]); merk.write_text(d["datei"])
                        with open(alle, "a") as fa:
                            fa.write(d["datei"] + "\n")
                    global _SOLL_DAUER
                    _SOLL_DAUER = dauer_text(EIN / d["datei"])
                    os.environ.pop("TS_OHNE_AIRDROP_EINMAL", None)
                try:
                    zeiten.append(ein_video(p, d, entwurf, aufr)); fertig.append(d["kachel"])
                except Stopp as e1:
                    if "nicht vorrätig" not in str(e1):
                        raise
                    log("ausverkauft → als Entwurf ohne Link (Artur 08.11.), weiter")   # 13.11.: nicht mehr stoppen
                    d["ausverkauft"] = True
                    os.environ["TS_OHNE_AIRDROP_EINMAL"] = "1"
                    zeiten.append(ein_video(p, d, entwurf, aufr)); fertig.append(d["kachel"])
            except Stopp as e:
                if not entwurf:
                    schreibe(p, d, "fehler", str(e))
                hart = any(w in str(e) for w in ("Showcase voll", "CAPTCHA", "Captcha", "Tageslimit", "Doppel-Schutz", "Login"))
                if hart or os.environ.get("TS_NIE_WEITER"):
                    if aufr and not entwurf and fertig:
                        print(f"Hinweis: {len(fertig)} gepostete Videos noch in Fotos – aufräumen: post_mensch.py --fotos {d['stapel']}", flush=True)
                    sys.exit(f"STOPP bei {d['datei']}: {e}")
                # Artur 13.11.2026: „wenn 1 Fehler passiert, warum startest du neu? setz doch einfach fort“
                print(f"✗ {d['datei']}: {e} – weiter mit dem nächsten (Steuer-Chat prüft es)", flush=True)
                nochmal.append((p, d))
                try:
                    tiktok_hauptseite()
                except Exception:
                    pass
        if aufr and not entwurf and fertig:
            t = time.time(); fotos_aufraeumen(fertig); log(f"Fotos aufgeräumt: {len(fertig)} Videos, {time.time() - t:.0f} s")
        print(f"FERTIG {len(zeiten)}/{len(liste)}" + (f", Ø {sum(zeiten) / len(zeiten):.0f} s" if zeiten else "")
              + (f", Limit übersprungen: {len(aus)}" if aus else ""), flush=True)
        if not entwurf:
            subprocess.run(["zsh", str(HIER / "sync.sh"), "sichern", "Posts"], capture_output=True)
    except Stopp as e:
        sys.exit(f"STOPP: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
