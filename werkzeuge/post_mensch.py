#!/usr/bin/env python3
"""Posten wie Artur (Bildschirmaufnahmen 12.11.2026, Editing System eigene/POSTEN-ABLAUF.md) – per Kabel, Schritt für Schritt
per Text-Label auf dem Bildschirm (seh.lesen), mit Gefahren-Sperre und menschlichen Pausen.

  python3 werkzeuge/post_mensch.py <eingang.json> [--entwurf] [--ohne-airdrop] [--ohne-aufraeumen]
  python3 werkzeuge/post_mensch.py --stapel <stapel> [--entwurf] [--ohne-airdrop]   # alle „freigegeben“, Account für Account
  python3 werkzeuge/post_mensch.py --aufraeumen <eingang.json>                      # nur Social1-Lesezeichen + Fotos
  python3 werkzeuge/post_mensch.py --fotos <stapel>                                 # Gepostete des Stapels aus Fotos löschen
  python3 werkzeuge/post_mensch.py --wo                                             # Trockenlauf: welcher Bildschirm? (nur lesen)
  python3 werkzeuge/test/test_posten.py                                             # Offline-Tests (vor jedem Stapel)

Seit 15.11.2026 abends: Zustandsmaschine (bildschirm.py erkennt jeden Bildschirm; je Bildschirm genau ein nächster
Schritt). Hänger → am aktuellen Bildschirm weiter (bis 6×), Sperre (falsches Video/Produkt/Text) → Video verwerfen,
nächstes; 3 Fehler hintereinander oder Hart (Login, Showcase voll, Limit, Doppel, Bild eingefroren) → STOPP.

Pro Video:  (Account prüfen/wechseln) → Safari social1.ai/products/<id> → „View on TikTok Shop“ → (Banner „ÖFFNEN“) →
            Showcase über „… pro Verkauf“, sonst Einkaufswagen (verfügbare Variante) → Produktseite zu → „+“ → Galerie →
            Video (Hook-Titel) → Auswählen → Weiter → Weiter → Beschreibung menschlich tippen → Link → Produkt →
            Showcase oben bzw. Weitere Produkte → Einkaufswagen → Hinzufügen → (@Brand, nur wenn Konto da) →
            Veröffentlichen (--entwurf: „Entwürfe“) → Social1-Lesezeichen am Mac abhaken; am Stapel-Ende alle Videos in Fotos löschen.
Gefahren-Sperre: nie in der Nähe von Kasse, Jetzt kaufen, LIVE, Konto hinzufügen, Delete; CAPTCHA → STOPP.
Ausgabe: eine Zeile pro Schritt mit Sekunden, am Ende „✓ <datei> 84 s“ bzw. „STOPP …“ (dann Foto: kabel.py foto).
"""
import datetime, json, os, pathlib, random, re, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh, tap as T
import bildschirm as B

PROJ = HIER.parent
EIN = PROJ / "uebergabe" / "eingang"
AUS = PROJ / "uebergabe" / "ausgang"
PFLICHT = ["#tiktokshopblackfriday", "#superdeals", "#livedeals"]      # bis 30.11.2026 (Artur)
PILOT = {"andreas.testet": 3}                                          # Shopping-Videos pro Tag
REIHENFOLGE = ["anduri.official", "ella_robinson2", "andreas.testet", "artur.official", "andreasfastlane"]
T0 = time.time()


class Stopp(Exception):
    """Weicher Fehler: am aktuellen Bildschirm weitermachen (Wiederaufnahme in ein_video)."""


class Sperre(Stopp):
    """Sicherheits-Stopp für DIESES Video (falsches Video/Produkt/Text, Preis …): nicht wiederholen, Beitrag verwerfen,
    Video als Fehler markieren, mit dem nächsten weiter. Artur 15.11.2026: „lieber nicht posten als falsch posten“."""


class Limit(Sperre):
    """17.11.2026 (Artur, 148-51): TikTok zeigt einen Hinweis zum Tageslimit → dieses Video verwerfen, Account für heute
    fertig (alle weiteren Videos des Accounts überspringen), mit dem nächsten Account weiter."""


LIMIT_RE = re.compile(r"(tages)?limit\b|limit erreicht|maximale? anzahl|heute (keine|nicht mehr)|morgen (erneut|wieder)|"
                      r"daily limit|reached the limit|noch 0 von", re.I)


def limit_hinweis(tx):
    """Reine Funktion: Text eines Limit-/Tageslimit-Hinweises am Bildschirm (sonst None). Produktnamen wie „Limited“
    oder „limitiert“ zählen nicht (Wortgrenze)."""
    for t in tx:
        if LIMIT_RE.search(t[0]) and not re.search(r"limitiert|limited", t[0], re.I):
            return t[0].strip()
    return None


def bildschirmtext(tx, n=40):
    return " | ".join(t[0].strip() for t in tx[:n])


class Hart(Stopp):
    """Stoppt den ganzen Lauf (Showcase voll, Tageslimit, Doppel-Schutz, Login, Bild bleibt eingefroren)."""


class ListeFalsch(Stopp):
    """Oberstes Produkt in Showcase-/Einkaufswagen-Liste passt nicht → nichts verlinken, Beitrag verwerfen,
    Einkaufswagen leeren und Produkt neu in den Einkaufswagen (Artur 15.11.2026 20:44)."""


class WagenLeeren(Stopp):
    """Einkaufswagen geht nicht (Neukunden-Hinweis = liegt schon drin) → ganzen Einkaufswagen leeren, neu hinzufügen."""


class Verbindungswechsel(Stopp):
    """Artur 17.11.2026: Kabel ab / Kabel↔WLAN mitten im Post → Beitrag verwerfen, Video neu."""


class Entwurf(Stopp):
    """Produkt nicht verfügbar/vorrätig → dieses Video als Entwurf ohne Link."""


ZB = {"warten": 0.0, "lesen": 0.0, "tippen": 0.0, "n_lesen": 0, "n_tipp": 0}


def _zeitbuch_an():
    """TS_ZEITBUCH=1 (16.11.2026, Tempo-Messung): je Log-Zeile, wie viel Zeit seit der letzten Zeile auf feste Pausen/Warten
    (time.sleep), Bild lesen (Kabel + Texterkennung) und Tipps/Wische/Tasten entfiel. Ändert kein Verhalten."""
    import kabel as KB
    s0 = time.sleep

    def schlaf(x):
        ZB["warten"] += max(0.0, x); s0(x)
    time.sleep = schlaf
    l0 = seh.lesen

    def les(*a, **k):
        t = time.time()
        try:
            return l0(*a, **k)
        finally:
            ZB["lesen"] += time.time() - t; ZB["n_lesen"] += 1
    seh.lesen = les
    a0 = KB.aktion

    def akt(*a, **k):
        t = time.time()
        try:
            return a0(*a, **k)
        finally:
            ZB["tippen"] += time.time() - t; ZB["n_tipp"] += 1
    KB.aktion = akt


def log(msg):
    zb = ""
    if os.environ.get("TS_ZEITBUCH"):
        zb = (f"   [warten {ZB['warten']:.1f} | lesen {ZB['lesen']:.1f} ({ZB['n_lesen']}×) | "
              f"eingaben {ZB['tippen']:.1f} ({ZB['n_tipp']}×)]")
        ZB.update(warten=0.0, lesen=0.0, tippen=0.0, n_lesen=0, n_tipp=0)
    print(f"{time.strftime('%H:%M:%S')} {time.time() - T0:5.0f}s {msg}{zb}", flush=True)


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
    """TikTok-Feed: oben links liegt das LIVE-Symbol → dort nie tippen (auch „_IVE“/„ÇIVE“ oben links)."""
    return B.feed_oben(tx) or any(_gefahr(t) for t, x, y in tx if x < 70 and y < 110)


def _captcha(tx):
    return B.captcha_wort(tx)                                    # 17.11.: eine Erkennung für beide (Kategorie-Ausnahme)
    alles = " ".join(t.lower() for t, _, _ in tx)
    alles = re.sub(r"verifiziert\w*", "", alles)   # „Von TikTok verifiziert“ (Shop-Abzeichen) ist kein CAPTCHA
    alles = re.sub(r"spiele\s*(&|und)\s*puzzles?|puzzles?\s*(&|und)\s*\w+|bestseller[^,]{0,40}|\w*puzzles\b", "", alles)
    # 17.11.2026 (147-25 UNO): Produktkategorie „Bestseller-Nr. 3 · Spiele & Puzzles“ ist kein CAPTCHA
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


def popup_ok(tx):
    """Artur 15.11.2026: Info-Popups (z. B. „Gesamtlikes“) mit „OK“ einfach wegdrücken – selbstständig."""
    o = seh.finde("OK", tx, genau=True)
    if o and (seh.finde("Gesamtlikes", tx) or seh.finde("Verstanden", tx) or 250 < o[2] < 700):
        tipp(o[0], o[1], tx, "OK (Popup)"); ruhe(1.0); return True
    return False


def _eingefroren(tx):
    k = seh.kabel()
    alt = k.bild_alter() if k and hasattr(k, "bild_alter") else 0
    return alt > 5000 or not _bild_aktuell(tx)


def _lesen_frisch():
    """Artur 15.11.2026: eingefrorenes Kabelbild → Tipps landeten auf LIVE. iPhone-Uhr im Bild gegen Mac-Uhr (Hauptschutz:
    am 15.11. 18:57 lieferte der Server „frische“ Bilder (Alter 92 ms) mit altem Inhalt, Uhr 6:28) + Bild-Alter vom Server; steht es: Server neu starten (einmal), dann nochmal. Bleibt es stehen → harter STOPP, nichts getippt."""
    tx = seh.lesen()
    if not _eingefroren(tx):
        return tx
    time.sleep(2); tx = seh.lesen()
    if not _eingefroren(tx):
        return tx
    log("Bild eingefroren → iPhone-Server neu starten")
    try:
        seh.kabel().neu_verbinden()
    except Exception as e:
        log(f"Neustart-Fehler: {e}")
    tx = seh.lesen()
    if _eingefroren(tx):
        uhr = next((t[0] for t in tx if t[2] < 30 and t[1] < 80 and re.fullmatch(r"\d{1,2}:\d{2}", t[0].strip())), "?")
        raise Hart(f"iPhone-Bild eingefroren (Uhr im Bild {uhr} ≠ {time.strftime('%H:%M')}) auch nach Server-Neustart – "
                   "iPhone gesperrt/Bildschirm aus? Bitte entsperren, dann neu starten. Nichts getippt")
    return tx


_VB = {"aktiv": False, "wechsel": 0, "art": "", "zuletzt": 0.0}


def verbindung_merken(aktiv=True):
    """Stand der Kabel-Verbindung zu Beginn eines Versuchs merken (Zähler + USB/WLAN)."""
    k = seh.kabel()
    _VB.update(aktiv=aktiv and bool(k), wechsel=getattr(k, "WECHSEL", 0) if k else 0, zuletzt=time.time(),
               art=(k.steuerung_art() if k and hasattr(k, "steuerung_art") else ""))


def verbindung_pruefen():
    """Artur 17.11.2026: „Hänger passiert nur, wenn das Kabel entfernt wird oder sich löst“ / „wenn von Kabel auf WLAN
    umgeschaltet wird oder andersrum“ → jeder Verbindungswechsel mitten im Post = Verbindungswechsel (Beitrag neu)."""
    if not _VB["aktiv"]:
        return
    k = seh.kabel()
    if not k:
        return
    if getattr(k, "WECHSEL", 0) != _VB["wechsel"]:
        raise Verbindungswechsel("Kabel-Steuerung neu verbunden")
    if time.time() - _VB["zuletzt"] > 2.0 and hasattr(k, "steuerung_art"):
        _VB["zuletzt"] = time.time()
        art = k.steuerung_art()
        if art and _VB["art"] and art != _VB["art"]:
            raise Verbindungswechsel(f"Verbindung gewechselt: {_VB['art']} → {art}")
        _VB["art"] = art or _VB["art"]


def lesen():
    """CAPTCHA: nie selbst lösen, aber auch nicht abbrechen (Artur 13.11.2026: „soll automatisiert gehen“) –
    melden, warten bis Artur es gelöst hat, dann am aktuellen Bildschirm weitermachen."""
    tx = _lesen_frisch()
    verbindung_pruefen()                                         # 17.11.: Kabel ab / WLAN↔USB → Beitrag neu
    w = _captcha(tx)
    if not w:
        return tx
    print(f"CAPTCHA/Prüfung am Bildschirm („{w}“) – warte, bis Artur sie gelöst hat …", flush=True)
    _melden("CAPTCHA am iPhone – bitte lösen, danach geht es von selbst weiter")
    start = time.time(); letzte = start
    while time.time() - start < 45 * 60:
        time.sleep(8)
        tx = _lesen_frisch()
        if not _captcha(tx):
            print(f"CAPTCHA gelöst nach {time.time() - start:.0f} s – weiter", flush=True)
            ruhe(2)
            return seh.lesen()
        if time.time() - letzte > 5 * 60:
            _melden("CAPTCHA wartet noch – bitte am iPhone lösen"); letzte = time.time()
    raise Hart(f"CAPTCHA/Prüfung („{w}“) seit 45 min ungelöst – Artur, bitte lösen, dann neu starten")


def tipp(x, y, tx=None, was="", abstand=38, zitter=3):
    """Ein Tipp mit Gefahren-Sperre (kein Gefahren-Label im Umkreis) und leicht zufälligem Punkt."""
    tx = lesen() if tx is None else tx
    jetzt = lesen()                                             # 15.11.: vor jedem Tipp frisches Bild (Uhr-Prüfung in lesen)
    alle = [t for t in jetzt if t[0].strip().lower() in ("alle", "alle auswählen", "alle auswahlen")
            and abs(t[1] - x) < 45 and abs(t[2] - y) < 25]
    if alle and "alle" not in (was or "").lower():               # 17.11.2026: in Fotos liegt oben links „Alle“ (alles
        raise Sperre(f"Gefahren-Sperre: „{alle[0][0]}“ bei {x:.0f},{y:.0f} – {was or 'Tipp'} nicht getippt")   # auswählen!)
    if x < 70 and y < 110 and (_feed(tx) or _feed(jetzt)):
        raise Stopp(f"Gefahren-Sperre: oben links im Feed liegt LIVE – {was or 'Tipp'} nicht getippt")
    if B.erkenne(jetzt) in (B.LIVE, B.SYSTEM):
        foto = AUS / f"live-{time.strftime('%H%M%S')}.png"           # 15.11.: Beleg, falls Fehlerkennung
        try:
            seh.kabel().foto(str(foto))
        except Exception:
            pass
        log(f"LIVE/System erkannt (Foto {foto.name}): {[t[0] for t in jetzt][:14]}")
        raise Stopp(f"Gefahren-Sperre: LIVE-/System-Seite offen – {was or 'Tipp'} nicht getippt")
    for t, gx, gy in list(tx) + list(jetzt):
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
    if name == "TikTok":                                         # 16.11.: auch Kamera/Galerie/Vorschau/Editor (nach AirDrop
        return _tabs(tx) or bool(seh.finde("Link hinzufügen", tx) or seh.finde("Kasse", tx, unter=600)) \
            or B.erkenne(tx) in (B.KAMERA, B.GALERIE, B.VORSCHAU, B.EDITOR)   # nicht weiterwischen)
    if name == "Safari":
        return bool(seh.finde("social1", tx) or seh.finde("View on TikTok Shop", tx) or seh.finde("Saved Videos", tx))
    return False


def app(name, erzwingen=False):
    """App nach vorn. Artur 13.11.: schon vorn → bleiben; sonst Wisch an der unteren Kante (vorige App), sonst Suche.
    erzwingen: direkt über Home + Suche (hängender Bildschirm)."""
    if not erzwingen and _ist_app(name):
        return
    tx = seh.lesen()                                             # 15.11.2026: nach AirDrop offene Fotos-Ansicht →
    z = [t for t in tx if t[2] < 42 and t[1] < 110 and name.lower() in t[0].lower()]   # Statusleisten-Link „◂ TikTok“
    if z:
        T.main([str(round(z[0][1], 1)), str(round(z[0][2], 1))]); ruhe(1.4)
        if _ist_app(name):
            log(f"{name} per Zurück-Link oben links"); return
    if name in ("TikTok", "Safari") and not erzwingen:
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


def lage(tx=None):
    """Wo bin ich? → (Bildschirm, texte, tabs). tabs = TikTok-Leiste mit „+“ (Pixel). bildschirm.py, offline getestet."""
    tx = lesen() if tx is None else tx
    z = B.erkenne(tx)
    tabs = False
    if z in (B.UNBEKANNT, B.FEED, B.PROFIL, B.TIKTOK_SONST, B.LADEN):
        tabs = _tabs(tx)                                         # Pixel des zuletzt gelesenen Bilds (= tx)
        if tabs and z in (B.UNBEKANNT, B.LADEN):
            z = B.TIKTOK
    return z, tx, tabs


def wisch_zurueck():
    """Zurück per Wisch vom linken Rand – nie oben links tippen (Artur 15.11.2026: dort liegt auf der Startseite LIVE)."""
    K().ziehe(3, 600, 220, 600, 0.3); ruhe(1.2)                # 15.11.: unten – bei y 400 liegt das Produktbild
                                                             # (Wisch blätterte nur die Bilder durch)


def produktseite_zu(tx):
    """Produktseite (über Social1-Link geöffnet) = ganze Seite mit X oben links (Artur 15.11.2026: Wisch blätterte nur
    das Produktbild, „TikTok neu öffnen“ landete wieder auf der Produktseite). X antippen – kein Feed, also kein LIVE."""
    x = [t for t in tx if t[1] < 60 and 40 < t[2] < 80 and t[0].strip()[:1] in ("×", "X", "x")]
    tipp(x[0][1] - (8 if len(x[0][0].strip()) > 1 else 0) if x else 21, x[0][2] if x else 57, tx, "Produktseite zu (X)",
         abstand=25)
    ruhe(1.4)


def blatt_runter(y0=300):
    K().ziehe(167, y0, 167, 740, 0.35); ruhe(1.2)


def tippe_text(tx, muster, was=None, genau=False, **kw):
    f = seh.finde(muster, tx, genau=genau, **kw)
    if not f:
        return False
    tipp(f[0], f[1], tx, was or muster); ruhe(1.0)
    return True


def anfordern_x(tx, a):
    """Reine Funktion: X unter dem Knopf „Jetzt anfordern“ – gelesenes X/× bis 110 Pkt darunter, sonst 60 Pkt unter dem
    Knopf mittig (transparentes Kreis-X, liest die Texterkennung oft nicht)."""
    xs = [t for t in tx if t[0].strip() in ("X", "x", "×", "⊗", "ⓧ", "⊠") and a[1] + 20 < t[2] < a[1] + 110]
    return (xs[0][1], xs[0][2]) if xs else (167, min(a[1] + 60, 715))


def dialog_wegmachen(z, tx, abbrechen=False):
    """Genau ein Schritt für einen Dialog. True = etwas getan. abbrechen=True: Beitrag wird verworfen (nie zustimmen/posten)."""
    if z == B.LOGIN:
        raise Hart("TikTok-Login/Registrieren am Bildschirm – Artur muss sich anmelden")
    if z == B.DLG_VERSTANDEN:
        return tippe_text(tx, "verstanden", "OK, verstanden")
    if z == B.DLG_ZUM_VIDEO:
        if abbrechen:
            return tippe_text(tx, "Abbrechen", genau=True) or (wisch_zurueck() or True)
        d = seh.finde("zum Video", tx)
        h = seh.finde("Hinzufügen", tx, genau=True, unter=d[1] if d else 0)
        if h:
            tipp(h[0], h[1], tx, "Hinzufügen (Dialog)"); ruhe(1.4); return True
        return False
    if z == B.DLG_VERWERFEN:
        return tippe_text(tx, "Verwerfen", genau=True) or tippe_text(tx, "Neu beginnen", genau=True) \
            or tippe_text(tx, "verwerfen")
    if z == B.DLG_UPLOAD:
        return tippe_text(tx, "Bestätigen", "Bestätigen (Upload läuft)")
    if z == B.DLG_ZUSTIMMEN:
        if abbrechen:
            return tippe_text(tx, "Abbrechen", genau=True) or tippe_text(tx, "Nicht jetzt") or (wisch_zurueck() or True)
        return tippe_text(tx, "zustimmen", "Posten zustimmen")
    if z == B.DLG_OK:
        return tippe_text(tx, "OK", "OK (Popup)", genau=True)
    if z == B.DLG_ERLAUBEN:
        return tippe_text(tx, "Nicht erlauben", genau=True)
    if z == B.DLG_ANFORDERN:                                     # Artur 16.11.2026: „einfach aufs transparente X unter
        a = seh.finde("Jetzt anfordern", tx)                     # ‚Jetzt anfordern‘ klicken“
        x = anfordern_x(tx, a)
        foto = AUS / f"anfordern-{time.strftime('%H%M%S')}.png"   # Beleg: sitzt das X richtig?
        try:
            seh.kabel().foto(str(foto))
        except Exception:
            pass
        log(f"Popup „Jetzt anfordern“ → X bei {x[0]:.0f},{x[1]:.0f} (Foto {foto.name})")
        tipp(x[0], x[1], tx, "Popup zu (X unter „Jetzt anfordern“)", abstand=20); ruhe(1.2); return True
    if z == B.DLG_SCHLIESSEN:                                    # Artur 15.11.: „einfach auf Schließen“
        return tippe_text(tx, "Schließen", "Schließen (Popup)", genau=True)
    if z == B.DLG_OEFFNEN:
        return tippe_text(tx, "Öffnen", genau=True) or tippe_text(tx, "TikTok öffnen")
    if z == B.LADEFEHLER:
        return neu_laden_tippen(tx)
    if z == B.LADEN:
        time.sleep(1.5); return True
    if z == B.OFFLINE:
        log("kein Internet am iPhone – warte"); time.sleep(10); return True
    return False


def bewerben_x_y(tx):
    """Reine Funktion: Höhe des X am Blatt „Wie möchtest du Produkte bewerben?“. Aufnahme Szenario 3 (16.11.2026): Titel
    bei 120 / 200 / 445 Pkt, X jeweils ~34 Pkt darüber (nach dem Entwurf steht das Blatt tief – fester Tipp auf 85 ging
    daneben)."""
    t = seh.finde("Wie möchtest", tx)
    if t:
        return max(40, t[1] - 34)
    t = seh.finde("bewerben?", tx)
    return max(40, t[1] - 52) if t else 85


def tiktok_schliessen():
    """17.11.2026 (Artur: „lerne TikTok auf dem Handy zu schließen“, Steuer-Chat am iPhone geübt): bei Hängern TikTok
    hart beenden statt nur nach vorn holen. Doppel-Home = App-Umschalter (Wisch vom unteren Rand öffnet ihn übers Kabel
    nicht), TikTok-Karte nach rechts holen, Karte nach oben wegwischen, prüfen, Home. Punkte 334 × 735."""
    K().taste("home"); ruhe(1.0)
    K().taste("home"); K().taste("home"); ruhe(1.2)
    tx, k = None, None
    for i in range(4):
        tx = lesen()
        k = seh.finde("TikTok", tx, genau=True)
        if k:
            break
        K().ziehe(90, 400, 300, 400, 0.4); ruhe(0.8)
    if not k:
        log("App-Umschalter: TikTok-Karte nicht gefunden"); K().taste("home"); ruhe(0.8); return False
    x = min(max(k[0], 150), 300)
    K().ziehe(x, 450, x, 40, 0.25); ruhe(1.0)
    weg = not seh.finde("TikTok", lesen(), genau=True)
    K().taste("home"); ruhe(0.8)
    log("TikTok geschlossen (App-Umschalter)" if weg else "TikTok-Karte nicht weggewischt")
    return weg


def zur_hauptseite(abbrechen=True, max_schritte=16):
    """Zustandsmaschine (Artur 15.11.2026): von JEDEM Bildschirm zurück zur TikTok-Hauptseite mit Leiste – je Bildschirm
    genau ein Schritt, dann neu schauen. Halbfertiger Beitrag wird verworfen (abbrechen). Nie oben links im Feed (LIVE),
    nie etwas auf LIVE-/System-Seiten antippen. Gleicher Bildschirm 3× ohne Wirkung → TikTok über Home/Suche öffnen."""
    vorher, gleich, apps = None, 0, 0
    for _ in range(max_schritte):
        z, tx, tabs = lage()
        if tabs and z in (B.FEED, B.PROFIL, B.TIKTOK):
            return tx
        gleich = gleich + 1 if z == vorher else 0
        vorher = z
        if gleich >= 3 and apps < 2 and z != B.PRODUKTSEITE:
            log(f"Bildschirm „{z}“ bleibt – TikTok schließen + neu öffnen"); apps += 1; gleich = 0
            tiktok_schliessen()                                  # 17.11.2026 (Artur): App schließen statt nach vorn
            app("TikTok", erzwingen=True); ruhe(4.0); continue
        if dialog_wegmachen(z, tx, abbrechen=abbrechen):
            continue
        if z == B.LIVE:
            log("LIVE-Seite offen → Wisch zurück (nichts antippen)")
            wisch_zurueck() if gleich % 2 == 0 else blatt_runter(200)
        elif z in (B.SYSTEM, B.SUCHE):
            K().taste("home"); ruhe(1.0); app("TikTok")
        elif z == B.TEILEN:
            blatt_runter(250)
        elif z in (B.HOME, B.SAFARI, B.SAFARI_SOCIAL1, B.FOTOS_MEDIATHEK, B.FOTOS_ALBUM, B.FOTOS_VOLLBILD):
            app("TikTok")
        elif z == B.SHOWCASE_SEITE:                              # 16.11.: „Entdecken | Verwalten“ → Zurück-Pfeil
            tipp(20, (seh.finde("Verwalten", tx) or (0, 57))[1], tx, "Zurück (Showcase-Seite)", abstand=20); ruhe(1.2)
        elif z == B.EDITOR:                                      # 15.11.: Editor-Pfeil „<“ sitzt tiefer (Höhe „Sound“)
            snd = seh.finde("Sound", tx, ueber=120)
            tipp(22, snd[1] if snd else 78, tx, "Zurück (editor)", abstand=20); ruhe(1.4)
        elif z in (B.UMBENENNEN, B.SHOWCASE_LISTE, B.WAGEN_LISTE, B.BEITRAG, B.VORSCHAU):
            tipp(18, 57, tx, f"Zurück ({z})", abstand=20); ruhe(1.4)    # keine Feed-Seite: tipp() prüft das nochmal
        elif z == B.LINK_BLATT:                                  # 15.11.: Blatt sitzt tief (ab ~540) → X rechts am Titel
            titel = [t for t in tx if t[0].strip() == "Link hinzufügen" and t[2] > 450]
            if titel:
                tipp(315, titel[0][2], tx, "Link-Blatt zu (X)", abstand=25); ruhe(1.0)
            else:
                blatt_runter(560)
        elif z in (B.WERBE_BLATT, B.VARIANTEN, B.KONTO_WECHSELN):
            blatt_runter(130 if z == B.WERBE_BLATT else 300)
        elif z == B.BEWERBEN:                                    # nie „LIVE gehen“; X sitzt ~34 Pkt über dem Titel –
            tipp(310, bewerben_x_y(tx), tx, "Blatt zu (X)", abstand=25); ruhe(1.2)   # Blatt steht mal oben, mal tief
        elif z == B.PRODUKT_BILDER:
            blatt_runter(250)
        elif z == B.NICHT_VERFUEGBAR:
            x_oben = any(t[1] < 60 and 40 < t[2] < 80 and t[0].strip()[:1] in ("×", "X", "x") for t in tx)
            produktseite_zu(tx) if x_oben else wisch_zurueck()
        elif z == B.PRODUKTSEITE and _feed(tx):                  # Blatt über dem Shop-Reiter (oben links LIVE!) →
            blatt_runter(250 if gleich % 2 == 0 else 150)        # nie X oben links, nur runterwischen
        elif z == B.PRODUKTSEITE:
            if any(t[1] < 60 and 40 < t[2] < 80 and t[0].strip()[:1] in ("×", "X", "x") for t in tx) or gleich % 2 == 0:
                produktseite_zu(tx)                              # ganze Seite: X oben links
            else:
                blatt_runter(150)                                # Blatt über dem Shop-Reiter: von oben runterwischen
        elif z == B.KAMERA:
            snd = seh.finde("Sound hinzufügen", tx)
            tipp(24, snd[1] if snd else 57, tx, "Kamera zu"); ruhe(1.4)
        elif z == B.GALERIE:
            tipp(28, 74, tx, "Galerie zu"); ruhe(1.2)
        elif z == B.FEED and not tabs:
            blatt_runter(330)                                    # Produktkarte halb offen über dem Feed
        else:                                                    # NICHT_VERFUEGBAR, TIKTOK_SONST, PROFIL ohne Leiste, UNBEKANNT
            wisch_zurueck()
    raise Stopp("TikTok-Hauptseite nicht erreicht")


def beitrag_abbrechen():
    """Halbfertigen Beitrag verwerfen und zur Hauptseite (Artur 15.11.2026: sonst Kette von Fehlern)."""
    try:
        zur_hauptseite(abbrechen=True); return True
    except Stopp:
        return False


def tiktok_hauptseite():
    app("TikTok")
    return zur_hauptseite(abbrechen=True)


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


def pfeil_x(dunkel, start, luecke=14):
    """Pfeil ▾ = letztes dunkles Pixel des Laufs, der direkt am Namen hängt (Lücke > 14 Pkt = Ende). 15.11.2026: rechts
    daneben steht oft eine Sprechblase („Was geht?“) – die darf nicht zählen (Tipp landete dort → Gesamtlikes-Popup)."""
    letzte = None
    for x in sorted(dunkel):
        if x < start:
            continue
        if letzte is not None and x - letzte > luecke:
            break
        letzte = x
    return (letzte - 3) if letzte is not None else start + 60


def konto(account):
    """Profil-Tab → @account prüfen, sonst Name ▾ oben links → Account (nie „Konto hinzufügen“)."""
    tx = tiktok_hauptseite()
    tipp(*PROFIL, tx, "Profil"); ruhe(1.5)
    for _ in range(3):
        f = warte("@" + account, 2.5)
        tx = lesen()
        if popup_ok(tx):
            tx = lesen()
        kopf = [t for t in tx if t[2] < 80 and _kn(account) in _kn(t[0])]   # 15.11.: Name in der Kopfzeile = aktives Konto
        if f or kopf:
            log(f"Account {account} ✓"); return
        if not seh.finde("Follower", tx) and not [t for t in tx if t[0].startswith("@") and t[2] < 220] \
           and (seh.finde("Entwürfe", tx) or seh.finde("Angepinnt", tx)):   # NUR wenn gescrollt → hoch
            K().ziehe(167, 250, 167, 600, 0.3); ruhe(1.0); continue
        if seh.finde("Follower", tx):                            # Profil oben, anderes Konto → gleich wechseln
            break
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
    # Artur 15.11.2026: nie nach Namenslänge rechnen – im Bild das letzte dunkle Zeichen rechts vom Namen = Pfeil ▾
    xs = list(range(int(n[1]), 300, 2))
    dunkel = set()                                               # 15.11.: ▾ ist dünn und sitzt nicht genau auf der
    for dy in (-4, -2, 0, 2, 4):                                 # Text-Mitte → 5 Zeilen absuchen
        dunkel |= {x for x, (r, g, b) in zip(xs, farben(*[(x, n[2] + dy) for x in xs])) if r < 90 and g < 90 and b < 90}
    x0 = pfeil_x(dunkel, n[1])
    for dx in (0, 7, -6, 14):
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


ADRESS_EDIT = ("Abbrechen", "Google-Vorschläge", "Letzte Sucheinträge", "Geöffneter Tab", "Favoriten", "Vorschläge",
               "Häufig besucht")


def adressleiste_aktiv():
    """Artur 15.11.2026 21:36: „warum hast du die ganze Social1-Seite markiert“ – ⌘L kam (Verzögerung) nicht an, das
    folgende ⌘A markierte die Seite. Jetzt ⌘A erst, wenn die Adressleiste sichtbar im Eingabemodus ist; sonst unten auf
    die Adressleiste tippen und nochmal prüfen. Nie blind ⌘A."""
    for versuch in range(4):
        if versuch < 2:
            K().taste("cmd+l")
        else:
            tx = lesen()
            a = [t for t in tx if t[2] > 620 and ("social1" in t[0].lower() or "suchen" in t[0].lower()
                                                    or "website" in t[0].lower())]
            tipp(a[0][1] if a else 167, a[0][2] if a else 684, tx, "Adressleiste", abstand=20)
        for _ in range(6):
            time.sleep(0.5)
            tx = lesen()
            if any(seh.finde(w, tx) for w in ADRESS_EDIT):
                return
    raise Stopp("Safari-Adressleiste lässt sich nicht aktivieren – nichts markiert/getippt")


_LETZTER_TIPP = {}


def kuerzlich(was, sek):
    """Doppel-Tipp-Schutz (16.11.2026, Tempo): wurde dieses Label in den letzten sek Sekunden schon angetippt? Dann nicht
    nochmal – kürzere Pausen dürfen nie dazu führen, dass ein noch sichtbares (ausblendendes) Label zweimal getippt wird."""
    return time.time() - _LETZTER_TIPP.get(was, 0) < sek


def merke(was):
    _LETZTER_TIPP[was] = time.time()


def zlog(msg):
    """Zwischenzeit nur im Zeitbuch-Modus (TS_ZEITBUCH=1)."""
    if os.environ.get("TS_ZEITBUCH"):
        log("  · " + msg)


def zum_produkt(pid, produkt):
    app("Safari"); zlog("Safari vorn")
    adressleiste_aktiv(); zlog("Adressleiste aktiv")
    schnell(f"social1.ai/products/{pid}"); time.sleep(0.3)
    K().taste("return"); zlog("Adresse getippt")
    f = warte("View on TikTok Shop", 15); zlog("Social1 geladen")
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
    zlog("Social1 zeigt das Produkt")
    tipp(f[0], f[1], tx, "View on TikTok Shop"); merke("View on TikTok Shop")
    ruhe(0.8)                                                    # 16.11.: war 2,0 – Schleife unten wartet auf die Seite
    getippt = 0
    for i in range(70):                                          # bis ~35 s: Banner/Dialoge, TikTok lädt das Produkt
        tx = lesen()
        if seh.finde("nicht mehr verfügbar", tx) or seh.finde("Produkt nicht verfügbar", tx) \
           or seh.finde("Artikel nicht verfügbar", tx) or seh.finde("Artikel nicht verfugbar", tx):
            # Artur 14.11.2026: Seite „Produkt nicht verfügbar“ → Entwurf ohne Link (nicht überspringen)
            raise Entwurf("Produkt nicht verfügbar – nicht vorrätig → Entwurf ohne Link")
        if produktseite_da(tx):
            txt = " ".join(t.lower() for t, _, _ in tx)
            if not shop or any(w in txt for w in shop) or any(w in txt for w in worte) or i > 24:
                return tx
        for lab in ("TikTok öffnen", "Öffnen", "ÖFFNEN", "App öffnen"):
            o = seh.finde(lab, tx, genau=True) or (seh.finde(lab, tx) if lab == "TikTok öffnen" else None)
            if o:
                if kuerzlich("öffnen", 3.0):                     # 16.11.: Dialog blendet noch aus → nicht nochmal tippen
                    time.sleep(0.4); break
                tipp(o[0], o[1], tx, lab); merke("öffnen"); getippt += 1
                ruhe(1.0 if lab != "TikTok öffnen" else 0.8); break   # 16.11.: war 2,5/1,5 – Schleife wartet weiter
        else:
            v = seh.finde("View on TikTok Shop", tx)
            if v and i % 10 == 9 and not kuerzlich("View on TikTok Shop", 4.0):   # Tipp kam nicht an
                tipp(v[0], v[1], tx, "View on TikTok Shop"); merke("View on TikTok Shop"); ruhe(1.5)
            time.sleep(0.4)
    raise Stopp("TikTok-Produktseite nicht erreicht")


# ---------------------------------------------------------------- 3) Showcase oder Einkaufswagen

def showcase_oder_wagen(tx):
    # Artur 13.11.2026: „Ausverkauft“ steht unten auf der Produktseite → Showcase ja, Einkaufswagen nein, Video als Entwurf
    ausv = bool(seh.finde("Ausverkauft", tx, unter=560) or seh.finde("Nicht vorrätig", tx, unter=560))
    if ausv:
        log("Produktseite: Ausverkauft")
    v = seh.finde("pro Verkauf", tx)
    if v:
        tipp(v[0], v[1], tx, "pro Verkauf"); ruhe(0.6)          # 16.11.: war 1,6 s – die Schleife wartet aufs Blatt
        for _ in range(14):
            tx = lesen()
            if seh.finde("verstanden", tx) and (seh.finde("nicht verfügbar", tx) or seh.finde("nicht hinzugefügt", tx)):
                vv = seh.finde("verstanden", tx); tipp(vv[0], vv[1], tx, "OK, verstanden"); ruhe(0.8)
                log("Produkt nicht verfügbar (gesperrt) → Entwurf ohne Link"); return "ausverkauft"   # Artur 13.11.
            z = seh.finde("Showcase hinzufügen", tx)
            if z:
                tipp(z[0], z[1], tx, "Zum Showcase hinzufügen"); ruhe(1.6)
                if showcase_voll(lesen()):
                    raise Hart("Showcase voll – Artur löscht selbst, danach neu starten")
                log("ins Showcase gelegt")
                return "ausverkauft" if ausv else "showcase"
            if seh.finde("Mehr erkunden", tx) or seh.finde("im Showcase", tx) or seh.finde("Jetzt erstellen", tx):
                break                                            # Artur 13.11.: „Jetzt erstellen“ = schon im Showcase
            time.sleep(0.3)
        if ausv:
            log("schon im Showcase, ausverkauft → kein Einkaufswagen"); return "ausverkauft"
        # Artur 13.11.2026 16:30: schon im Showcase → IMMER Einkaufswagen und Link aus dem Einkaufswagen (nie im Showcase suchen)
        log("schon im Showcase → Einkaufswagen")
        tx = lesen()
        for _ in range(4):                                       # Blatt schließen: nach unten wischen, bis „Kasse“ +
            if produktseite_da(tx):                              # „Einkaufswagen“ wieder frei stehen (16.11.: sonst
                break                                            # fehlte der Einkaufswagen-Knopf → Social1 von vorn)
            wa = seh.finde("Werbeaktion", tx)
            if wa:
                K().ziehe(167, wa[1] + 10, 167, wa[1] + 420, 0.3)
            else:
                blatt_runter(130)
            ruhe(1.0); tx = lesen()
        in_wagen(tx)
        return "wagen"
    else:
        log("kein „pro Verkauf“ → Einkaufswagen")
    in_wagen(tx)
    return "wagen"


def showcase_voll(tx):
    t = " ".join(x[0].lower() for x in tx)
    return bool(re.search(r"showcase (ist )?voll|maximale anzahl|maximum (an|von) produkt|limit (für|von) produkte", t))


def neukunde_hinweis(tx):
    """Reine Funktion (Artur 16.11.2026, Szenario 3): Hinweis „Das Angebot für Neukund*innen ist auf 1 Option pro Artikel
    beschränkt … über die Schaltfläche „Kaufen“ …“ = Produkt kann NICHT in den Einkaufswagen. NICHT gemeint sind die
    normalen Texte „Funde für Neukund*innen“ (Shop-Reiter), „Neukunden-Angebot“ (Produktseite) und „Angebot für
    Neukund*innen“ in Listen – die lösten vorher fälschlich den „Jetzt erstellen“-Weg aus."""
    t = " ".join(x[0].lower() for x in tx)
    return any(w in t for w in ("option pro artikel", "1 option pro", "auf 1 option", "schaltfläche „kaufen",
                                 "schaltfläche \"kaufen", "das produkt direkt erwerben", "das angebot für neukund"))


def wagen_ergebnis(tx):
    """Reine Funktion: Bildschirm nach einem Einkaufswagen-Tipp → „ok“ (Hinweis „hinzugefügt“), „neukunde“ (kann nicht
    hinein), „auswahl“ (Varianten-Blatt offen) oder None (noch nichts zu sehen)."""
    if neukunde_hinweis(tx):
        return "neukunde"
    if seh.finde("hinzugefügt", tx) or seh.finde("Zur Kasse (", tx):
        return "ok"
    if seh.finde("Bitte auswählen", tx) or B.erkenne(tx) == B.VARIANTEN:
        return "auswahl"
    return None


def _wagen_warten(sek=3.0):
    ende = time.time() + sek
    while True:
        tx = lesen()
        erg = wagen_ergebnis(tx)
        if erg or time.time() > ende:
            return erg, tx
        time.sleep(0.3)


def _neukunde_merken():
    global _NEUKUNDE
    _NEUKUNDE = True
    log("Neukunden-Hinweis: Produkt kann nicht in den Einkaufswagen → „Jetzt erstellen“-Weg"); ruhe(1.5)


def in_wagen(tx):
    w = muss(seh.finde("Einkaufswagen", tx, unter=600), "Einkaufswagen-Knopf fehlt")
    k = seh.finde("Kasse", tx, unter=600)
    muss(w[0] < 167 and (not k or k[0] > w[0] + 80), "Einkaufswagen nicht links neben Kasse – Lage unklar")
    tipp(w[0], w[1], tx, "Einkaufswagen (grau)"); ruhe(0.6)
    # Artur 16.11.2026 (Szenario 2/3): Produkte ohne Varianten kommen DIREKT in den Wagen („Zum Einkaufswagen
    # hinzugefügt“) bzw. zeigen den Neukunden-Hinweis. Vorher wurde danach der graue Knopf ein ZWEITES Mal gedrückt
    # (er stand noch unten) → doppelt im Wagen bzw. falscher Neukunden-Weg. Jetzt erst das Ergebnis abwarten.
    erg, tx = _wagen_warten(3.0)
    if erg == "ok":
        log("im Einkaufswagen"); return
    if erg == "neukunde":
        _neukunde_merken(); return
    if erg is None:                                              # kein Hinweis gelesen (Toast kurz/blass) → nicht nochmal
        log("kein Hinweis nach dem Einkaufswagen-Tipp – Liste prüft das oberste Produkt"); return   # tippen
    versucht = set()
    for runde in range(3):                                       # Artur 13.11.: irgendeine Variante/Größe, Hauptsache schnell
        if _wagen_runde(versucht):
            return
    raise Stopp("nicht in den Einkaufswagen gelegt")


KEIN_OPTION = re.compile(r"(?i)nicht vorr|vorrätig|menge|einkaufswagen|tabelle|lieferung|versand|kasse|€|^\W*[+\-–]?\W*$|^\d{1,3}$")


def varianten_optionen(tx, probiert=()):
    """Reine Funktion (Artur 16.11.2026, Tatort: „nimm doch einfach die andere Variante“): Varianten-Blatt mit „Der Artikel
    ist nicht vorrätig“ → (Gruppe (x, y) oder None, Liste antippbarer Optionen [(text, x, y)]). Gruppe = „Größe“/„Farbe“
    bzw. die unterste „Name:“-Zeile (Fall:, Sorte: …), aber nie „Menge:“. Optionen = Texte unter der Gruppe, oberhalb von
    „Menge“/Hinweis/rotem Knopf; nie „+“/„-“, Menge, Hinweis, Preis, Einkaufswagen (vorher hätte „+“ die Menge erhöht).
    Ohne Texte: Bildkacheln nebeneinander (auch die müssen über „Menge“/Hinweis liegen)."""
    unten = min([t[2] for t in tx if re.match(r"(?i)\W*menge\b", t[0].strip()) and t[2] > 450]
                + [t[2] for t in tx if "vorrätig" in t[0].lower() and t[2] > 450]
                + [t[2] for t in tx if t[0].strip() == "Einkaufswagen" and t[2] > 600] + [700])
    gr = None
    for w in ("Größe", "Farbe"):
        kand = [t for t in tx if t[0].strip().lower().startswith(w.lower()) and "tabelle" not in t[0].lower()
                and 150 < t[2] < unten]
        if kand:
            gr = (kand[-1][1], kand[-1][2]); break
    if not gr:                                                   # „Fall:“, „Sorte:“ … → unterste „Name:“-Zeile
        kopf = [t for t in tx if re.match(r"^[A-Za-zÄÖÜäöü][\w ]{1,20}:", t[0].strip()) and 250 < t[2] < unten
                and not re.match(r"(?i)\W*menge", t[0].strip())]
        if kopf:
            k = max(kopf, key=lambda t: t[2]); gr = (k[1], k[2])
    if not gr:
        return None, []
    texte = [t for t in tx if gr[1] + 15 < t[2] < min(gr[1] + 110, unten - 8) and t[0].strip()
             and not KEIN_OPTION.search(t[0].strip())]
    opt = [t for t in texte if (round(t[1]), round(t[2])) not in probiert]
    if not texte and gr[1] + 55 < unten - 15:                    # Varianten nur als Bilder → Kacheln nebeneinander
        opt = [("", x, gr[1] + 55) for x in (50, 130, 212, 294) if (round(x), round(gr[1] + 55)) not in probiert]
    return gr, opt


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
        gr, opt = varianten_optionen(tx, probiert)               # 16.11.2026: reine Funktion (offline getestet)
        if not opt:
            raise Entwurf("Artikel nicht vorrätig, keine weitere Variante")
        o = min(opt, key=lambda t: (round(t[2] / 10), t[1]))
        probiert.add((round(o[1]), round(o[2])))
        tipp(o[1], o[2], tx, "Variante"); ruhe(0.9)
    tx = lesen()
    if seh.finde("nicht vorrätig", tx):
        raise Entwurf("Artikel nicht vorrätig (keine vorrätige Variante)")
    erg = wagen_ergebnis(tx)                                     # Hinweis kam schon während der Variantenwahl
    if erg == "ok":
        log("im Einkaufswagen"); return True
    if erg == "neukunde":
        _neukunde_merken(); return True
    if seh.finde("Kasse", tx, unter=600):                        # kein Varianten-Blatt (Produktseite) → nie den grauen
        log("Varianten-Blatt zu, kein Hinweis – Liste prüft das oberste Produkt"); return True   # Knopf nochmal
    btn = [t for t in tx if t[2] > 600 and t[0].strip() == "Einkaufswagen"]
    muss(btn, "rotes „Einkaufswagen“ im Varianten-Blatt fehlt")
    tipp(btn[0][1], btn[0][2], tx, "Einkaufswagen (rot)"); ruhe(0.6)
    for i in range(14):
        tx = lesen()
        erg = wagen_ergebnis(tx)
        if erg == "ok":
            log("im Einkaufswagen"); return True
        if erg == "neukunde":                                    # Artur 16.11.: kann nicht in den Wagen → Szenario 3
            _neukunde_merken(); return True
        if seh.finde("Bitte auswählen", tx):
            log("noch eine Auswahl offen → nächste Variante"); return False
        if not [t for t in tx if t[2] > 600 and t[0].strip() == "Einkaufswagen"] and i >= 4:
            log("im Einkaufswagen (Blatt zu)"); return True      # Artur 13.11.: nicht extra in den Warenkorb gehen
        time.sleep(0.3)
    return False


# ---------------------------------------------------------------- 4) Produktseite zu → „+“ → Video

def warte_bildschirm(ziele, max_s, min_s=0.3, nachlauf=0.35):
    """16.11.2026 (Tempo): statt fester Pause nach einem Tipp warten, bis einer der erwarteten Bildschirme erkannt ist
    (dann kurz nachlaufen lassen – Animation), höchstens max_s = die alte feste Pause. Nie langsamer als vorher, und
    der nächste Schritt passiert erst, wenn der neue Bildschirm wirklich da ist (die Zustandsmaschine prüft ihn ohnehin)."""
    time.sleep(min_s)
    ende = time.time() + max(0.0, max_s - min_s)
    for _ in range(int(max_s / 0.2) + 2):                        # Rundenzahl begrenzt (Tests ohne echte Pausen)
        if time.time() >= ende:
            break
        z, _tx, _t = lage()
        if z in ziele:
            time.sleep(nachlauf); return z
        time.sleep(0.15)
    return None


def _zurueck_in_tiktok():
    """Nach einem AirDrop mitten im Erstellen (Fotos springt auf): zurück in TikTok, ohne den Beitrag zu verlieren –
    „◂ TikTok“ oben links bzw. app("TikTok") (erkennt Galerie/Kamera/Editor jetzt als TikTok)."""
    try:
        z, tx, _t = lage()
        if z in ERSTELLEN_SEITEN or z == B.BEITRAG:
            return
        app("TikTok")
    except Stopp as e:
        log(f"zurück in TikTok: {e}")


def zum_plus():
    """16.11.2026: Produktseite/Blätter über die Zustandsmaschine schließen (X oben links bei der Social1-Produktseite,
    Blätter runterwischen) – der alte Wisch vom linken Rand auf Höhe 400 blätterte nur das Produktbild (vgl. 15.11. 19:50)
    und kostete bis zu 4 Runden, bevor die Hauptseite geholt wurde."""
    for i in range(3):
        tx = lesen()
        if not _tabs(tx):
            tx = zur_hauptseite(abbrechen=True)
        if _tabs(tx):
            tipp(167, 681, tx, "+"); warte_bildschirm((B.KAMERA, B.GALERIE), 1.6)
            return
    raise Stopp("„+“ nicht erreicht")


_KYR = str.maketrans("ЗОАЕТСВМНКРХІ×", "3OAETCBMHKPXIX")   # 15.11.: OCR liest „З0-TEILIGES“ (kyrillisch)


def _kn(t):
    import unicodedata
    t = t.upper().translate(_KYR).replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", t))


def _passt(kachel, ocr):
    k, o = _kn(kachel), _kn(ocr)
    if bool(k) and (o.startswith(k[:max(6, len(k) - 2)]) or (len(o) >= 6 and k.startswith(o))):
        return True
    # 16.11.2026 (HOTU): OCR las „ANHÄNGER“ als „ANMANGER“ → Kachel nie gefunden, Lauf hing. Ähnlichkeit ≥ 85 %
    # (ab 10 Zeichen); Länge ±1 s bleibt Pflicht, fremde Hooks sind weit darunter.
    import difflib
    if len(k) >= 10 and len(o) >= 10 and difflib.SequenceMatcher(None, k, o[:len(k) + 2]).ratio() >= 0.85:
        return True
    # 16.11.2026 (Tempo): kurze Hooks (6–9 Zeichen, z. B. „EISTEE?!“) hatten gar keine Toleranz → genau EIN gelesener
    # Buchstabe darf abweichen (gleiche Länge), sonst nichts. Länge ±1 s bleibt in der Galerie Pflicht.
    return 6 <= len(k) < 10 and len(o) >= len(k) and sum(a != b for a, b in zip(k, o[:len(k)])) <= 1


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
_AKT_DATEI = None    # Datei des Videos, das gerade gepostet wird (für ein zweites AirDrop)


def cover_passt(tx, kachel):
    """Reine Funktion: Cover oben rechts auf der Beitragsseite zeigt den Hook? → (ok, cover-texte)."""
    cover = [t for t in tx if t[1] > 200 and t[2] < 200 and not re.search(r"cover|bearbeiten", t[0], re.I)]
    # 16.11.2026: Hook im Cover steht oft auf 2–3 Zeilen (OCR liest sie einzeln) → auch die Zeilen zusammen prüfen
    zusammen = " ".join(t[0] for t in sorted(cover, key=lambda t: t[2]))
    return any(_passt(kachel, t[0]) for t in cover) or (len(cover) > 1 and _passt(kachel, zusammen)), cover


def cover_pruefen(kachel):
    """Artur 15.11.2026: falsches Video = Verstoß/Kontosperre. Zweite, unabhängige Prüfung auf der Beitragsseite:
    Hook-Text im Cover (oben rechts) muss zum Video passen – sonst STOPP, bevor getippt/verlinkt/gespeichert wird."""
    cover = []
    for _ in range(8):
        tx = lesen()
        ok, cover = cover_passt(tx, kachel)
        if ok:
            log(f"Cover passt: {kachel}"); return
        time.sleep(0.5)
    raise Sperre(f"Cover zeigt nicht „{kachel}“ ({[t[0] for t in cover][:3]}) – falsches Video, NICHT gepostet")


_NEUKUNDE = False


def tastatur_offen(tx):
    """Reine Funktion: iPhone-Tastatur unten sichtbar (einzelne Buchstaben-Tasten / „123“ / „ABC“ im unteren Drittel)."""
    tasten = [t for t in tx if t[2] > 430 and re.fullmatch(r"[a-zäöüß]", t[0].strip().lower())]
    return len(tasten) >= 6 or any(t[0].strip() in ("123", "ABC") and t[2] > 560 for t in tx)


def produktname_feld_tippen(tx, lab_y):
    time.sleep(0.6); tx = lesen()                                # 16.11.: Hinweisband „Überprüfe die Qualität …“ schiebt
    jetzt = seh.finde("Produktname", tx, genau=True)             # das Feld nach dem Laden nach unten → frisch lesen
    lab_y = jetzt[1] if jetzt else lab_y
    """15.11.2026 21:17: direkt AUF den vorhandenen Namen tippen (Mitte+), nicht rechts daneben (200) – dort bekam das
    Feld keinen Fokus (Belibuy: Name blieb stehen). Getestet: Tipp auf Text → ⌘A → 40× Löschen → tippen = 16/30."""
    # Artur 16.11.2026 19:30: „du klickst das Textfeld am Anfang weg, deswegen kannst du nicht reinschreiben“ – auf
    # „Produkt umbenennen“ ist das Feld schon aktiv (Tastatur offen, siehe Aufnahmen). Dann NICHT tippen, direkt ⌘A/Löschen.
    # 17.11.2026 (147-03): bei schon offener Tastatur kamen ⌘A/Löschen/Tippen nicht an → immer direkt AUF den Namen tippen
    # (Tipp auf den Text behält/holt den Fokus; nie daneben).
    z = [t for t in tx if lab_y + 35 < t[2] < lab_y + 95 and t[1] < 230 and not re.fullmatch(r"\d{1,2}/30", t[0].strip())
         and "Produktname wird" not in t[0] and "Zeichen wird" not in t[0]]
    if z:
        tipp(min(z[0][1] + 40, 250), z[0][2], tx, "Produktname (auf den Text)")
    else:
        tipp(60, lab_y + 59, tx, "Produktname-Feld")
    ruhe(0.6)


def feldzeile(tx, lab_y):
    """Reine Funktion: Text in der Produktname-Zeile (unter dem Label, ohne Hinweis-/Zähler-Texte)."""
    jetzt = seh.finde("Produktname", tx, genau=True)
    lab_y = jetzt[1] if jetzt else lab_y
    z = [t[0].strip() for t in tx if lab_y + 35 < t[2] < lab_y + 95 and t[1] < 230 and "Produktname wird" not in t[0]
         and "Zeichen wird" not in t[0] and "Ungültige" not in t[0] and not re.fullmatch(r"\d{1,2}/30", t[0].strip())]
    return " ".join(z)


def feld_zaehler(tx, lab_y):
    """Reine Funktion: Zähler „N/30“ neben dem Label Produktname → N (None, wenn nicht lesbar)."""
    jetzt = seh.finde("Produktname", tx, genau=True)
    lab_y = jetzt[1] if jetzt else lab_y
    z = [t for t in tx if re.fullmatch(r"\d{1,2}/30", t[0].strip()) and abs(t[2] - lab_y) < 15]
    return int(z[0][0].strip().split("/")[0]) if z else None


def feld_leeren(lab_y):
    """17.11.2026 (148-01 ESN, Steuer-Chat): Produktname-Feld robust leeren – Feld antippen, Cursor ans Ende (⌘→),
    so oft Löschen wie Zeichen drin sind (+5), dann am Bildschirm prüfen, dass es leer ist (0/30). Vorher blieb mit
    ⌘A/Löschen der alte Name „ESN Vitamin D3+K2 Daily Tablet“ stehen. Gibt True zurück, wenn das Feld leer ist."""
    for runde in range(3):
        tx = lesen()
        n = feld_zaehler(tx, lab_y)
        if n == 0:
            return True
        produktname_feld_tippen(tx, lab_y)
        K().taste("cmd+a"); ruhe(0.2)
        try:
            K().aktion("hid", keys=[[8, 0x4F]])                  # ⌘→ = Cursor ans Zeilenende
        except Exception as e:
            log(f"Cursor ans Ende ging nicht: {e}")
        ruhe(0.2)
        K().loeschen((n if n is not None else 30) + 5); ruhe(0.5)
        for _w in range(6):
            n2 = feld_zaehler(lesen(), lab_y)
            if n2 == 0:
                return True
            time.sleep(0.4)
        log(f"Produktname-Feld nicht leer ({n2}/30) – nochmal leeren")
    return False


def name_ok(tx, lab_y, alt=None):
    """Produktname im Umbenennen-Feld = _BUTTON? OCR-tolerant (Auswahl-Griffe/Cursor lesen sich mit, 15.11. 20:26 WMF:
    richtiger Name, 4× neu getippt) – ähnlicher Text in der Feldzeile ODER Zähler „N/30“ mit N = Länge."""
    jetzt = seh.finde("Produktname", tx, genau=True)            # 15.11. 21:21: Lage frisch lesen – die gemerkte
    if jetzt:                                                    # stammte aus dem noch hereinfahrenden Bildschirm
        lab_y = jetzt[1]
    zeile = [t for t in tx if lab_y + 30 < t[2] < lab_y + 95]
    if any(_gleich(t[0], _BUTTON) or _kn(_BUTTON) in _kn(t[0]) and len(_kn(t[0])) <= len(_kn(_BUTTON)) + 2 for t in zeile):
        return True
    # Zähler „N/30“ nur noch als Hilfe, wenn sich der Feldtext gegenüber VORHER geändert hat. Artur 16.11.2026 17:31:
    # Fanttik – alter Name „E1 Max Schrauber“ blieb stehen, hat aber wie „Wenige verfügbar“ 16 Zeichen → Zähler 16/30
    # meldete fälschlich „umbenannt“.
    if alt is None or _gleich(feldzeile(tx, lab_y), alt) or _kn(feldzeile(tx, lab_y)) == _kn(alt):
        return False
    zaehler = [t for t in tx if re.fullmatch(r"\d{1,2}/30", t[0].strip()) and abs(t[2] - lab_y) < 15]
    return bool(zaehler) and int(zaehler[0][0].split("/")[0]) == len(_BUTTON.strip())


def erstellen_route(ausverkauft=False):
    """Artur 15.11.2026 (seit 19:58 für JEDES Produkt – „Showcase/Einkaufswagen-Liste ist zu komplex“):
    Produktseite → „pro Verkauf“ → (steht „Zum Showcase hinzufügen“: antippen) → unterer Knopf „Jetzt erstellen“ bzw. „Mehr erkunden“
    → „Videos – Lade ein Video hoch“ → Produktname umbenennen → Hinzufügen → Kamera (Galerie unten rechts).
    Produkt ist damit verlinkt – kein Auswählen aus Listen. Ausverkauft: nur ins Showcase, dann Entwurf ohne Link.
    Zustandsmaschine: setzt an jedem dieser Bildschirme fort."""
    umbenannt = False; feld_warten = 0; unklar = 0; mehr = 0
    for _ in range(36):
        z, tx, _t = lage()
        if z == B.KAMERA:
            log("Produkt über „Jetzt erstellen“ verlinkt"); return
        if z == B.LIVE:
            raise Stopp("LIVE-Seite statt Kamera")              # nie „LIVE gehen“ – Rückweg macht zur_hauptseite
        if z == B.DLG_VERSTANDEN:
            nv = seh.finde("nicht verfügbar", tx) or seh.finde("nicht hinzugefügt", tx) or seh.finde("nicht verfugbar", tx)
            dialog_wegmachen(z, tx)
            if nv:
                raise Entwurf("Produkt nicht verfügbar (gesperrt) → Entwurf ohne Link")
            continue
        if dialog_wegmachen(z, tx):
            continue
        if z == B.BEWERBEN:
            # Artur 15.11.2026: „zu schnell geklickt, auf Karussell statt Video“ → erst tippen, wenn das Blatt ruht
            # (zwei Bilder mit gleicher Lage), und nur die Zeile „Videos“ – klar über „Karussells“
            v = seh.finde("Videos", tx, genau=True)
            time.sleep(0.7); tx2 = lesen()
            v2 = seh.finde("Videos", tx2, genau=True); ka2 = seh.finde("Karussell", tx2)
            if not (v and v2 and abs(v[1] - v2[1]) < 3 and (not ka2 or ka2[1] - v2[1] > 50)):
                time.sleep(0.5); continue
            tipp(v2[0], v2[1] + 10, tx2, "Videos (Lade ein Video hoch)")   # 16.11.: war feste 2,5 s
            warte_bildschirm((B.UMBENENNEN, B.KAMERA), 2.5); continue
        if z == B.UMBENENNEN:
            if not umbenannt:
                lab = seh.finde("Produktname", tx, genau=True)
                if not lab or not seh.finde("/30", tx):
                    feld_warten += 1
                    if feld_warten <= 6:
                        time.sleep(1.0); continue                # 15.11.: erst tippen, wenn das Feld geladen ist
                    # Artur 15.11.2026 21:10: Produkt zum 2. Mal über „Jetzt erstellen“ → Name nicht änderbar → überspringen
                    log("Produktname-Feld nicht änderbar (Produkt schon einmal so verlinkt) → Umbenennen übersprungen")
                    umbenannt = True; continue
                alt = feldzeile(tx, lab[1])                      # Name vorher (für die Zähler-Prüfung)
                if not feld_leeren(lab[1]):                      # 17.11.: robust leeren (0/30), dann tippen
                    log("Produktname-Feld lässt sich nicht leeren")
                menschlich(_BUTTON); ruhe(0.3)
                # Artur 15.11.2026 20:28: „gib einfach die Textvorschläge für den Produktnamen ein“ → einmal tippen,
                # keine Neu-tipp-Schleife; aber warten, bis TikTok den Text übernommen hat (Eingaben kommen verzögert
                # an – 20:37 blieb sonst der alte Name stehen), erst dann Return/Hinzufügen
                ok = False
                for runde in range(2):
                    for _w in range(20):                         # 16.11.: öfter nachsehen, gleiche Gesamtzeit
                        tx = lesen()
                        if name_ok(tx, lab[1], alt):
                            ok = True; break
                        time.sleep(0.5)
                    if ok:
                        break
                    zeile = [t[0] for t in tx if lab[1] + 30 < t[2] < lab[1] + 95 or abs(t[2] - lab[1]) < 15]
                    foto = AUS / f"umbenennen-{time.strftime('%H%M%S')}.png"
                    try:
                        seh.kabel().foto(str(foto))
                    except Exception:
                        pass
                    log(f"Produktname nicht übernommen – Feld zeigt {zeile} (Foto {foto.name})")
                    if runde == 0:                               # Artur 21:12: „es war doch da“ → einmal neu: Feld
                        feld_leeren(lab[1])                      # antippen, leeren (0/30), tippen
                        menschlich(_BUTTON); ruhe(1.0)
                if ok:
                    log(f"umbenannt: {_BUTTON}")
                else:                                            # Artur 21:10: Name lässt sich nicht ändern → überspringen
                    log("Produktname nicht änderbar → Umbenennen übersprungen")
                umbenannt = True
                K().taste("return"); ruhe(1.2); continue
            hz = seh.finde("Hinzufügen", tx, unter=600)
            if hz:
                if kuerzlich("erstellen-hinzu", 4.0):           # 16.11.: nie zweimal in Folge; war feste 3 s
                    time.sleep(0.5); continue
                tipp(hz[0], hz[1], tx, "Hinzufügen"); merke("erstellen-hinzu"); ruhe(1.5)
            else:
                time.sleep(0.8)
            continue
        if z == B.WERBE_BLATT:
            sc = seh.finde("Showcase hinzufügen", tx)
            if sc:                                               # Artur 15.11.: steht es da → ins Showcase
                tipp(sc[0], sc[1], tx, "Zum Showcase hinzufügen"); ruhe(1.6)
                if showcase_voll(lesen()):
                    raise Hart("Showcase voll – Artur löscht selbst, danach neu starten")
                log("ins Showcase gelegt")
                if ausverkauft:
                    raise Entwurf("ausverkauft – ins Showcase gelegt, Entwurf ohne Link")
                continue
            if ausverkauft and (seh.finde("Jetzt erstellen", tx) or seh.finde("Mehr erkunden", tx)):
                raise Entwurf("ausverkauft (schon im Showcase) → Entwurf ohne Link")
            # Artur 15.11.2026 20:12: „Mehr erkunden heißt das auch – halt quasi immer der Button, wo der Showcase
            # eigentlich steht oder der durch den Showcase ersetzt wird“ → unteren Knopf antippen, ob „Jetzt erstellen“
            # oder „Mehr erkunden“
            # Artur 16.11.2026 19:40: NIE „Mehr erkunden“ antippen – das steht direkt nach „Zum Showcase hinzufügen“
            # kurz da und führt auf die Showcase-Seite („Entdecken | Verwalten“). Nur „Jetzt erstellen“. Steht nur
            # „Mehr erkunden“: kurz warten, sonst Blatt zu und „pro Verkauf“ neu öffnen.
            j = seh.finde("Jetzt erstellen", tx, unter=560)
            if j:
                tipp(j[0], j[1], tx, "Jetzt erstellen")             # 16.11.: war feste 2,5 s → bis das Blatt da ist
                warte_bildschirm((B.BEWERBEN, B.UMBENENNEN, B.KAMERA), 2.5); continue
            if seh.finde("Mehr erkunden", tx, unter=560):
                mehr += 1
                if mehr % 3 == 0:
                    if mehr > 9:
                        try:                                     # 17.11.2026 (148-08/32): Bild + Text sichern
                            foto = AUS / f"mehr-erkunden-{time.strftime('%H%M%S')}.png"; seh.kabel().foto(str(foto))
                            log(f"nur „Mehr erkunden“ – Foto {foto.name} – Bildschirm: {bildschirmtext(tx, 80)}")
                        except Exception:
                            pass
                        raise Stopp("„Jetzt erstellen“ erscheint nicht (nur „Mehr erkunden“)")
                    log("nur „Mehr erkunden“ (nicht antippen) → Blatt zu, „pro Verkauf“ neu")
                    blatt_runter(130)
                else:
                    time.sleep(0.8)
                continue
            time.sleep(0.8); continue                            # Blatt lädt noch
        if z == B.SHOWCASE_SEITE:                                # 16.11.: nach „Zum Showcase hinzufügen“ öffnet TikTok
            tipp(20, (seh.finde("Verwalten", tx) or (0, 57))[1], tx, "Zurück (Showcase-Seite)", abstand=20)   # teils die
            ruhe(1.2); continue                                  # Showcase-Seite → zurück zur Produktseite
        if z in (B.FEED, B.PROFIL, B.TIKTOK) or (z == B.UNBEKANNT and _tabs(tx)):
            raise Stopp("„Jetzt erstellen“-Weg verloren (Hauptseite) – Produkt neu über Social1")
        if z in (B.PRODUKTSEITE, B.VARIANTEN):
            v = seh.finde("pro Verkau", tx, unter=520)               # 16.11.: nie „Mehr erkunden“ antippen
            if v and z == B.PRODUKTSEITE:
                tipp(v[0], v[1], tx, "pro Verkauf"); ruhe(1.6)
            else:
                blatt_runter(130)                                # Varianten-/Werbeblatt zu
            continue
        if z in (B.UNBEKANNT, B.LADEN) and unklar < 4:          # 16.11.: Neukunden-Hinweis/Toast liegt kurz über der
            unklar += 1; time.sleep(0.8); continue               # Seite (15.11. 19:48 sofort Stopp → Weg verloren)
        raise Stopp(f"„Jetzt erstellen“-Weg: unerwarteter Bildschirm „{z}“")
    raise Stopp("„Jetzt erstellen“-Weg kam nicht zur Kamera")


def _sek(dauer):
    m, sk = dauer.strip().lstrip("~•").split(":")
    return int(m) * 60 + int(sk)


def galerie_kachel(tx, kachel, soll_dauer):
    """Artur 14./15.11.2026 (Pflicht-Prüfung 1): Kachel nur, wenn Länge (±1 s) UND Hook-Text darunter passen –
    neueste passende (unten rechts). → (x, y) zum Antippen oder None. Reine Funktion (offline getestet)."""
    dauern = B.dauern(tx)

    def hook_ok(t):
        # 17.11.2026 (147-25 UNO): Hook ganz oben in der Kachel liegt ~98 über der Länge → bis 108 (Kachel ~112 hoch,
        # Hook der Kachel darüber liegt immer > 112 entfernt)
        unter = [u for u in tx if abs(u[1] - t[1] + 40) < 60 and 25 < t[2] - u[2] < 108 and not B.dauer_text(u[0])]
        return any(_passt(kachel, u[0]) for u in unter)
    passend = [t for t in dauern if (soll_dauer is None or abs(_sek(t[0]) - soll_dauer) <= 1.1) and hook_ok(t)]
    if not passend:
        return None
    letzte = max(passend, key=lambda t: (round(t[2] / 20), t[1]))
    return letzte[1] - 40, letzte[2] - 50


def auswahl_weiter(tx, kachel, soll_dauer):
    """17.11.2026 (147-24, neue TikTok-Ansicht nach Arturs Umstellung): nach dem Kachel-Tipp „Ausgewählt (1)“ oben rechts,
    unten Mini-Kachel mit Hook + Länge, rechts „Weiter (1)“, links „AutoCut“ (nie antippen). Reine Funktion: (x, y) von
    „Weiter (1)“ nur, wenn genau 1 Video gewählt ist UND Mini-Kachel Hook + Länge (±1 s) passen; „Weiter (2+)“ → Sperre."""
    if not seh.finde("Ausgew", tx, ueber=130):
        return None
    w = [t for t in tx if t[2] > 600 and t[1] > 167 and re.match(r"\s*weiter\s*\(\s*\d+\s*\)", t[0].lower())]
    if not w:
        return None
    n = int(re.search(r"\((\s*\d+)", w[0][0]).group(1))
    if n != 1:
        raise Sperre(f"Auswahl-Ansicht: {n} Videos ausgewählt – nicht weiter")
    mini = [(B.dauer_text(t[0]), t[1], t[2]) for t in tx if 600 < t[2] < 740 and B.dauer_text(t[0])]   # Mini-Kachel unten
    dauer_ok = soll_dauer is None or any(abs(_sek(t[0]) - soll_dauer) <= 1.1 for t in mini)
    hook_ok = any(_passt(kachel, t[0]) for t in tx if 560 < t[2] < 720)
    if not hook_ok:                                              # 17.11. (147-17): Mini-Kachel zeigt Produktbild, Hook-Text
        mini_text = [t for t in tx if t[1] < 130 and 600 < t[2] < 740 and not B.dauer_text(t[0])]   # unlesbar → reicht
        hook_ok = not mini_text                                  # die Länge (Kachel war vorher Länge + Hook ✓, Cover-
                                                                 # Prüfung folgt); fremder lesbarer Text → nein
    return (w[0][1], w[0][2]) if dauer_ok and hook_ok else None


FFMPEG = next((x for x in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg",
                             os.path.expanduser("~/Documents/Coding/Editing System 1.1/tools/bin/ffmpeg")) if os.path.exists(x)), "ffmpeg")


def dauer_position(tx, hx, hy):
    """Reine Funktion: Lage des Längen-Labels (unten rechts in der Kachel) zu einem Hook-Text bei (hx, hy):
    Spalte aus x (3 Spalten, Labels bei ~92/201/313), Zeile = nächste bekannte Label-Zeile unter dem Hook."""
    sp = min(2, max(0, round((hx - 55) / 111)))
    zeilen = sorted({round(t[2]) for t in B.dauern(tx)})
    unter = [y for y in zeilen if y > hy + 15]
    return 92 + 110.5 * sp, (unter[0] if unter else hy + 98)


def dauer_nachlesen(x, y):
    """17.11.2026 (147-25 UNO): „00:11“ auf hellem Hintergrund liest die OCR im ganzen Bild nicht → Ausschnitt um (x, y)
    (334×735-Rahmen) 4× vergrößert lesen, erst mit Schwelle (nur reines Weiß = Schrift), sonst roh."""
    quelle = os.path.join(seh.TMP, "f.png")
    for filt in ("format=gray,lutyuv=y='if(gte(val\\,245)\\,0\\,255)'", "null"):
        ziel = os.path.join(seh.TMP, "dauer.png")
        vf = (f"crop=w=iw*70/334:h=ih*26/735:x=iw*{x - 35:.1f}/334:y=ih*{y - 13:.1f}/735,"
              f"scale=iw*4:ih*4,{filt}")
        try:
            subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", quelle, "-vf", vf, ziel], check=True, timeout=10)
            for z in seh._ocr(ziel).splitlines():
                d = B.dauer_text(z.partition("\t")[2])
                if d:
                    return d
        except Exception:
            pass
    return None


def mehrfach_an(y):
    """Haken „Mehrere auswählen“ rot (an)? Weißer Haken im roten Kreis → mehrere Punkte um den Kreis (Text-Zeile y)."""
    pts = [(15, y - 7), (18, y - 7), (21, y - 7), (24, y - 1), (12, y - 1), (15, y + 2), (24, y + 2)]
    rot = [f for f in farben(*pts) if f[0] > 225 and f[1] < 110 and f[2] < 150]
    return len(rot) >= 4


def galerie_kachel_nachlesen(tx, kachel, soll_dauer):
    """Kachel mit sicherem Hook, deren Länge die OCR nicht gelesen hat → Länge im Ausschnitt nachlesen. Pflicht-Prüfung
    bleibt: Länge ±1 s UND Hook. → (x, y) zum Antippen oder None."""
    if soll_dauer is None:
        return None
    treffer = []
    for t in tx:
        if 120 < t[2] < 650 and _passt(kachel, t[0]):
            x, y = dauer_position(tx, t[1], t[2])
            if any(abs(d[1] - x) < 25 and abs(d[2] - y) < 15 for d in B.dauern(tx)):
                continue                                         # Länge war lesbar (passte nicht) → nicht raten
            d = dauer_nachlesen(x, y)
            log(f"Länge im Ausschnitt nachgelesen ({x:.0f},{y:.0f}): {d}")
            if d and abs(_sek(d) - soll_dauer) <= 1.1:
                treffer.append((x - 40, y - 50))
    return max(treffer, key=lambda p: (round(p[1] / 20), p[0])) if treffer else None


def zum_beitrag(kachel, galerie=None, warten_s=120):
    """Zustandsmaschine „+“ → Beitragsseite (Artur 15.11.2026): jede Runde Bildschirm lesen, genau ein Schritt.
    Hakt etwas, geht es am aktuellen Bildschirm weiter. Video NUR mit passender Länge + Hook (sonst Sperre)."""
    gewaehlt = bestaetigt = nochmal = neu_geoeffnet = False
    seit = vor_ziel = None
    gemeldet = fotos_zurueck = 0
    unbekannt_seit = None
    galerie_foto = mehrfach_getippt = False
    for _ in range(90):                                          # 16.11.: 90 Runden (Warten jetzt 2 s statt 5 s je Runde)
        z, tx, tabs = lage()
        if z != B.UNBEKANNT:
            unbekannt_seit = None
        if z == B.BEITRAG:
            if seh.finde("Vorlage", tx):                         # Artur 13.11.: AutoCut/Vorlage (Musik) am Video
                raise Sperre("Vorlage/AutoCut am Video (Musik!) – nicht posten")
            return tx
        if dialog_wegmachen(z, tx):
            continue
        if z in (B.FOTOS_VOLLBILD, B.FOTOS_ALBUM, B.FOTOS_MEDIATHEK) and fotos_zurueck < 2:
            fotos_zurueck += 1                                   # 16.11.: spät angekommenes AirDrop öffnet Fotos →
            _zurueck_in_tiktok(); continue                       # zurück in TikTok (Galerie), nicht abbrechen
        if z in (B.FEED, B.PROFIL, B.TIKTOK) and tabs:
            tipp(167, 681, tx, "+"); warte_bildschirm((B.KAMERA, B.GALERIE), 1.6); continue
        if z == B.KAMERA:
            if galerie:                                          # 15.11.: Kamera aus „Jetzt erstellen“ → Galerie unten rechts
                tipp(galerie[0], galerie[1], tx, "Galerie unten rechts"); warte_bildschirm((B.GALERIE,), 2.0)
            else:
                tipp(30, 672, tx, "Galerie unten links", abstand=60); warte_bildschirm((B.GALERIE,), 1.6)
            continue
        if z == B.GALERIE or (z == B.VORSCHAU and not bestaetigt):
            if z == B.VORSCHAU:                                  # Vorschau: Hook steht im Bild (falls lesbar), dann Auswählen
                a = seh.finde("Auswählen", tx, genau=True) or seh.finde("Auswahlen", tx, genau=True)
                tipp(a[0], a[1], tx, "Auswählen"); ruhe(0.9); bestaetigt = gewaehlt = True; continue
            w = seh.finde("Weiter", tx, genau=True, unter=600)
            if gewaehlt and w and w[0] > 167:
                tipp(w[0], w[1], tx, "Weiter"); warte_bildschirm((B.EDITOR, B.BEITRAG), 2.2); continue
            m = seh.finde("Mehrere auswählen", tx) or seh.finde("Mehrere auswahlen", tx)
            if m and not mehrfach_getippt and mehrfach_an(m[1]):   # 17.11.2026 (Artur: „Claude schaltet aus“): Mehrfach-
                mehrfach_getippt = True                          # Auswahl aus – höchstens EIN Tipp pro Video (nie hin und her)
                if not kuerzlich("mehrfach-aus", 3.0):           # (roter Haken unten links)
                    tipp(19, m[1], tx, "Mehrere auswählen (aus)"); merke("mehrfach-aus"); ruhe(0.8)
                    lesen(); log("„Mehrere auswählen“ ausgeschaltet" if not mehrfach_an(m[1]) else
                                 "„Mehrere auswählen“ noch an")
                else:
                    time.sleep(0.4)
                continue
            ziel = galerie_kachel(tx, kachel, _SOLL_DAUER)
            if not ziel and seit and time.time() - seit > 4:
                ziel = galerie_kachel_nachlesen(tx, kachel, _SOLL_DAUER)
            if not ziel:
                seit = seit or time.time()
                if time.time() - seit > warten_s:
                    raise Sperre(f"gesendetes Video „{kachel}“ ({_SOLL_DAUER and round(_SOLL_DAUER)} s) nicht in der Galerie "
                                 "– NICHT gepostet")
                if time.time() - seit > 15 and not nochmal and _AKT_DATEI \
                   and _AIRDROPS.get(_AKT_DATEI, 0) < 2:          # Artur 16.11.2026 22:25: „wenn der AirDrop nicht
                    nochmal = time.time()                        # zuverlässig ist bzw. lange dauert, airdrop nochmal“
                    _AIRDROPS[_AKT_DATEI] = _AIRDROPS.get(_AKT_DATEI, 0) + 1   # (vorher schon 2× → nicht nochmal)
                    try:
                        import airdrop
                        airdrop.senden([str(frisch_datiert(EIN / _AKT_DATEI))])
                        log("Video nach 15 s nicht in der Galerie → nochmal per AirDrop")
                    except Exception as e:
                        log(f"zweites AirDrop ging nicht: {e}")
                    _zurueck_in_tiktok()                         # 16.11.: Fotos springt nach dem AirDrop auf → zurück in
                    continue                                     # die Galerie (vorher Hänger „unbekannt“, Video 145-08)
                if nochmal and not neu_geoeffnet and time.time() - nochmal > 10:
                    neu_geoeffnet = True                         # 16.11.: Galerie zeigt neue Videos evtl. erst nach dem
                    log("nach dem 2. AirDrop noch keine Kachel → Galerie neu öffnen")   # Neu-Öffnen → zu (Kamera), die
                    tipp(28, 74, tx, "Galerie zu"); ruhe(1.2); continue            # Kamera-Regel öffnet sie wieder
                if time.time() - gemeldet > 10:                  # Log höchstens alle 10 s (Kontext sparen)
                    log("keine Kachel mit passender Länge + Hook – Video noch nicht in Fotos, warte"); gemeldet = time.time()
                    if time.time() - seit > 20 and not galerie_foto:   # 17.11. (147-13): Beleg, was die Galerie zeigt
                        galerie_foto = True
                        try:
                            seh.kabel().foto(str(AUS / f"galerie-{time.strftime('%H%M%S')}.png"))
                        except Exception:
                            pass
                        log(f"Galerie (Längen/Texte): {[(t[0], round(t[1]), round(t[2])) for t in tx if 120 < t[2] < 700][:30]}")
                time.sleep(2); continue                          # 16.11.: war 5 s – nur Lesen, kein Tipp
            if not (vor_ziel and abs(vor_ziel[0] - ziel[0]) < 4 and abs(vor_ziel[1] - ziel[1]) < 4):
                vor_ziel = ziel; time.sleep(0.25); continue      # 16.11.: erst tippen, wenn die Kachel in zwei Bildern
            log(f"Video-Kachel „{kachel}“ bei {ziel[0]:.0f},{ziel[1]:.0f} ✓ (Länge + Hook)")   # gleich liegt (Galerie fährt ein)
            tipp(ziel[0], ziel[1], tx, "Video-Kachel"); warte_bildschirm((B.VORSCHAU,), 1.4); gewaehlt = True; continue
        if z == B.VORSCHAU and bestaetigt:
            w = seh.finde("Weiter", tx, genau=True, unter=600)
            if w and w[0] > 167:                                 # 13.11.: links liegt AutoCut (Vorlage + Musik)
                tipp(w[0], w[1], tx, "Weiter"); warte_bildschirm((B.EDITOR, B.BEITRAG), 2.2); continue
            time.sleep(0.6); continue
        if z == B.EDITOR:
            w = seh.finde("Weiter", tx, genau=True, unter=600)
            if not (w and w[0] > 167):
                raise Stopp("Editor: „Weiter“ nicht rechts – AutoCut-Gefahr")
            tipp(w[0], w[1], tx, "Weiter (Editor)"); warte_bildschirm((B.BEITRAG,), 2.0); continue
        if z == B.UNBEKANNT and gewaehlt:                        # 17.11.2026: neue Auswahl-Ansicht „Ausgewählt 1“ + „Weiter (1)“
            wa = auswahl_weiter(tx, kachel, _SOLL_DAUER)
            if wa:
                if kuerzlich("auswahl-weiter", 3.0):
                    time.sleep(0.4); continue
                log("Auswahl-Ansicht: 1 Video, Hook + Länge ✓ → Weiter (1)")
                tipp(wa[0], wa[1], tx, "Weiter (1)"); merke("auswahl-weiter")
                warte_bildschirm((B.EDITOR, B.BEITRAG), 2.2); continue
        if z == B.UNBEKANNT:                                     # 17.11.2026 (147-12/15): nach dem Kachel-Tipp fährt die
            unbekannt_seit = unbekannt_seit or time.time()       # Vorschau animiert ein → Zwischenbild „unbekannt“. Kein
            if time.time() - unbekannt_seit < 5:                 # Hänger: bis 5 s nur lesen (kein Tipp), dann erst Stopp
                time.sleep(0.4); continue                        # (→ Beitrag verwerfen + neu, Regel 17.11.)
            try:
                seh.kabel().foto(str(AUS / f"unbekannt-{time.strftime('%H%M%S')}.png"))
            except Exception:
                pass
            log(f"unbekannter Bildschirm 5 s: {[t[0] for t in tx][:12]}")
        raise Stopp(f"unerwarteter Bildschirm „{z}“ auf dem Weg zur Beitragsseite")
    raise Stopp("Beitragsseite nicht erreicht")


def video_waehlen(kachel, galerie=None):
    """Alter Name (Kompatibilität)."""
    return zum_beitrag(kachel, galerie)


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
            raise Sperre(f"{was} enthält Verbotenes („{v}“): {text!r} – nicht gepostet (Artur 14.11.: kein Preis, keine Versprechen)")


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


KURZTEXTE = ("schau mal was ich gefunden hab", "hab ich mir geholt", "gerade entdeckt", "richtig praktisch",
             "gefällt mir echt gut", "zeig ich euch mal", "bin begeistert", "das teil ist echt gut")


def kurztext(d):
    """Artur 16.11.2026: „ab sofort auch ein einfacher kurzer simpler Beschreibungstext, alles kleingeschrieben, nicht
    unbedingt Emojis“ (ersetzt „nur Hashtags“ vom 15.11.). Text aus der Eingang-JSON (`text`, vom Editing System beim
    Einreichen), sonst ein neutraler Standardsatz. Immer klein, ohne Emojis/#, höchstens 8 Wörter; enthält er Preis/
    Versprechen (VERBOTEN) → Standardsatz statt Sperre."""
    t = tippbar(str(d.get("text") or "")).lower().replace("#", " ")
    t = " ".join(re.sub(r"[^0-9a-zäöüß ,.?-]", " ", t).split()[:8]).strip(" ,.-")
    if t and any(re.search(v, t) for v in VERBOTEN):
        log(f"Beschreibungstext „{t}“ enthält Preis/Versprechen → Standardsatz")
        t = ""
    return t or random.choice(KURZTEXTE)


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
    wort = kurztext(d)                                           # Artur 16.11.2026: kurzer, simpler Text vor den Hashtags
    t = " ".join(([wort] if wort else []) + teile)
    if not pfl:
        t = " ".join(([wort] if wort else []) + [h.lower() for h in eigen[:3]])
    return t + " "


def feld_text(tx):
    """Text im Beschreibungsfeld (links oben auf der Beitragsseite), ohne Platzhalter."""
    feld = " ".join(t[0] for t in tx if t[1] < 230 and 60 < t[2] < 225).lower()
    return re.sub(r"beschreibung hinzufügen\W*", " ", feld).strip()


def feld_ruhig_lesen(max_s=15):
    """15.11.2026 20:32: TikTok arbeitet Eingaben auf der Beitragsseite teils erst Sekunden später ab (Video wird
    verarbeitet) – Text erschien nach der Prüfung, neue Tipps stauten sich (öffnete „Standort“). Darum warten, bis der
    Feldtext in zwei Bildern gleich ist (und nicht leer), höchstens max_s."""
    ende = time.time() + max_s
    alt = None
    while True:
        tx = lesen()
        jetzt = feld_text(tx)
        if jetzt and jetzt == alt:
            return tx
        if time.time() > ende:
            return tx
        alt = jetzt
        time.sleep(1.0)


def beschreibung_feld_tippen(tx):
    b = seh.finde("Beschreibung", tx, ueber=330)
    if b:
        tipp(b[0], b[1], tx, "Beschreibung")
    else:                                                        # 15.11.: Feld hat schon Text (Beitrag fortsetzen)
        alt = muss([t for t in tx if t[1] < 230 and 60 < t[2] < 225], "Beschreibungsfeld nicht gefunden")
        tipp(alt[0][1], alt[0][2], tx, "Beschreibung (vorhandener Text)")
    ruhe(0.7)


def beschreiben(text):
    """Artur 14.11.2026 (Verstoß): IMMER tippen (nie Zwischenablage), vorher Feld leeren. Vor JEDEM Versuch ins Feld
    tippen (15.11. 20:17 WMF: Text kam nicht im Feld an – Feld blieb leer → kein Verstoß, sondern Hänger).
    Fremder/falscher Text nach 3 Versuchen → Sperre; Feld bleibt leer → Stopp (am Beitrag weiter)."""
    muss(warte("Beschreibung", 4, ueber=330) or [t for t in lesen() if t[1] < 230 and 60 < t[2] < 225],
         "Beschreibungsfeld nicht gefunden")
    leer = 0
    for versuch in range(3):
        beschreibung_feld_tippen(lesen())
        K().taste("cmd+a"); ruhe(0.2); K().loeschen(1); K().loeschen(len(text) + 40)
        menschlich(text)
        ruhe(0.6)
        tx = feld_ruhig_lesen()
        if beschreibung_stimmt(text, tx):
            break
        if not feld_text(tx):
            leer += 1
            log("Beschreibungsfeld leer – Text kam nicht an, Feld neu antippen")
        else:
            log("Beschreibung am Bildschirm stimmt nicht – Feld leeren, neu tippen")
    else:
        if leer == 3:
            raise Stopp("Beschreibung kam nicht im Feld an (Feld leer)")
        raise Sperre("Beschreibung am Bildschirm stimmt nicht mit der geplanten überein – NICHT gepostet")
    tastatur_zu()
    log(f"Beschreibung getippt: {text.strip()}")


def _gleich(a, b):
    """OCR-tolerant gleich: exakt, oder ab 5 Zeichen ≥ 80 % ähnlich (15.11.2026: „#livedeals“ als „fivedeals“ gelesen)."""
    import difflib
    a, b = _kn(a), _kn(b)
    return bool(a) and (a == b or (min(len(a), len(b)) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8))


def beschreibung_stimmt(text, tx=None):
    """Artur 15.11.2026: falsche Beschreibung/Hashtags = Verstoß. Getippten Text am Bildschirm lesen: alle geplanten
    Wörter/Hashtags da, nichts Fremdes (kein anderer Hashtag, kein Satz wie „Beklagte Lip Plumper“), kein Preis.
    Vergleich je Wort OCR-tolerant (_gleich), damit Lesefehler einen richtigen Text nicht blockieren."""
    tx = lesen() if tx is None else tx
    feld = feld_text(tx)
    soll = [w.lower() for w in text.split()]
    ist = re.findall(r"[0-9a-zäöüß]+", feld)                     # „#“ trennt nur (OCR liest es mal als f/F/#)
    # 16.11.2026 (HOTU): OCR las „#digitalkamera“ am Zeilenumbruch als „digita kamera“ → 3× gelöscht + Sperre.
    # Daher auch zwei benachbarte OCR-Stücke zusammen vergleichen (nur für „fehlt“, fremde Wörter bleiben streng).
    paare = ist + [a + b for a, b in zip(ist, ist[1:])]
    fehlt = [w for w in soll if _kn(w) and not any(_gleich(w, i) for i in paare) and _kn(w) not in _kn(feld)]
    fremd = [i for i in ist if len(i) >= 2 and not any(_gleich(i, w) or _kn(i) in _kn(w) and len(i) >= 4 for w in soll)
             and not any(i in (a, b) and any(_gleich(a + b, w) and abs(len(a + b) - len(_kn(w))) <= 2 for w in soll)
                         for a, b in zip(ist, ist[1:]))]
    if not all(w.startswith("#") for w in soll):                 # mit Text: ein kurzes Füllwort tolerieren
        fremd = [i for i in fremd if len(i) >= 4]
        fremd = fremd if len(fremd) > 1 else []
    preis = re.search(r"\d+[.,]\d+|€|euro", feld) and not re.search(r"\d+[.,]\d+|€|euro", text.lower())
    if fehlt or fremd or preis:
        log(f"Feld: {feld[:120]!r} | fehlt {fehlt[:3]} | fremd {fremd[:3]} | preis {bool(preis)}")
        return False
    return True


def tastatur_zu():
    tx = lesen()
    for lab in ("Fertig", "OK"):
        f = seh.finde(lab, tx, genau=True, ueber=200)
        if f:
            tipp(f[0], f[1], tx, lab); ruhe(0.8); return


def produkt_passt(block, produkt):
    """Reine Funktion: oberstes Listen-Produkt passt zum Shop-Namen (≥ 1 Wort mit ≥ 4 Zeichen, Umlaute egal – OCR
    „Vitalitat“, Artur 15.11.2026). Nie suchen, nie scrollen – passt es nicht: Sperre."""
    worte = list(dict.fromkeys(re.findall(r"[a-zäöüß0-9]{4,}", produkt.lower())))
    return not worte or any(_kn(w) in _kn(block) for w in worte)


def oberstes_produkt(tx):
    """Reine Funktion: oberstes „Hinzufügen“ in Showcase-/Einkaufswagen-Liste und der Text seines Produkt-Blocks."""
    hin = sorted([t for t in tx if t[0].strip().startswith("Hinzuf") and 180 < t[2] < 700], key=lambda t: t[2])
    if not hin:
        return None, ""
    hy = hin[0][2]
    return hin, " ".join(t[0] for t in tx if hy - 110 <= t[2] <= hy + 10).lower()


def liste_laedt(tx):
    """Reine Funktion: Showcase-/Einkaufswagen-Liste lädt noch („Wird geladen …“ in der Kopfzeile)."""
    return any("wird geladen" in t[0].lower() for t in tx if t[2] < 90)


def verlinken(weg, produkt, kurz=""):
    """Artur 13.11.2026: hakt etwas, am aktuellen Bildschirm weitermachen (nicht neu anfangen).
    Jede Runde: Bildschirm lesen → passenden nächsten Schritt machen. Max. ~60 s."""
    # Artur 14.11.2026: Handschuhe – ein allgemeines Wort reicht nicht (falsches Produkt aus dem Showcase).
    # Treffer = mind. 2 Wörter aus dem echten Shop-Namen (Social1/TikTok-Link), bei nur einem Wort dieses eine.
    def passt(block):
        return produkt_passt(block, produkt)
    oben = oberstes_produkt
    ende = time.time() + 60
    vorher = None                                                # oberster Block im letzten Bild (Liste stabil?)
    while time.time() < ende:
        tx = lesen()
        if seh.finde("verstanden", tx):
            v = seh.finde("verstanden", tx); tipp(v[0], v[1], tx, "Verstanden"); ruhe(0.8)
            if seh.finde("nicht verfügbar", tx) or seh.finde("nicht verfugbar", tx) or seh.finde("nicht vorrätig", tx) \
               or seh.finde("nicht hinzugefügt", tx):
                raise Entwurf("Produkt beim Verlinken nicht vorrätig/verfügbar → Entwurf")
            continue
        if seh.finde("zum Video", tx) or seh.finde("umbenennen", tx) or seh.finde("zustimmen", tx):
            nach_hinzufuegen(weg); return
        wagen_liste = bool(seh.finde("Einkaufswagen", tx, ueber=80) and seh.finde("Produkte suchen", tx))
        showcase_liste = bool(seh.finde("Dein Showcase", tx) or seh.finde("Aus dem Showcase", tx))
        if (weg == "wagen" and wagen_liste) or (weg != "wagen" and showcase_liste):
            hin, block = oben(tx)
            if not hin:
                neu_laden_tippen(tx); time.sleep(0.4); continue
            # Artur 16.11.2026 (Szenario 1, Aufnahme): während oben „Wird geladen …“ steht, zeigt TikTok noch die ALTE
            # Reihenfolge (dort stand Nike oben, eine Sekunde später das neue Produkt). Erst entscheiden, wenn nichts mehr
            # lädt und das oberste Produkt in zwei Bildern gleich ist – sonst könnte ein altes, ähnlich benanntes passen.
            sig = (round(hin[0][2] / 6), block)
            if liste_laedt(tx) or sig != vorher:
                vorher = sig; time.sleep(0.4); continue
            # Artur 14.11.2026: NIE in TikTok nach Produkten suchen – immer über Social1. Das gerade über den
            # Social1-Link hinzugefügte Produkt steht oben; passt es nicht, warten (lädt) und dann STOPP statt suchen.
            ziel = hin[0]
            # Artur 15.11.2026: NIE in der Liste scrollen, NIE suchen. Das gerade über Social1 hinzugefügte Produkt
            # steht oben → oberstes nehmen, wenn mind. 1 Wort des Shop-Namens passt (Umlaute egal); sonst warten/STOPP.
            if not passt(block):
                if time.time() > ende - 30:
                    raise ListeFalsch(f"oberstes Produkt passt nicht zu „{produkt}“ ({block[:60]!r}) – nicht verlinkt")
                time.sleep(0.6); continue
            tipp(ziel[1], ziel[2], tx, "Hinzufügen"); ruhe(0.6)  # 16.11.: war 1,4 s – nach_hinzufuegen wartet selbst
            nach_hinzufuegen(weg); return                        # (tippt in der Liste nichts mehr an)
        quellen = seh.finde("Hinzufügen von", tx) or seh.finde("Gekaufte Produkte", tx) or seh.finde("Kooperationen", tx)
        if weg == "wagen" and quellen and not wagen_liste:       # Blatt „Hinzufügen von“ (Szenario 2, Aufnahme 16.11.):
            e = [t for t in tx if t[2] > 500 and re.fullmatch(r"\W{0,3}\s*einkaufswagen", t[0].strip().lower())]   # OCR „: Einkaufswagen“
            e = (e[0][1], e[0][2]) if e else None                # NUR „Einkaufswagen“ – „Weitere Produkte“ liegt
            if e:                                                # verdeckt darunter, an seiner Stelle „Gekaufte Produkte“
                if not kuerzlich("wagen-liste", 2.5):            # 16.11.: Doppel-Tipp-Schutz statt langer Pause
                    tipp(e[0], e[1], tx, "Einkaufswagen (Liste)", abstand=20); merke("wagen-liste"); ruhe(0.7)
                else:
                    time.sleep(0.3)
            else:
                time.sleep(0.4)
            continue
        if weg == "wagen" and showcase_liste:
            w = seh.finde("Weitere Produkte", tx)
            if w:
                if kuerzlich("weitere", 2.5):
                    time.sleep(0.3); continue
                tipp(w[0], w[1], tx, "Weitere Produkte hinzufügen"); merke("weitere"); ruhe(0.7); continue
        if weg == "wagen":
            e = seh.finde("Einkaufswagen", tx, unter=500)
            if e and not wagen_liste:
                if kuerzlich("wagen-liste", 2.5):
                    time.sleep(0.3); continue
                tipp(e[0], e[1], tx, "Einkaufswagen (Liste)"); merke("wagen-liste"); ruhe(0.7); continue
        pr = seh.finde("Produkt", tx, genau=True, unter=380)
        if pr and not showcase_liste and not wagen_liste:
            if kuerzlich("produkt", 2.5):
                time.sleep(0.3); continue
            tipp(pr[0], pr[1], tx, "Produkt", abstand=30); merke("produkt"); ruhe(0.7); continue
        l = seh.finde("Link hinzufügen", tx)
        if l and not showcase_liste and not wagen_liste:
            if kuerzlich("link", 2.5):
                time.sleep(0.3); continue
            tipp(l[0], l[1], tx, "Link hinzufügen"); merke("link"); ruhe(0.6); continue
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
            if kuerzlich("dialog-hinzu", 2.5):                   # 16.11.: Dialog blendet noch aus → nicht nochmal
                time.sleep(0.3); continue
            tipp(h[0], h[1], tx, "Hinzufügen (Dialog)"); merke("dialog-hinzu"); ruhe(0.7); continue   # war 1,4 s
        lh = limit_hinweis(tx)                                   # 17.11.2026: erst Hinweise lesen, dann warten
        if lh:
            try:
                foto = AUS / f"limit-{time.strftime('%H%M%S')}.png"; seh.kabel().foto(str(foto))
            except Exception:
                foto = None
            log(f"Hinweis am Bildschirm: {bildschirmtext(tx)}")
            raise Limit(f"Tageslimit-Hinweis: „{lh}“")
        if seh.finde("umbenennen", tx):
            r = re.search(r"noch (\d+) von (\d+)", " ".join(t for t, _, _ in tx))
            if r:
                log(f"Pilot: noch {r.group(1)} von {r.group(2)}")
            global _umbenannt
            # 17.11.2026 (148-01 ESN): Shop-Name mit „+“ → „Ungültige Zeichen entfernen“, Hinzufügen bleibt blass →
            # früher nie umbenannt (wartete auf Rot) → Hänger. Jetzt: ungültige Zeichen = Feld geladen → umbenennen.
            if not kraeftig_rot(80, 678) and not (_BUTTON and not _umbenannt and seh.finde("Ungültige", tx)):
                time.sleep(0.4); continue                        # erst blass (lädt), dann kräftig rot
            if _BUTTON and not _umbenannt:                       # Artur 13.11.: Produktname IMMER umbenennen (≤ 20 Zeichen)
                # 15.11. 21:30 (Artur: „Umbenennen hat nicht geklappt, da steht ‚Wen‘“): Tipp direkt auf den Namen,
                # leeren, tippen, warten bis der GANZE Name im Feld steht (TikTok verschluckt bei Verzögerung Zeichen),
                # sonst einmal komplett neu tippen
                lab = seh.finde("Produktname", tx, genau=True)
                lab_y = lab[1] if lab else 307
                alt = feldzeile(tx, lab_y)                       # Name vorher (für die Zähler-Prüfung)
                ok = False
                for runde in range(2):
                    if not feld_leeren(lab_y):                   # 17.11.: nur in ein leeres Feld (0/30) tippen
                        log("Produktname-Feld lässt sich nicht leeren"); continue
                    menschlich(_BUTTON); ruhe(0.3)               # 16.11.: war 0,8 – die Prüfung unten wartet ohnehin,
                    ok = False                                   # bis der GANZE Name im Feld steht (gleiche Gesamtzeit,
                    for _w in range(16):                         # öfter nachgesehen)
                        if name_ok(lesen(), lab_y, alt):
                            ok = True; break
                        time.sleep(0.5)
                    if ok:
                        break
                    log("Produktname unvollständig – nochmal komplett neu")
                _umbenannt = True
                log(f"umbenannt: {_BUTTON}" if ok else "Produktname nicht sauber übernommen – weiter")
                time.sleep(0.4); continue                        # 17.11.: neu lesen → Hinzufügen erst, wenn es rot ist
            if kuerzlich("hinzufuegen-rot", 3.0):               # 16.11.: nie zweimal „Hinzufügen“ in Folge
                time.sleep(0.4); continue
            tipp(167, 678, None, "Hinzufügen (rot)"); merke("hinzufuegen-rot"); ruhe(0.6); continue   # Schutz 3 s oben
        if seh.finde("zustimmen", tx):
            z = seh.finde("zustimmen", tx); tipp(z[0], z[1], tx, "Posten zustimmen"); ruhe(1.2); continue
        if seh.finde("Veröffentlichen", tx, unter=600) or seh.finde("Entwürfe", tx, unter=600):
            log(f"Produkt verlinkt ({weg})"); return
        time.sleep(0.4)
    try:                                                         # 17.11.2026 (148-51): Bild der Hängestelle sichern
        foto = AUS / f"verlinken-haenger-{time.strftime('%H%M%S')}.png"; seh.kabel().foto(str(foto))
        log(f"Hänger beim Verlinken – Foto {foto.name} – Bildschirm: {bildschirmtext(lesen())}")
    except Exception:
        pass
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


def _bis_weg(label, max_s, min_s=0.5):
    """Wartet, bis der Knopf (unten, Text endet auf label) verschwunden ist → True, sonst nach max_s False."""
    time.sleep(min_s)
    ende = time.time() + max(0.0, max_s - min_s)
    for _ in range(int(max_s / 0.3) + 2):
        tx = lesen()
        if not [t for t in tx if label.lower() in t[0].lower() and t[2] > 600]:
            return True
        if time.time() >= ende:
            break
        time.sleep(0.3)
    return False


def abschluss(entwurf):
    tx = lesen()
    if entwurf:
        e = muss(seh.finde("Entwürfe", tx, unter=600), "Knopf „Entwürfe“ fehlt")
        muss(e[0] < 167, "„Entwürfe“ nicht links – Abbruch (Veröffentlichen-Gefahr)")
        tipp(e[0], e[1], tx, "Entwürfe")
        weg = _bis_weg("Veröffentlichen", 3.0, min_s=0.6)        # 16.11.: war feste 2,0 s – Prüfung bleibt gleich
        muss(weg, "Entwurf nicht gespeichert – Beitragsseite noch offen")
        log("ALS ENTWURF GESPEICHERT"); return
    ruhe(0.3, 0.6)                                               # Knopf wird erst nach dem Laden kräftig rot (16.11.: war
    for _ in range(10):                                          # 1,0–1,8 s fest – die Schleife wartet auf kräftig rot)
        tx = lesen()
        z = seh.finde("zustimmen", tx)
        if z:
            tipp(z[0], z[1], tx, "Posten zustimmen"); ruhe(1.2); continue
        kn = [t for t in tx if t[0].strip().endswith("Veröffentlichen") and t[1] > 167 and t[2] > 600]
        v = (kn[0][1], kn[0][2]) if kn else None
        if not v and not seh.finde("Entwürfe", tx, unter=600):
            log("VERÖFFENTLICHT"); return
        muss(v, "„Veröffentlichen“-Knopf rechts unten nicht gefunden")
        if not kraeftig_rot(v[0] + 40, v[1]) and _ < 5:          # 13.11.: nach 3 Versuchen trotzdem tippen (16.11.: 5,
            time.sleep(0.8); continue                            # weil die feste Pause davor kürzer ist – gleiche Zeit)
        tipp(v[0], v[1], tx, "Veröffentlichen")
        _bis_weg("Veröffentlichen", 4.0, min_s=0.8)              # 16.11.: war feste 2,5 s; nochmal getippt wird erst,
                                                                 # wenn der Knopf nach 4 s noch da ist (vorher 2,5 s)
    raise Stopp("Beitragsseite noch offen – nicht veröffentlicht?")


# ---------------------------------------------------------------- 6) Aufräumen

def social1_abhaken(pid, liste_id=None, _runde=0):
    """Mac-Safari (Artur eingeloggt): auf der Social1-Liste die Karte des Produkts → Lesezeichen → Liste abhaken → Done.
    Nie „Delete“ (löscht die ganze Liste). Ohne offene Liste im Mac-Safari: Hinweis, kein Stopp.
    16.11.2026 (Tempo): kein Neuladen nach jedem Abhaken mehr. Abgehakte Karten bekommen eine Markierung (data-ts-ab)
    und werden beim nächsten Mal übersprungen (2. Vorbild-Video desselben Produkts). Ist der Haken der gefundenen Karte
    schon raus (Seite veraltet), wird die Liste neu geladen und einmal wiederholt – nie wird „abgehakt“ gemeldet, ohne
    dass ein gesetzter Haken entfernt wurde."""
    js = r"""(()=>{const u=location.href; const m=u.match(/saved-videos\/([0-9a-f]+)/); if(!m) return 'keine-liste';
const lid=m[1]; document.querySelectorAll('[data-ts-aktiv]').forEach(k=>delete k.dataset.tsAktiv);
const k=[...document.querySelectorAll('[data-slot=card]')].find(k=>{const p=k.querySelector('img[src*="/products/"]');return !k.dataset.tsAb&&p&&p.src.includes('PID')});
if(!k) return 'nicht-in-liste'; k.dataset.tsAktiv='1'; k.querySelector('button[title="Save to list"]').click(); return 'auf:'+lid})()""".replace("PID", pid)
    liste_id = liste_id or SOCIAL1_LISTE
    r = _safari(js, liste_id)
    if r == "keine-liste":                                       # 16.11.2026: Liste nicht offen → öffnen, nochmal
        _liste_oeffnen(liste_id); r = _safari(js, liste_id)
    if r == "nicht-in-liste" and _runde == 0:                    # Seite älter als die Liste → einmal neu laden
        _liste_oeffnen(liste_id); return social1_abhaken(pid, liste_id, 1)
    if not r.startswith("auf:"):
        return r
    lid = r[4:]
    js2 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'kein-dialog';
const c=d.querySelector('button[role=checkbox][id="LID"]'); if(!c) return 'keine-checkbox';
if(c.getAttribute('aria-checked')=='true'){c.click(); return 'ok'}
const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='Close'); if(b) b.click(); return 'schon-raus'})()""".replace("LID", lid)
    r2 = "kein-dialog"
    for _ in range(8):                                           # 16.11.: Dialog abwarten statt fester 1,2 s
        time.sleep(0.3)
        r2 = _safari(js2, liste_id)
        if r2 not in ("kein-dialog", "keine-checkbox"):          # Listen im Dialog laden evtl. noch
            break
    if r2 == "schon-raus":                                       # veraltete Karte (schon abgehakt) → neu laden, nochmal
        _safari("(()=>{const k=document.querySelector('[data-ts-aktiv]'); if(k){k.dataset.tsAb='1'} return 'ok'})()", liste_id)
        if _runde == 0:
            _liste_oeffnen(liste_id); return social1_abhaken(pid, liste_id, 1)
        return "schon-raus"
    js3 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'zu';
const c=d.querySelector('button[role=checkbox][id="LID"]'); const ok=c&&c.getAttribute('aria-checked')=='false';
if(!ok) return 'warte';
const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='Done'); if(b) b.click();
const k=document.querySelector('[data-ts-aktiv]'); if(k){k.dataset.tsAb='1'; delete k.dataset.tsAktiv}
return 'abgehakt'})()""".replace("LID", lid)
    js3_zu = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'zu';
const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='Close'); if(b) b.click(); return 'nicht-abgehakt'})()"""
    if r2 != "ok":
        if r2 == "keine-checkbox":
            _safari(js3_zu, liste_id)                            # Dialog nicht offen stehen lassen
        return r2
    r3 = "warte"
    for _ in range(8):                                           # 16.11.: Haken-Wechsel abwarten statt fester 0,8 s
        time.sleep(0.25)
        r3 = _safari(js3, liste_id)
        if r3 != "warte":
            break
    if r3 == "warte":
        r3 = _safari(js3_zu, liste_id)
    return r3


_S1_FADEN = None


def aufraeumen_im_hintergrund(d):
    """16.11.2026 (Tempo): Social1-Abhaken läuft am Mac (Safari) – das iPhone muss darauf nicht warten (~3–6 s je Video).
    Immer nur ein Abhaken gleichzeitig (vorheriges wird erst abgewartet); am Lauf-Ende wartet main() auf das letzte."""
    import threading
    global _S1_FADEN
    social1_warten()

    def los():
        try:
            aufraeumen(d, fotos=False)
        except Exception as e:
            log(f"Social1 ging nicht: {e}")
    _S1_FADEN = threading.Thread(target=los, name="social1")
    _S1_FADEN.start()


def social1_warten():
    if _S1_FADEN is not None and _S1_FADEN.is_alive():
        _S1_FADEN.join(60)


NV_LISTE = "nicht verfügbar"   # Artur 16.11.2026: eigene Social1-Liste für ausverkaufte/nicht provisionsberechtigte Produkte


def social1_verschieben(pid, liste_id=None, ziel=NV_LISTE):
    """Vorbild-Video des Produkts aus der ausgewählten Liste in die Liste „nicht verfügbar“ verschieben (Lesezeichen →
    Haken bei „nicht verfügbar“ setzen, fehlt die Liste: „Create new list“ → Haken der Arbeitsliste raus → Done)."""
    liste_id = liste_id or SOCIAL1_LISTE
    js = r"""(()=>{const k=[...document.querySelectorAll('[data-slot=card]')].find(k=>{const p=k.querySelector('img[src*="/products/"]');return p&&p.src.includes('PID')});
if(!k) return 'nicht-in-liste'; k.querySelector('button[title="Save to list"]').click(); return 'auf'})()""".replace("PID", pid)
    r = _safari(js, liste_id)
    if r == "keine-liste":
        _liste_oeffnen(liste_id); r = _safari(js, liste_id)
    if r != "auf":
        return r
    time.sleep(1.2)
    such = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]'); if(!d) return 'kein-dialog';
const c=[...d.querySelectorAll('button[role=checkbox]')].find(c=>c.nextElementSibling&&c.nextElementSibling.innerText.trim()=='ZIEL');
if(!c) return 'fehlt'; if(c.getAttribute('aria-checked')!='true') c.click(); return 'ok'})()""".replace("ZIEL", ziel)
    r = _safari(such, liste_id)
    if r == "fehlt":                                             # Liste anlegen (React-Feld per nativem Setter)
        _safari(r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]');[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='Create new list').click();return 'ok'})()""", liste_id)
        time.sleep(0.8)
        _safari(r"""(()=>{const i=document.querySelector('[data-slot=dialog-content] input[placeholder="Enter list name..."]');
Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'ZIEL');i.dispatchEvent(new Event('input',{bubbles:true}));return 'ok'})()""".replace("ZIEL", ziel), liste_id)
        time.sleep(0.6)
        _safari(r"""(()=>{const b=[...document.querySelectorAll('[data-slot=dialog-content] button[type=submit]')].find(b=>b.innerText.trim()=='Create');if(b&&!b.disabled)b.click();return 'ok'})()""", liste_id)
        time.sleep(2.0)
        r = _safari(such, liste_id)                              # neue Liste ist meist schon angehakt
    if r != "ok":
        return f"verschieben: {r}"
    time.sleep(0.6)
    js3 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]');const c=d.querySelector('button[role=checkbox][id="LID"]');
if(c&&c.getAttribute('aria-checked')=='true') c.click(); return 'ok'})()""".replace("LID", liste_id)
    _safari(js3, liste_id); time.sleep(0.8)
    js4 = r"""(()=>{const d=document.querySelector('[data-slot=dialog-content]');const c=d.querySelector('button[role=checkbox][id="LID"]');
const n=[...d.querySelectorAll('button[role=checkbox]')].find(c=>c.nextElementSibling&&c.nextElementSibling.innerText.trim()=='ZIEL');
const ok=(!c||c.getAttribute('aria-checked')=='false')&&n&&n.getAttribute('aria-checked')=='true';
const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==(ok?'Done':'Close')); if(b) b.click(); return ok?'nach „ZIEL“ verschoben':'nicht-verschoben'})()""".replace("LID", liste_id).replace("ZIEL", ziel)
    r = _safari(js4, liste_id)
    _liste_oeffnen(liste_id)
    return r


def _liste_oeffnen(liste_id):
    """Social1-Liste im Mac-Safari öffnen/neu laden (Tab mit social1 per „set URL“, sonst neues Fenster), bis Karten da."""
    url = f"https://www.social1.ai/saved-videos/{liste_id}"
    subprocess.run(["osascript", "-e", 'tell application "Safari"\nrepeat with d in documents\n'
                    'if URL of d contains "social1.ai/saved-videos" then\nset URL of d to "' + url + '"\nreturn\nend if\n'
                    'end repeat\nmake new document with properties {URL:"' + url + '"}\nend tell'], capture_output=True, text=True)
    for _ in range(30):
        time.sleep(0.5)
        n = _safari("String(document.querySelectorAll('[data-slot=card]').length)", liste_id)
        if n.isdigit() and int(n) > 0:
            time.sleep(1.0); return


def liste_fuer(d):
    """Artur 16.11.2026: abhaken in der Social1-Liste, die beim Schneiden ausgewählt war (nicht fest bof 2.0).
    Reihenfolge: `social1_liste` aus der Eingang-JSON → neueste ausgang/social1-*.json mit diesem Produkt → SOCIAL1_LISTE."""
    if d.get("social1_liste"):
        return d["social1_liste"]
    m = re.search(r"saved-videos/([0-9a-f]{24})", d.get("social1_link", ""))
    if m:
        return m.group(1)
    pid = d.get("tts_link", "").rstrip("/").split("/")[-1]
    beste = None
    for f in AUS.glob("social1-*.json"):
        try:
            j = json.loads(f.read_text())
        except Exception:
            continue
        if any(e.get("produkt_id") == pid for e in j.get("eintraege", [])):
            m = re.search(r"saved-videos/([0-9a-f]{24})", j.get("url", ""))
            if m and (beste is None or str(j.get("gelesen", "")) > beste[0]):
                beste = (str(j.get("gelesen", "")), m.group(1))
    return beste[1] if beste else SOCIAL1_LISTE


SOCIAL1_LISTE = os.environ.get("TS_SOCIAL1_LISTE", "6af5c87e84c1d2f55b052550")   # Artur 15.11.2026: die richtige Liste


def _safari(js, liste_id=None):
    esc = js.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    r = subprocess.run(["osascript", "-e", 'tell application "Safari"\nrepeat with d in documents\n'
                        'if URL of d contains "social1.ai/saved-videos/' + (liste_id or SOCIAL1_LISTE) + '" then return do JavaScript "' + esc + '" in d\n'
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
    log(f"Social1: {social1_abhaken(pid, liste_fuer(d))}")
    if fotos:
        fotos_aufraeumen([d])


def _ziel(v):
    """(kachel, dauer_s) aus Eingang-Dict oder Kachel-Text."""
    if isinstance(v, dict):
        try:
            return v["kachel"], dauer_text(EIN / v["datei"])
        except Exception:
            return v["kachel"], None
    return v, None


def album_treffer(tx, ziele):
    """Reine Funktion (offline getestet): Kacheln im Fotos-Raster, deren Hook-Text UND Länge zu einem gesendeten Video
    passen → [(x, y, kachel)]. Hook steht im Vorschaubild (oben in der Kachel), Länge unten rechts."""
    raus = []
    for t, dx, dy in [(B.dauer_text(u[0]), u[1], u[2]) for u in tx if 120 < u[2] < 735 and B.dauer_text(u[0])]:
        try:
            sek = _sek(t)
        except ValueError:
            continue
        for k, soll in ziele:
            if soll is not None and abs(sek - soll) > 1.1:
                continue
            hook = [u for u in tx if abs(u[1] - (dx - 40)) < 52 and 20 < dy - u[2] < 125 and _passt(k, u[0])]
            if hook:
                raus.append((dx - 40, dy - 50, k)); break
    return raus


def _ausgewaehlt(tx):
    alles = " ".join(t.lower() for t, _, _ in tx)
    m = re.search(r"(\d+)\s+(videos?|objekte?|fotos?|elemente?)\s+ausgew", alles) \
        or re.search(r"auswahl\s*\((\d+)\)", alles)                # 17.11.: iOS neu „Auswahl (N) anzeigen“
    if m:
        return int(m.group(1))
    # Auswahlmodus, nichts gewählt: „Objekte auswählen“ als EIN Text unten (nicht „237 Objekte“ + „Auswählen“ oben)
    return 0 if any(re.fullmatch(r"\W*objekte\s+ausw[aä]hlen\W*", t.strip().lower()) and y > 600 for t, _, y in tx) else None


def fotos_sammel_loeschen(videos):
    """Artur 17.11.2026 (Bildschirmaufnahme 14:42, ersetzt den Ablauf vom 15.11.): Fotos → Album „Zuletzt gesichert“ →
    oben RECHTS „Auswählen“ (oben links steht dann „Alle“ – NIE antippen) → jede Video-Kachel des Stapels (Hook + Länge)
    genau EINMAL antippen → Papierkorb unten rechts → „N Videos löschen“, nur wenn N = Zähler am iPhone = selbst angetippt.
    Nichts zwischen letztem Haken und Papierkorb. Gescrollt wird NUR außerhalb des Auswahlmodus (ein Wisch im Auswahlmodus
    hakt Kacheln an/ab – daher das „an und wieder aus“). Pro Bildschirm ein Durchgang; 3 Bildschirme ohne Treffer → fertig.
    Gelöschtes bleibt 30 Tage in „Zuletzt gelöscht“. → Anzahl gelöscht."""
    ziele = [_ziel(v) for v in videos]
    app("Fotos")
    for _ in range(8):                                           # → Album „Zuletzt gesichert“
        z, tx, _t = lage()
        if seh.finde("Zuletzt gesichert", tx, ueber=140) and (z == B.FOTOS_ALBUM or seh.finde("Objekte", tx, ueber=160)):
            break
        if z == B.FOTOS_VOLLBILD:
            zz = seh.finde("<", tx, ueber=80)
            tipp(zz[0], zz[1], tx, "Zurück") if zz else tipp(30, 57, tx, "Zurück"); ruhe(1.0); continue
        zg = seh.finde("Zuletzt", tx, unter=300, ueber=650)
        if zg and seh.finde("gesichert", tx, unter=300, ueber=650):
            tipp(zg[0], zg[1], tx, "Zuletzt gesichert"); ruhe(1.5); continue
        sm = seh.finde("Sammlungen", tx, unter=650)
        if sm:
            tipp(sm[0], sm[1], tx, "Sammlungen"); ruhe(1.2); continue
        tipp(30, 57, tx, "Zurück"); ruhe(1.0)                    # (Sperre greift, falls dort „Alle“ steht)
    else:
        raise Stopp("Fotos: „Zuletzt gesichert“ nicht erreicht")
    geloescht, leer = 0, 0
    for runde in range(12):
        tx = lesen()
        if _ausgewaehlt(tx) is not None:                         # noch im Auswahlmodus → erst raus (X oben rechts)
            if (_ausgewaehlt(tx) or 0) > 0:
                tippe_text(tx, "Auswahl aufheben"); ruhe(0.8); tx = lesen()
            tipp(298, 57, tx, "X (Auswahl beenden)"); ruhe(1.0); tx = lesen()
        treffer = album_treffer(tx, ziele)
        if not treffer:
            leer += 1
            if leer >= 3:
                break
            K().ziehe(167, 250, 167, 560, 0.4); ruhe(1.0)       # außerhalb des Auswahlmodus: normal hochscrollen
            continue
        leer = 0
        a = seh.finde("Auswählen", tx, genau=True, ueber=100) or seh.finde("Auswahlen", tx, genau=True, ueber=100)
        muss(a and a[0] > 167, "Fotos: „Auswählen“ oben rechts fehlt")
        tipp(a[0], a[1], tx, "Auswählen (oben rechts)"); ruhe(1.0)
        tx = lesen()
        muss(_ausgewaehlt(tx) == 0, "Fotos: Auswahlmodus nicht leer – nicht weiter")
        treffer = album_treffer(tx, ziele)                       # Lage im Auswahlmodus frisch (Kacheln stehen gleich)
        for x, y, k in treffer:                                  # jede Kachel genau EINMAL, keine Kontroll-Tipps
            tipp(x, y, None, f"Kachel {k}"); ruhe(0.35)
        tx = lesen(); n = _ausgewaehlt(tx)
        if n != len(treffer):
            tippe_text(tx, "Auswahl aufheben")
            raise Stopp(f"Fotos: {n} ausgewählt, {len(treffer)} angetippt – Auswahl aufgehoben, nichts gelöscht")
        tipp(290, 686, None, "Papierkorb (unten rechts)"); ruhe(1.0)
        tx = lesen()
        d = [t for t in tx if re.search(r"(\d+)\s+(videos?|objekte?|elemente?)\s+löschen", t[0].lower())]
        if not d:
            raise Stopp("Fotos: Lösch-Dialog nicht gesehen (Auswahl bleibt)")
        m = int(re.search(r"(\d+)", d[0][0]).group(1))
        if m != n:
            tippe_text(tx, "Abbrechen", genau=True)
            raise Stopp(f"Fotos: Dialog nennt {m}, ausgewählt {n} – abgebrochen")
        tipp(d[0][1], d[0][2], tx, d[0][0]); ruhe(1.5)
        geloescht += m
        log(f"Fotos: {m} Videos gelöscht (Zuletzt gesichert)")
    return geloescht


def fotos_aufraeumen(videos):
    """Artur 17.11.2026: nur noch Sammel-Löschen in „Zuletzt gesichert“ (nicht einzeln – das Einzel-Löschen über die
    Mediathek passt nicht mehr zum neuen iOS). Klappt es nicht: Hinweis, Steuer-Chat prüft."""
    try:
        log(f"Fotos aufgeräumt: {fotos_sammel_loeschen(videos)} gelöscht")
    except Stopp as e:
        log(f"Hinweis Fotos (Sammel-Löschen): {e}")


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

BEITRAG_SEITEN = (B.BEITRAG, B.SHOWCASE_LISTE, B.WAGEN_LISTE, B.LINK_BLATT, B.UMBENENNEN, B.DLG_ZUM_VIDEO,
                  B.DLG_VERSTANDEN, B.DLG_ZUSTIMMEN, B.DLG_OK, B.LADEN, B.LADEFEHLER)
ERSTELLEN_SEITEN = (B.KAMERA, B.GALERIE, B.VORSCHAU, B.EDITOR)


def fortsetzen_planen(F, fehler):
    """Nach einem Hänger: Bildschirm lesen und entscheiden, wo es weitergeht (Artur 13./15.11.2026: am aktuellen
    Bildschirm weitermachen, nie von vorn, keine Ketten-Fehler). Reine Entscheidung über F (Fortschritt) + Bildschirm."""
    z, tx, tabs = lage()
    plan = naechster_schritt(F, z, tabs)
    log(f"Hänger („{fehler}“) – Bildschirm „{z}“ → {plan}")
    if plan == "hauptseite":
        zur_hauptseite(abbrechen=True)
    elif z in (B.DLG_OK, B.DLG_ERLAUBEN, B.LADEFEHLER, B.LADEN, B.OFFLINE):
        dialog_wegmachen(z, tx)                                  # kleine Popups weg, dann am Schritt weiter
    return plan


def naechster_schritt(F, z, tabs=False):
    """Reine Funktion (offline getestet): Fortschritt F + Bildschirm z → Plan. Setzt verlorene Schritte in F zurück.
    Pläne: „weiter“ (am Bildschirm fortsetzen), „hauptseite“ (erst zur Hauptseite, dann fehlende Schritte)."""
    if F["beitrag"] and z in BEITRAG_SEITEN:
        return "weiter"                                          # Beschreibung/Link/Veröffentlichen am Beitrag fortsetzen
    if not F["beitrag"] and F["produkt"] and z in ERSTELLEN_SEITEN:
        return "weiter"                                          # Kamera/Galerie/Editor → zum_beitrag macht dort weiter
    if F["produkt"] == "erstellen" and F.get("erstellen_offen"):
        if z in (B.UMBENENNEN, B.BEWERBEN, B.WERBE_BLATT, B.PRODUKTSEITE, B.VARIANTEN, B.KAMERA, B.SHOWCASE_SEITE):
            return "weiter"                                      # „Jetzt erstellen“-Weg mittendrin
        F["produkt"] = None; F["erstellen_offen"] = False        # Weg verloren → Produkt neu über Social1
    if not F["produkt"] and z in (B.PRODUKTSEITE, B.WERBE_BLATT, B.VARIANTEN, B.SAFARI_SOCIAL1, B.DLG_OEFFNEN):
        return "weiter"                                          # Produkt-Schritt wird ohnehin neu über Social1 geöffnet
    if F["beitrag"]:                                             # Beitrag ist weg (verworfen/abgestürzt) → neu ab „+“
        F.update(beitrag=False, cover=False, text=False, link=False)
        if F["produkt"] == "erstellen":                          # Link hing am „Jetzt erstellen“-Weg → der ist mit weg
            F["produkt"] = None
    if F["produkt"] == "erstellen" and not F["beitrag"] and not F.get("erstellen_offen"):
        F["produkt"] = None
    return "hauptseite"


def schluss_pruefung(d, F, text):
    """Vor JEDEM Veröffentlichen/Entwurf (Artur 15.11.2026, Verstoß-Schutz): Cover-Hook + Beschreibung nochmal am
    Bildschirm lesen – auch nach Wiederaufnahmen. Passt etwas nicht → Sperre (nicht posten)."""
    cover_pruefen(d["kachel"])
    if not beschreibung_stimmt(text):
        raise Sperre("Schluss-Prüfung: Beschreibung am Bildschirm passt nicht – NICHT gepostet")
    if F["produkt"] == "erstellen" and not produkt_am_beitrag(produkt=d.get("produkt", "")):
        raise Stopp(f"Produkt „{_BUTTON}“ (noch) nicht am Beitrag zu sehen")   # 15.11.: lädt verzögert → am Beitrag weiter


def produkt_am_beitrag(max_s=12, produkt=""):
    """Verlinktes Produkt (umbenannt = _BUTTON) unter „Link hinzufügen“ sichtbar? TikTok zeigt es teils erst Sekunden
    später (15.11.2026 20:36 WMF). OCR-tolerant („Geringer Bestand X“ mit Entfernen-Kreuz)."""
    ende = time.time() + max_s
    while True:
        tx = lesen()
        chips = [t for t in tx if 300 < t[2] < 440 and re.search(r"[x×]\s*$", t[0].strip(), re.I)]   # Produkt-Chip „… X“
        if any(_gleich(re.sub(r"\s*[x×]$", "", t[0].strip(), flags=re.I), _BUTTON) or _kn(_BUTTON) in _kn(t[0])
               for t in tx if t[2] > 300):
            return True
        if produkt and any(produkt_passt(t[0].lower(), produkt) for t in chips):
            log(f"Hinweis: richtiges Produkt verlinkt, aber nicht umbenannt ({chips[0][0]!r})")   # Link stimmt
            return True
        if time.time() > ende:
            return False
        time.sleep(1.0)


def nicht_vorraetig(tx):
    """Produktseite sagt: nicht vorrätig / ausverkauft / nicht verfügbar → kein Showcase, kein Wagen, kein Link."""
    t = " ".join(x[0].lower() for x in tx)
    return any(w in t for w in ("nicht vorrätig", "nicht vorratig", "ausverkauft", "artikel nicht verfügbar",
                                "produkt nicht verfügbar", "nicht mehr verfügbar"))


def badge_scrollen():
    """Artur 15.11.2026 21:20: „in der Regel musst du komplett runterscrollen und hochscrollen innerhalb der
    Produktkarte“ → bis 5× nach unten (Finger hoch), dann bis 6× nach oben (Finger runter, Mitte der Karte);
    nach jedem Wisch prüfen, ob „pro Verkauf“ / „Mehr erkunden“ steht. → letzter Bildschirm."""
    log("kein „pro Verkauf“-Badge → Produktkarte ganz runter- und wieder hochscrollen")
    tx = lesen()
    for richtung, (y1, y2), n in (("runter", (620, 260), 5), ("hoch", (300, 600), 6)):
        alt = None
        for _ in range(n):
            K().ziehe(167, y1, 167, y2, 0.35); ruhe(0.9)
            tx = lesen()
            if seh.finde("pro Verkau", tx) or seh.finde("Mehr erkunden", tx) or nicht_vorraetig(tx):
                return tx
            if B.erkenne(tx) != B.PRODUKTSEITE:
                return tx                                        # Karte zu/anderer Bildschirm → Aufrufer entscheidet
            sig = " ".join(t[0] for t in tx)
            if sig == alt:
                break                                            # Ende erreicht
            alt = sig
    return tx


def warenkorb_leeren():
    """Artur 15.11.2026 20:44 (ersetzt „Jetzt erstellen“): geht Showcase/Einkaufswagen nicht → GESAMTEN Einkaufswagen
    leeren, danach das Produkt neu in den Einkaufswagen (steht dann oben). Getestet 15.11. 20:45:
    Startseite → oben „Shop“ → Einkaufswagen-Symbol oben rechts (309,57) → Bearbeiten-Symbol (280,57) →
    „Alle auswählen“ → „Entfernen“ → Dialog „Artikel aus dem Einkaufswagen entfernen?“ → „Löschen“ → „ist leer“."""
    zur_hauptseite(abbrechen=True)
    for _ in range(4):                                           # Startseite-Reiter (Feed mit „Shop“ oben)
        tx = lesen()
        sh = seh.finde("Shop", tx, genau=True, ueber=90)
        if sh and sh[0] > 120:
            break
        tipp(34, 681, tx, "Startseite"); ruhe(1.5)
    else:
        raise Stopp("Einkaufswagen leeren: „Shop“ oben nicht gefunden")
    tipp(sh[0], sh[1], tx, "Shop"); ruhe(2.5)
    tipp(309, 57, None, "Einkaufswagen-Symbol", abstand=20); ruhe(2.5)
    tx = lesen()
    muss(seh.finde("Einkaufswagen", tx, ueber=80), "Einkaufswagen-Seite nicht offen")
    if not seh.finde("ist leer", tx):
        tipp(280, 57, tx, "Einkaufswagen bearbeiten", abstand=20); ruhe(1.8)
        a = muss(warte("Alle auswählen", 4), "„Alle auswählen“ fehlt")
        tipp(a[0] - 50, a[1], a[2], "Alle auswählen"); ruhe(1.2)
        e = muss(seh.finde("Entfernen", lesen(), unter=640), "„Entfernen“ fehlt")
        tipp(e[0], e[1], None, "Entfernen"); ruhe(1.5)
        l = muss(warte("Löschen", 4, genau=True), "Dialog „Löschen“ fehlt")
        muss(seh.finde("entfernen?", l[2]), "Dialog ist nicht „… aus dem Einkaufswagen entfernen?“")
        tipp(l[0], l[1], l[2], "Löschen"); ruhe(2.5)
        muss(warte("ist leer", 6), "Einkaufswagen nach dem Löschen nicht leer")
    log("Einkaufswagen geleert")
    tipp(17, 58, None, "Zurück (Einkaufswagen)", abstand=20); ruhe(1.5)


def _ablauf(d, F, pid):
    """Ein Video Schritt für Schritt; erledigte Schritte (F) werden übersprungen → Wiederaufnahme am aktuellen Schritt."""
    global _konto, _NEUKUNDE
    if not F["konto"]:
        if _konto != d["account"]:
            konto(d["account"]); _konto = d["account"]
        F["konto"] = True
    if not F["produkt"]:
        if F["ohne_link"]:
            F["produkt"] = "ohne"
        else:
            _NEUKUNDE = False
            tx = zum_produkt(pid, d["produkt"]); log("Produktseite")
            for runde in range(1):                               # 15.11.: „pro Verkauf“ lädt verzögert → warten, und
                for i in range(12):                              # Artur 15.11.2026: „wenn kein Badge erscheint, musst du
                    if B.erkenne(tx) in (B.DLG_ANFORDERN, B.DLG_SCHLIESSEN, B.DLG_OK, B.DLG_ERLAUBEN, B.DLG_OEFFNEN, B.LADEFEHLER):
                        dialog_wegmachen(B.erkenne(tx), tx); tx = lesen(); continue   # Popup weg, nicht neu laden
                    if nicht_vorraetig(tx):                      # Artur 21:33: „Artikel ist nicht vorrätig“ ZUERST lesen →
                        raise Entwurf("Artikel nicht vorrätig → nur Video ohne Produkt als Entwurf")   # nichts geht
                    if seh.finde("nicht provisionsberechtigt", tx):  # Artur 12.11.2026 (Galaxy Buds) + 16.11. (House of
                        raise Entwurf("Produkt nicht provisionsberechtigt → nur als Entwurf ohne Link")   # Thêom): Entwurf
                    if seh.finde("pro Verkau", tx) or seh.finde("Mehr erkunden", tx):   # hochswipen“ → nach ~3 s hoch;
                        break                                    # „wenn kein Badge da ist, einfach nochmal über Social1
                    # Artur 16.11.2026 21:50: KEIN Scrollen mehr (badge_scrollen raus) – fehlt das Badge, einfach
                    # nochmal über Social1 öffnen, bis es angezeigt wird (bis 10×)
                    time.sleep(0.5); tx = lesen()
                else:
                    # Artur 16.11.2026 22:05: „damit wir keine Zeit verlieren: wenn das Badge nicht angezeigt wird,
                    # packs einfach in den Einkaufswagen“ → kein Neu-Öffnen, direkt Einkaufswagen-Weg
                    log("kein „pro Verkauf“-Badge → direkt in den Einkaufswagen")
                    F["nur_wagen"] = True
                break
            # Artur 15.11.2026 20:15 – DREI Wege: (1) „Zum Showcase hinzufügen“ → Produkt aus dem Showcase,
            # (2) schon im Showcase → Einkaufswagen → Produkt aus dem Einkaufswagen, (3) geht beides nicht (Neukunden-
            # Angebot, oberstes Listen-Produkt passt nicht) → „Jetzt erstellen“ → Video
            if F.get("nur_erstellen") or d.get("weg") == "erstellen":   # Weg 4 / Test-Schalter (Artur 16.11.2026:
                weg = "erstellen"                                # „stell dir vor, der Neukunden-Hinweis wär gekommen“)
            elif F.get("nur_wagen"):                             # nach dem Leeren: direkt in den Einkaufswagen
                in_wagen(tx); weg = "wagen"
            else:
                weg = "wagen" if d.get("weg") == "wagen" else showcase_oder_wagen(tx)
            if weg == "ausverkauft":
                F["ohne_link"] = True; weg = "ohne"
            elif weg == "wagen" and _NEUKUNDE:                   # Artur 15.11. 21:08: Neukunden-Hinweis → Einkaufswagen
                log("Neukunden-Hinweis – Einkaufswagen geht nicht → direkt „Jetzt erstellen“ (Video-Methode)")
                weg = "erstellen"                                # geht nicht → DIREKT „Jetzt erstellen“ (nicht leeren)
            if weg == "erstellen":
                F["erstellen_offen"] = True
            F["produkt"] = weg
    if not F["beitrag"]:
        if F["produkt"] == "erstellen":
            if F.get("erstellen_offen"):
                erstellen_route(); F["erstellen_offen"] = False
            zum_beitrag(d["kachel"], galerie=(264, 583))
        else:
            z, _tx, _tabs = lage()
            if z not in ERSTELLEN_SEITEN:                        # offene Produktseite/Blätter/alter Beitrag → erst Hauptseite
                zur_hauptseite(abbrechen=True)
            zum_beitrag(d["kachel"])
        F["beitrag"] = True; log("Beitragsseite")
    if not F["cover"]:
        cover_pruefen(d["kachel"]); F["cover"] = True
    text = beschreibung_text(d) if not F.get("text_soll") else F["text_soll"]
    F["text_soll"] = text
    if not F["text"]:
        pruefe_verboten(text, "Beschreibung", d.get("brand", ""))
        beschreiben(text); F["text"] = True
    if not F["link"]:
        if F["produkt"] in ("showcase", "wagen"):
            verlinken(F["produkt"], d["produkt"], produktname(d, kurz=False))
        F["link"] = True
    schluss_pruefung(d, F, text)


def zurueck_zum_beitrag():
    """Nach „nicht verfügbar“ beim Verlinken: zurück auf die Beitragsseite (nie oben links im Feed)."""
    for _ in range(8):
        z, tx, _t = lage()
        if z == B.BEITRAG:
            return
        if dialog_wegmachen(z, tx, abbrechen=True):
            continue
        if z in (B.SHOWCASE_LISTE, B.WAGEN_LISTE, B.UMBENENNEN):
            tipp(18, 57, tx, "Zurück", abstand=20); ruhe(1.2)
        elif z == B.LINK_BLATT:
            titel = [t for t in tx if t[0].strip() == "Link hinzufügen" and t[2] > 450]
            tipp(315, titel[0][2], tx, "Link-Blatt zu (X)", abstand=25) if titel else blatt_runter(560)
            ruhe(1.0)
        else:
            raise Stopp(f"nicht zurück auf der Beitragsseite („{z}“)")
    raise Stopp("nicht zurück auf der Beitragsseite")


MAX_WIEDERAUFNAHMEN = 6


def ein_video(p, d, entwurf=False, aufr=True):
    global _BUTTON, _umbenannt, _LETZTE_KACHEL
    # Artur 15.11.2026: Produktname wie üblich („Wenige verfügbar“ …, Liste ACCOUNTS.md), aber NIE ein Preis darin
    _BUTTON, _umbenannt = ((d.get("button") or "").strip()[:20].strip() or produktname(d)), False
    if re.search(r"\d|€|euro|cent|gratis|kostenlos", _BUTTON.lower()):
        raise Sperre(f"Produktname „{_BUTTON}“ enthält Preis/Zahl – nicht gepostet")
    start = time.time()
    datei = EIN / d["datei"]
    if not entwurf:
        r = subprocess.run(["zsh", str(HIER / "gepostet.sh"), "pruefen", str(datei)], capture_output=True, text=True)
        if r.returncode:
            raise Hart(f"Doppel-Schutz: {r.stdout.strip()}")
        lim = PILOT.get(d["account"])
        if lim and heute_gepostet(d["account"]) >= lim:
            raise Hart(f"{d['account']}: Tageslimit {lim} erreicht")
    pid = muss(d.get("tts_link", "").rstrip("/").split("/")[-1], "keine Produkt-ID (tts_link)")
    F = {"konto": False, "produkt": None, "beitrag": False, "cover": False, "text": False, "link": False,
         "ohne_link": bool(d.get("ausverkauft")), "erstellen_offen": False}
    neustarts = 0
    for versuch in range(MAX_WIEDERAUFNAHMEN + 1):
        try:
            verbindung_merken()
            _ablauf(d, F, pid)
            verbindung_merken(False)
            break
        except (Sperre, Hart):
            verbindung_merken(False)
            raise
        except (ListeFalsch, WagenLeeren) as e:                  # Artur 15.11. 21:10: „wenn weder Showcase noch
            if F.get("nur_erstellen"):                           # Einkaufswagen gehen, dann Jetzt erstellen“
                raise Sperre(f"{e} – auch über „Jetzt erstellen“ nicht, nicht verlinkt")
            verbindung_merken(False)
            log(f"{e} → Showcase/Einkaufswagen gehen nicht → „Jetzt erstellen“ (Video-Methode)")
            zur_hauptseite(abbrechen=True)
            F.update(produkt=None, beitrag=False, cover=False, text=False, link=False, nur_erstellen=True)
        except Entwurf as e:                                     # Artur 13.11.: nicht verfügbar → Entwurf ohne Link
            verbindung_merken(False)
            log(f"{e} – weiter als Entwurf ohne Link")
            F["ohne_link"] = True
            if F["beitrag"] and not F["link"]:
                zurueck_zum_beitrag(); F["link"] = True
            F["produkt"] = F["produkt"] if F["beitrag"] else "ohne"
            F["erstellen_offen"] = False
            if not F["beitrag"]:
                zur_hauptseite(abbrechen=True)
        except Exception as e:                                   # Stopp, KabelFehler, Verbindungswechsel, Netz …
            # Artur 17.11.2026 (ersetzt „am aktuellen Bildschirm weitermachen“ vom 13.11.): „bei einem Hänger verwirfst
            # du den post und machst ihn neu, um nicht verwirrt zu werden“ – auch bei Kabel ab / Kabel↔WLAN mitten im
            # Post. Einmal neu (kein 2. AirDrop, Kachel nach Länge + Hook); scheitert es wieder → Video „fehler“, nächstes.
            verbindung_merken(False)
            if neustarts >= 1 or versuch == MAX_WIEDERAUFNAHMEN:
                raise Stopp(f"{e} – auch im 2. Versuch (Beitrag neu) gescheitert")
            neustarts += 1
            if type(e).__name__ == "KabelFehler":
                log(f"Kabel: {e} → Server neu"); seh.kabel().neu_verbinden()
            log(f"Hänger/Verbindungswechsel („{str(e)[:90]}“) → Beitrag verwerfen, Video neu (Artur 17.11.)")
            zur_hauptseite(abbrechen=True)
            F.update(produkt=None, beitrag=False, cover=False, text=False, link=False, erstellen_offen=False)
            _umbenannt = False
    aus = F["ohne_link"]
    test_entwurf = entwurf
    weg = F["produkt"] if not aus else "ohne Link"
    abschluss(entwurf or aus)
    if F["produkt"] == "erstellen":                              # Szenario 3 (Aufnahme 16.11.): nach dem Speichern steht
        try:                                                     # wieder „Produkt umbenennen“ → Blatt → Produktseite offen →
            zur_hauptseite(abbrechen=True)                       # gleich zurück, sonst stapeln sich die Seiten beim nächsten
        except Stopp as e:                                       # Video
            log(f"Aufräumen nach „Jetzt erstellen“: {e}")
    entwurf = entwurf or aus
    dauer = time.time() - start
    if not entwurf:
        subprocess.run(["zsh", str(HIER / "gepostet.sh"), "eintragen", str(datei), d["account"]], capture_output=True)
        schreibe(p, d, "gepostet", f"post_mensch ({weg}), {dauer:.0f} s")
        _LETZTE_KACHEL = d.get("kachel", "")
    elif aus:
        schreibe(p, d, "entwurf", "ausverkauft/nicht verfügbar – als Entwurf ohne Link gespeichert")
    else:                                                        # 15.11.: auch --entwurf merken → Neustart macht ihn nicht doppelt
        schreibe(p, d, "entwurf", f"als Entwurf gespeichert ({weg}), {dauer:.0f} s")
    eintragen(d, dauer, weg, entwurf)
    print(f"✓ {d['datei']} → {d['account']} ({weg}{', Entwurf' if entwurf else ''}) {dauer:.0f} s", flush=True)
    if aufr and not entwurf:
        aufraeumen_im_hintergrund(d)                             # 16.11.: Mac-Safari parallel zum nächsten Video
    elif aufr and aus and not test_entwurf:                      # 16.11.: im --entwurf-Test Social1 nicht anfassen                                           # Artur 16.11.2026: ausverkauft/nicht provisionsberechtigt
        pid = d.get("tts_link", "").rstrip("/").split("/")[-1]  # → Vorbild in Social1-Liste „nicht verfügbar“ verschieben
        social1_warten()                                         # nie zwei Social1-Schritte gleichzeitig im Mac-Safari
        try:
            log(f"Social1: {social1_verschieben(pid, liste_fuer(d))}")
        except Exception as e:
            log(f"Social1 verschieben ging nicht: {e}")
    return dauer


def lade(pfad):
    p = pathlib.Path(pfad)
    if not p.exists():
        p = EIN / pfad
    return p, json.loads(p.read_text(encoding="utf-8"))


DATALESS = 0x40000000                                            # macOS SF_DATALESS: Datei liegt nur in iCloud


def icloud_holen(pfad, max_s=300):
    """15.11.2026: iCloud-ausgelagerte Dateien (Video/JSON) erst herunterladen – sonst hängt Lesen/AirDrop minutenlang."""
    p = pathlib.Path(pfad)
    try:
        if not (os.stat(p).st_flags & DATALESS):
            return True
    except FileNotFoundError:
        return False
    log(f"iCloud: lade {p.name} herunter …")
    subprocess.run(["brctl", "download", str(p)], capture_output=True, timeout=60)
    ende = time.time() + max_s
    while time.time() < ende:
        if not (os.stat(p).st_flags & DATALESS):
            return True
        time.sleep(3)
    return False


def airdrop_einmal(d):
    """Jedes Video nur EINMAL per AirDrop (Artur 15.11.2026), auch nach Neustarts. Gilt als gesendet, sobald der
    Empfänger angeklickt ist. Ankunft am Bildschirm nicht erkannt → kein Fehler: die Galerie-Prüfung (Länge + Hook,
    bis 120 s) entscheidet, ob das Video da ist."""
    merk = AUS / "letztes-airdrop.txt"
    alle = AUS / f"airdrop-{d['stapel']}.txt"                     # angeklickt (Übertragung gestartet)
    da = AUS / f"airdrop-{d['stapel']}-da.txt"                    # 16.11.2026: Ankunft am iPhone GESEHEN (Fotos)
    if airdrop_schon_da(d["datei"], da):
        log("schon am iPhone (Ankunft früher gesehen) – kein zweites AirDrop"); return
    if airdrop_schon_da(d["datei"], alle) or (merk.exists() and merk.read_text().strip() == d["datei"]):
        # 16.11.2026 (Video 145-04): früher angeklickt, Ankunft aber nie gesehen (z. B. Lauf abgebrochen, AirDrop hing) →
        # galt als „schon am iPhone“, die Galerie wartete vergeblich. Jetzt: nochmal senden (Artur 16.11. 22:25:
        # „wenn der AirDrop nicht zuverlässig ist, airdrop nochmal“). Doppelt in Fotos schadet nicht (Galerie wählt nach
        # Länge + Hook, Fotos-Aufräumen löscht alle passenden Kacheln).
        log("früher angeklickt, Ankunft nie gesehen → nochmal per AirDrop")

    def gesendet():
        merk.write_text(d["datei"])
        with open(alle, "a") as fa:
            fa.write(d["datei"] + "\n")
    if not seh.kabel():
        raise Stopp("Kabel-Steuerung nicht aktiv – kein AirDrop")
    import airdrop
    try:                                                         # Fotos noch vorn → würde sofort als „angekommen“ gelten
        if airdrop._fotos_vorn(seh.lesen()):
            seh.kabel().taste("home"); time.sleep(0.6)
    except Exception:
        pass
    datei = frisch_datiert(EIN / d["datei"])
    letzter = None
    for versuch in (1, 2):                                       # 16.11.2026: kommt es nicht an → sofort nochmal (vorher
        try:                                                     # erst in der TikTok-Galerie nach 15 s → Fotos sprang
            _AIRDROPS[d["datei"]] = _AIRDROPS.get(d["datei"], 0) + 1   # mitten in TikTok auf → Hänger)
            erg = airdrop.senden([str(datei)], nach_klick=gesendet)
            if erg == "fotos":
                with open(da, "a") as fa:
                    fa.write(d["datei"] + "\n")
            log("per AirDrop aufs iPhone" + ("" if erg == "fotos" else " (Mac meldet OK, Fotos nicht gesehen – Galerie prüft)"))
            letzter = None
            break
        except Exception as e:
            letzter = e
            if versuch == 1:
                log(f"AirDrop nicht angekommen ({e}) → sofort nochmal")
                try:
                    seh.kabel().taste("home"); time.sleep(0.6)
                except Exception:
                    pass
    if letzter is not None:
        if airdrop_schon_da(d["datei"], alle):
            log(f"AirDrop gesendet, Ankunft nicht gesehen ({letzter}) – Galerie prüft")
        else:
            raise Stopp(f"AirDrop nicht gesendet: {letzter}")
    try:
        seh.kabel().taste("home"); time.sleep(0.8)
    except Exception:
        pass


_AIRDROPS = {}       # 16.11.2026: Datei → wie oft in diesem Lauf per AirDrop geschickt (Galerie schickt höchstens bis 2×)


def airdrop_schon_da(datei, liste):
    """Reine Funktion: steht die Datei als eigene Zeile in der Merkliste (Datei fehlt → nein)?"""
    try:
        return datei in pathlib.Path(liste).read_text().split("\n")
    except FileNotFoundError:
        return False


MAX_FEHLER_FOLGE = 3


def main(a):
    if not a:
        sys.exit(__doc__)
    if os.environ.get("TS_ZEITBUCH"):
        _zeitbuch_an()
    entwurf = "--entwurf" in a
    aufr = "--ohne-aufraeumen" not in a
    if "--ohne-airdrop" in a:
        os.environ["TS_OHNE_AIRDROP"] = "1"
    rest = [x for x in a if not x.startswith("--")]
    import eingang as EG
    global _SOLL_DAUER, _AKT_DATEI
    if a[0] == "--wo":                                           # Trockenlauf: nur lesen, nichts tippen
        tx = seh.lesen()
        alt = seh.kabel().bild_alter() if seh.kabel() else 0
        z = B.erkenne(tx)
        tabs = _tabs(tx) if z in (B.UNBEKANNT, B.FEED, B.PROFIL, B.TIKTOK_SONST, B.LADEN) else False
        print(f"Bildschirm: {z}{' (+ Leiste)' if tabs else ''} | Bild-Alter {alt} ms | Uhr ok: {_bild_aktuell(tx)} | "
              f"LIVE oben links: {_feed(tx)}")
        return
    try:
        if a[0] == "--aufraeumen":
            p, d = lade(rest[0]); aufraeumen(d); return
        if a[0] == "--fotos":                                    # alle geposteten Videos des Stapels aus Fotos
            fotos_aufraeumen([d for _, d in EG.alle() if d["stapel"] == rest[0] and d["status"] in ("gepostet", "entwurf")]); return
        if a[0] == "--stapel":
            liste = [(p, d) for p, d in EG.alle() if d["status"] == "freigegeben" and d["stapel"] == rest[0]]
            if not liste:
                sys.exit("nichts freigegeben")
            liste.sort(key=lambda x: (REIHENFOLGE.index(x[1]["account"]) if x[1]["account"] in REIHENFOLGE else 99, x[1]["datei"]))
        else:
            liste = [lade(rest[0])]
        try:                                                     # 15.11.: Steuerung über WLAN = Eingaben kommen nicht an
            if seh.kabel() and hasattr(seh.kabel(), "auf_usb"):
                seh.kabel().auf_usb()
        except Exception as e:
            log(f"USB-Prüfung: {e}")
        bereit = []                                              # 15.11.: iCloud-ausgelagerte Videos vorher holen
        for p, d in liste:
            if icloud_holen(EIN / d["datei"]):
                bereit.append((p, d))
            else:
                print(f"✗ {d['datei']}: Video fehlt/liegt nur in iCloud (Download hing) – übersprungen", flush=True)
                if not entwurf:
                    schreibe(p, d, "fehler", "Video nicht lokal (iCloud)")
        liste = bereit
        zeiten, aus, fertig, fehler = [], [], [], []
        folge = 0
        limit_konten = set()                                     # 17.11.2026: Tageslimit-Hinweis gesehen → Account fertig
        for p, d in liste:
            if d["account"] in limit_konten:
                if not entwurf:
                    schreibe(p, d, "fehler", f"LIMIT {d['account']} – heute nicht mehr")
                print(f"✗ {d['datei']}: LIMIT {d['account']} – Account für heute fertig, übersprungen", flush=True)
                fehler.append(d["datei"]); continue
            lim = PILOT.get(d["account"])
            if not entwurf and lim and heute_gepostet(d["account"]) >= lim:
                aus.append(d["datei"]); log(f"übersprungen (Limit {d['account']}): {d['datei']}"); continue
            log(f"── {d['datei']} → {d['account']}")
            try:
                if not os.environ.get("TS_OHNE_AIRDROP"):
                    airdrop_einmal(d)
                _SOLL_DAUER = dauer_text(EIN / d["datei"])
                _AKT_DATEI = d["datei"]
                zeiten.append(ein_video(p, d, entwurf, aufr)); fertig.append(d)
                folge = 0
            except Hart as e:
                if not entwurf:
                    schreibe(p, d, "fehler", str(e))
                if aufr and not entwurf and fertig:
                    print(f"Hinweis: {len(fertig)} gepostete Videos noch in Fotos – aufräumen: post_mensch.py --fotos {d['stapel']}", flush=True)
                sys.exit(f"STOPP bei {d['datei']}: {e}")
            except BaseException as e:                           # Sperre, Stopp, Kabel, alles andere: Video markieren, weiter
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                if not entwurf:
                    schreibe(p, d, "fehler", str(e))
                art = "SPERRE (nicht gepostet)" if isinstance(e, Sperre) else "Fehler"
                if isinstance(e, Limit):
                    limit_konten.add(d["account"]); art = f"LIMIT {d['account']}"; folge -= 1   # kein Ketten-Fehler
                print(f"✗ {d['datei']}: {art}: {e} – weiter mit dem nächsten (Steuer-Chat prüft es)", flush=True)
                fehler.append(d["datei"]); folge += 1
                try:
                    zur_hauptseite(abbrechen=True)               # halbfertigen Beitrag verwerfen → nächstes Video sauber
                except BaseException as e2:
                    if isinstance(e2, Hart):
                        sys.exit(f"STOPP: {e2}")
                    log(f"Rückweg zur Hauptseite: {e2}")
                if folge >= MAX_FEHLER_FOLGE:                    # keine Ketten-Fehler: lieber anhalten + Foto
                    foto = AUS / f"stopp-{time.strftime('%Y%m%d-%H%M%S')}.png"
                    try:
                        seh.kabel().foto(str(foto))
                    except Exception:
                        pass
                    sys.exit(f"STOPP: {folge} Videos hintereinander gescheitert (zuletzt: {e}) – Foto {foto}")
        social1_warten()                                         # 16.11.: letztes Social1-Abhaken (Hintergrund) abwarten
        if aufr and not entwurf and fertig:
            t = time.time(); fotos_aufraeumen(fertig); log(f"Fotos aufgeräumt in {time.time() - t:.0f} s")
        print(f"FERTIG {len(zeiten)}/{len(liste)}" + (f", Ø {sum(zeiten) / len(zeiten):.0f} s" if zeiten else "")
              + (f", Limit übersprungen: {len(aus)}" if aus else "") + (f", Fehler: {len(fehler)}" if fehler else ""), flush=True)
        if not entwurf:
            subprocess.run(["zsh", str(HIER / "sync.sh"), "sichern", "Posts"], capture_output=True)
    except Stopp as e:
        sys.exit(f"STOPP: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
