#!/usr/bin/env python3
"""Stapel posten über den Einkaufswagen-Weg (Artur, 10.11.2026):
pro Video  1) Produkt über Social1 → View on TikTok Shop → „Einkaufswagen“ (beliebige Variante) in den Wagen des Accounts,
           2) Video hochladen (Galerie von unten nach oben durchsuchen),
           3) Link hinzufügen → Produkt → „Weitere Produkte hinzufügen“ → „Einkaufswagen“ → Produkt → Hinzufügen,
           4) Button-Text, Beschreibung + Brand, Veröffentlichen, eintragen, liken.
Nie „Kasse“. Bei Unklarem STOPP.

  python3 werkzeuge/post_wagen.py <stapel>
"""
import json, pathlib, re, subprocess, sys, time, unicodedata
import seh, stock, posten as P, eingang as EG
from posten import taps, schnell, key, Stopp, muss, log

HIER = pathlib.Path(__file__).resolve().parent


def _tippe_einfuegen(text):
    """10.11.2026: Einzel-Tastenanschläge kommen am iPhone nicht an → Text per ⌘V (Einfügen an der Cursor-Stelle)."""
    P.front()
    if seh.kabel():                                              # Kabel: Tippen kommt zuverlässig an (12.11.2026),
        seh.kabel().schreibe(text, menschlich=True)              # Zwischenablage war manchmal noch alt
        time.sleep(0.4)
        return
    else:
        subprocess.run(["pbcopy"], input=text.encode("utf-8")); time.sleep(1.5)   # Zwischenablage braucht bis zum iPhone
        subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "v" using command down'])
    gesehen = False
    for i in range(30):                                          # „Einsetzen von ‚MacBook …‘“ erscheint verzögert, läuft bis ~15 s
        da = bool(seh.finde("Einsetzen von"))
        gesehen |= da
        if not da and (gesehen or i >= 4):
            break
        time.sleep(0.6)
    time.sleep(0.4)


P.tippe = _tippe_einfuegen
PROJ = HIER.parent


def einfuegen(text):
    """Adressleiste: Tastenanschläge kamen über die Synchronisierung oft nicht an, ⌘V schon (10.11.2026). Kabel: schnell tippen."""
    if seh.kabel():
        return seh.kabel().schreibe(text)
    _tippe_einfuegen(text)


def _kurz(k):
    """⌘-Kürzel am iPhone: Kabel → Tastatur übers Kabel, sonst Mac-Tastatur in die iPhone-Synchronisierung."""
    if seh.kabel():
        return seh.kabel().taste("cmd+" + k)
    subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{k}" using command down'])


def geraet(*cmd):
    if seh.kabel():                                              # Kabel: „SCROLL 0 dy …“ → echtes Ziehen
        for c in cmd:
            t = c.split()
            if t[0] == "SCROLL":
                dy = int(t[2]) * int(t[3]) if len(t) > 3 else int(t[2])
                h = seh.kabel().hoehe()
                weg = max(-0.35, min(0.35, dy / 150)) * h        # dy>0 = Inhalt runter (ältere/obere Zeilen), Finger nach unten
                seh.kabel().ziehe(167, h * 0.5 - weg / 2, 167, h * 0.5 + weg / 2, 0.35)
        return
    subprocess.run([str(HIER / "bin" / "zeiger"), "rel", "0.5", "0.6"], capture_output=True)
    subprocess.run([sys.executable, str(PROJ / "geraet" / "geraet.py"), "MOVE 4 0", "MOVE -4 0", *cmd], capture_output=True)


# ---------------------------------------------------------------- Kachel in der Galerie

def _kn(t):
    t = t.upper().replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")
    t = re.sub(r"(\d)\s*[€CE](?=[?!17\s]|$)", r"\1€", t)
    if "€" in t and len(re.sub(r"[^A-Z0-9]", "", t.split("€")[0])) >= 6:
        t = t.split("€")[0]
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", t))


def _kpasst(kachel, ocr):
    k, o = _kn(kachel), _kn(ocr)
    if not k or not o.startswith(k):
        return False
    rest = o[len(k):]
    return len(rest) <= 3 and all(c in "17UGOECA" for c in rest)


def kachel_suchen(kachel):
    time.sleep(1.5)
    for _ in range(14):
        tr = [t for t in seh.lesen() if 140 < t[2] < 660 and _kpasst(kachel, t[0])]
        if tr:
            return max(tr, key=lambda t: t[2])                   # unterste = neueste
        geraet("SCROLL 0 10 2 15"); time.sleep(1.2)
    return None


def hochladen(kachel):
    taps(167, 681, "w1.8")
    if seh.finde("Kamera") and seh.finde("OK", genau=True):     # Hinweis „Kamera nicht verfügbar“ (Kabel: Kamera läuft)
        x, y = muss(seh.finde("OK", genau=True), "Kamera-Hinweis ohne OK"); taps(x, y, "w0.8")
    taps(30, 672, "w1.8")
    for _ in range(2):                                           # Reiter „Videos“ (nicht LIVE-Aufnahmen o. Ä.)
        a = seh.finde("Videos", genau=True, ueber=150)
        if a:
            subprocess.run([sys.executable, str(HIER / "tap.py"), str(round(a[0])), str(round(a[1])), "w1.2"], capture_output=True)
    t = muss(kachel_suchen(kachel), f"Kachel „{kachel}“ nicht in der Galerie")
    for _ in range(3):                                           # Kachel zu weit oben → Auswahlkreis läge auf der Reiterleiste
        if t[2] >= 215:
            break
        geraet("SCROLL 0 10 2 15"); time.sleep(1.2)
        t = muss(kachel_suchen(kachel), f"Kachel „{kachel}“ nicht in der Galerie")
    _, x, y = t
    sp = min(2, max(0, int((x - 8) // 107.5)))
    # Auswahlkreis = oben rechts der Kachel. Kachel-Oberkante aus der Dauer-Anzeige der Kachel darüber (gleiche Spalte)
    dauer = [d for d in seh.lesen() if re.match(r"^\d\d[:.]\d\d", d[0].strip()) and int((d[1] - 8) // 107.5) == sp and d[2] < y]
    cy = (max(d[2] for d in dauer) + 26) if dauer else y - 18
    if cy < 150:
        cy = y - 18
    taps(8 + 107.5 * (sp + 1) - 12, cy, "w1.0")
    if not seh.warte("Weiter", 2, unter=650) or not [w for w in seh.lesen() if w[0].strip() == "1"]:
        pass
    muss(seh.warte("Weiter", 3, unter=650), "Video nicht ausgewählt")
    tx = seh.lesen()
    muss([t for t in tx if _kpasst(kachel, t[0])], "nach Auswahl ist die Kachel nicht mehr zu sehen – Abbruch (falsches Video?)")
    taps(242, 680, "safe", "w2.5")
    if not seh.finde("Link hinzufügen"):
        muss(seh.warte("Deine Story", 4), "Editor nicht erreicht")
        taps(242, 680, "safe", "w2.5")
    muss(seh.warte("Link hinzufügen", 4), "Beitragsseite nicht erreicht")


# ---------------------------------------------------------------- Einkaufswagen

def _tabs_da():
    tx = seh.lesen()
    return bool(seh.finde("Für dich", tx, ueber=130) or seh.finde("TikTok Studio", tx))


def tiktok_auf():
    if seh.finde("iPhone-Kamera"):
        x, y = muss(seh.finde("OK", genau=True), "Kamera-Hinweis ohne OK"); taps(x, y, "w1.0")
    stock.home()
    _, y = muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2"); schnell("TikTok"); time.sleep(1.5)
    muss(seh.warte("TikTok", 4, ueber=200), "TikTok nicht in der Suche")
    taps(62, 145, "w3.5")
    for _ in range(3):
        if seh.finde("iPhone-Kamera"):
            x, y = muss(seh.finde("OK", genau=True), "Kamera-Hinweis ohne OK"); taps(x, y, "w1.0")
        if kamera_zu():
            continue
        break


def kamera_zu():
    """Kamera-/Aufnahme-Seite offen („Sound hinzufügen“) → X oben links (Kabel: x=24 auf Höhe des Texts)."""
    snd = seh.finde("Sound hinzufügen")
    if not snd:
        return False
    taps(24, snd[1], "w1.5") if seh.kabel() else taps(67, 110, "w1.5")
    return True


def zu_tabs():
    for _ in range(6):
        if _tabs_da():
            return
        if kamera_zu():
            continue
        tx = seh.lesen(); txt = " ".join(t.lower() for t, _, _ in tx)
        # 12.11.2026: blinde Zurück-Tipps landeten im LIVE-Event-Bereich bzw. bei „Konto hinzufügen“ → bei solchen Seiten sofort Stopp
        if any(w in txt for w in ("live-event", "event erstellen", "live gehen", "registrieren", "konto hinzufügen", "kasse")):
            raise Stopp("Unerwartete Seite (LIVE/Registrieren/Kasse) – nichts mehr angetippt")
        if seh.kabel():
            K = seh.kabel(); K.taste("home"); time.sleep(0.8)  # sicherer Weg: TikTok neu nach vorn holen, dann Home-Symbol
            tiktok_auf(); time.sleep(1.0)
            if _tabs_da():
                return
            tx = seh.lesen()
            if seh.finde("Profil", tx, unter=650) or seh.finde("Freund*innen", tx):
                taps(33, 681, "w1.6"); continue                  # Home-Symbol unten links
            continue
        taps(23, 92, "w1.6")                                     # alte Steuerung: X/Zurück oben links
    muss(_tabs_da(), "TikTok-Hauptseite nicht erreicht")


def in_wagen(pid):
    stock.home()
    _, y = muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2"); schnell("Safari"); time.sleep(1.2)
    muss(seh.warte("Safari", 3, ueber=200), "Safari nicht in der Suche")
    taps(62, 145, "w2.0")
    if seh.kabel():                                              # Kabel: ⌘L springt in die Adressleiste (12.11.2026;
        seh.kabel().taste("cmd+l"); time.sleep(0.8)              # fester Tipp traf dort das Mikrofon → Diktierfunktion)
    else:
        leiste = [t for t in seh.lesen() if t[2] > 640 and ("." in t[0] or "suchen" in t[0].lower())]
        muss(leiste, "Safari-Adressleiste nicht gefunden")
        taps(167, leiste[0][2], "w1.0")
        if not seh.finde("Website suchen"):
            taps(241, 686, "w0.6")
    einfuegen(f"social1.ai/products/{pid}"); time.sleep(0.5); key(36)
    f = seh.warte("View on TikTok Shop", 6)
    if not f:                                                    # Return kam nicht an → obersten Vorschlag antippen
        vs = [t for t in seh.lesen() if t[2] < 200 and pid[:10] in t[0].replace(" ", "")]
        vy = round(vs[0][2] - 9) if vs else 98
        for _ in range(4):                                       # erster Tipp landet oft am alten Zeiger
            subprocess.run([sys.executable, str(HIER / "tap.py"), "120", str(vy), "w1.0"], capture_output=True)
            f = seh.warte("View on TikTok Shop", 4)
            if f:
                break
        f = f or seh.warte("View on TikTok Shop", 10)
    muss(f, "Social1-Seite ohne „View on TikTok Shop“")
    taps(f[0], f[1], "w3.0")
    for i in range(30):
        tx = seh.lesen(); o = seh.finde("Öffnen", tx, genau=True)
        if o:
            taps(o[0], o[1], "w2.5"); continue
        vv = seh.finde("View on TikTok Shop", tx)
        if vv and i % 5 == 4:                                    # Tipp kam nicht an → nochmal
            taps(vv[0], vv[1], "w3.0"); continue
        if seh.finde("Kasse", tx, unter=640) and seh.finde("Einkaufswagen", tx, unter=640):
            break
        time.sleep(0.5)
    else:
        raise Stopp("TikTok-Produktkarte nicht erreicht")
    # Artur 10.11.: erst Showcase versuchen; Einkaufswagen NUR, wenn es schon im Showcase ist
    v = muss(seh.warte("pro Verkauf", 4), "Provisions-Badge fehlt")
    taps(v[0], v[1], "w2.5")
    tx = seh.lesen()
    z = seh.finde("Showcase hinzufügen", tx)
    if z:
        taps(z[0], z[1], "w2.2")
        log("ins Showcase gelegt")
        zu_tabs(); return "showcase"
    log("schon im Showcase → Einkaufswagen")
    wa = seh.finde("Werbeaktion")
    if wa:                                                       # Werbeaktions-Blatt schließen (Pfeil ~29 Pkt über dem Titel;
        taps(167, wa[1] - 29 if seh.kabel() else 165, "w1.8")    # Kabel 12.11.: fester Wert 165 lag unter dem Pfeil)
    muss(seh.warte("Kasse", 3, unter=640), "Produktkarte nach Blatt nicht zurück")
    w = seh.finde("Einkaufswagen", unter=640)
    muss(w and w[0] < 150, "Einkaufswagen-Knopf nicht links unten")
    taps(w[0], w[1], "w2.5")
    versucht = set()
    for _ in range(14):                                          # Varianten wählen (beliebig); ausverkaufte überspringen
        tx = seh.lesen()
        b = seh.finde("Bitte auswählen", tx)
        if not b:
            break
        opt = [t for t in tx if b[1] + 15 < t[2] < b[1] + 140 and len(t[0].strip()) > 0
               and "tabelle" not in t[0].lower() and (round(t[1]), round(t[2])) not in versucht]
        muss(opt, "keine wählbare Variante")
        o = min(opt, key=lambda t: (round(t[2] / 10), t[1]))
        versucht.add((round(o[1]), round(o[2])))
        taps(o[1], o[2], "w1.0")
    probiert = set(); farben = [119, 193, 267, 45]
    for _ in range(16):                                          # „nicht vorrätig“ → andere Größe, dann andere Farbe
        tx = seh.lesen()
        if not seh.finde("nicht vorrätig", tx):
            break
        gr = seh.finde("Größe:", tx)
        opt = [t for t in tx if gr and gr[1] + 15 < t[2] < gr[1] + 100 and re.search(r"\d", t[0])
               and (round(t[1]), round(t[2])) not in probiert] if gr else []
        if opt:
            o = min(opt, key=lambda t: (round(t[2] / 10), t[1])); probiert.add((round(o[1]), round(o[2])))
            taps(o[1], o[2], "w1.2"); continue
        fb = seh.finde("Farbe:", tx)
        muss(fb and farben, "Artikel nicht vorrätig, keine weitere Variante")
        taps(farben.pop(0), fb[1] + 42, "w1.2"); probiert.clear()
    muss(not seh.finde("nicht vorrätig"), "keine vorrätige Variante gefunden")
    tx = seh.lesen()
    btn = [t for t in tx if t[2] > 640 and t[0].strip() == "Einkaufswagen"]
    muss(btn, "Knopf „Einkaufswagen“ in der Auswahl fehlt")
    muss(not seh.finde("Kasse", tx, unter=640) or abs(btn[0][1] - 167) < 60, "Knopf-Lage unklar (Kasse?)")
    taps(btn[0][1], btn[0][2], "w2.0")
    ok = False
    for i in range(10):
        tx = seh.lesen()
        if seh.finde("hinzugefügt", tx) or seh.finde("Zur Kasse (", tx):      # Bestätigung oder Wagen-Seite (nie Kasse tippen)
            ok = True; break
        if seh.finde("Bitte auswählen", tx):
            raise Stopp("Variante noch nicht gewählt")
        nb = [t for t in tx if t[2] > 640 and t[0].strip() == "Einkaufswagen"]
        if nb and i in (3, 7):                                   # Tipp kam nicht an → nochmal
            taps(nb[0][1], nb[0][2], "w1.5")
        time.sleep(0.5)
    muss(ok, "nicht in den Einkaufswagen gelegt")
    log("im Einkaufswagen")
    zu_tabs(); return "wagen"


def verlinken_wagen(produkt, button):
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
    for _ in range(3):
        if seh.finde("Gekaufte Produkte", unter=600):
            break
        w = muss(seh.finde("Weitere Produkte hinzufügen"), "„Weitere Produkte hinzufügen“ fehlt")
        taps(w[0], w[1], "w1.8")
    e = muss(seh.finde("Einkaufswagen", unter=560), "Auswahl „Einkaufswagen“ fehlt")
    taps(e[0], e[1], "w2.2")
    muss(seh.warte("Produkte suchen", 3), "Einkaufswagen-Liste nicht offen")
    tx = seh.lesen()
    titel = sorted([t for t in tx if t[2] > 220 and len(t[0]) > 12], key=lambda t: t[2])
    muss(titel, "Einkaufswagen leer?")
    py = titel[0][2]                                             # oberster Eintrag = gerade hinzugefügt
    block = " ".join(t[0] for t in tx if py - 5 <= t[2] <= py + 50).lower()
    muss(produkt.lower() in block, f"oberster Wagen-Eintrag ist nicht „{produkt}“: {block[:80]}")
    h = [t for t in tx if t[0].startswith("Hinzuf") and py - 10 < t[2] < py + 110]
    muss(h, "Hinzufügen-Knopf beim Produkt fehlt")
    taps(h[0][1], h[0][2], "w2.0")
    tx = seh.lesen(); d = seh.finde("zum Video", tx)
    if d:
        _, y = muss(seh.finde("Hinzufügen", tx, genau=True, unter=d[1]), "Dialog ohne Hinzufügen")
        taps(167, y, "w2.0")
    muss(seh.warte("Produkt umbenennen", 3), "Seite Produkt umbenennen fehlt")
    button_setzen(button)



def verlinken_showcase(produkt, button):
    """wie posten.verlinken, aber Button-Text per Einfügen (Tastenanschläge kommen nicht an)."""
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
                    f"„{produkt}“ nicht oben im Showcase")
    by = muss(seh.finde("Hinzufügen", tx, genau=True, unter=ny, ueber=ny + 120), "Produkt ausverkauft? (kein Hinzufügen)")
    taps(264, by[1], "w2.0")
    tx = seh.lesen(); d = seh.finde("zum Video", tx)
    if d:
        _, y = muss(seh.finde("Hinzufügen", tx, genau=True, unter=d[1]), "Dialog ohne Hinzufügen")
        taps(167, y, "w2.0")
    muss(seh.warte("Produkt umbenennen", 3), "Seite Produkt umbenennen fehlt")
    button_setzen(button)


def button_setzen(button):
    pn = seh.finde("Produktname")
    fy = (pn[1] + 58) if pn else 326
    for versuch in range(3):                                     # Feld leeren klappt nicht immer → prüfen und wiederholen
        subprocess.run([sys.executable, str(HIER / "tap.py"), "170", "470", "w0.4", "200", str(round(fy)), "w0.9"], capture_output=True)
        _kurz("a"); time.sleep(0.6)
        if versuch == 0:
            P.tippe(button)
        elif seh.kabel():
            seh.kabel().loeschen(30); P.tippe(button)
        else:
            _kurz("v")
            time.sleep(1.0)
            for _ in range(25):
                if not seh.finde("Einsetzen von"):
                    break
                time.sleep(0.6)
        time.sleep(0.5)
        feld = [t for t in seh.lesen() if fy - 15 < t[2] < fy + 15]
        if feld and feld[0][0].strip() == button:
            break
    muss(seh.aehnlich(button), f"Button-Text „{button}“ nicht im Feld")
    taps(167, 678, "safe", "w2.2")
    muss(seh.warte("Veröffentlichen", 3, unter=640), "nach Hinzufügen nicht auf der Beitragsseite")
    muss(seh.aehnlich(button), "Produkt-Link fehlt auf der Beitragsseite")


def beschreiben_oder_ohne_brand(v):
    """Shop-Account nicht eindeutig (nur Länder-Accounts o. Ä.) → ohne Brand posten (Artur 10.11.: „weiter posten“)."""
    try:
        P.beschreiben(v["text"], v["brand"], v["handle"]); log("Text + Brand")
    except Stopp as e:
        if "Trefferliste" not in str(e):
            raise
        for _ in range(3):                                       # Erwähnung schließen (Tipp kommt nicht immer an)
            subprocess.run([sys.executable, str(HIER / "tap.py"), "22", str(P.oben(94)), "w1.5"], capture_output=True)
            if seh.warte("Veröffentlichen", 3, unter=640):
                break
        muss(seh.finde("Veröffentlichen", unter=640), "nach Erwähnung-Schließen nicht auf der Beitragsseite")
        log(f"OHNE Brand – „{v['brand']}“ nicht eindeutig")
        with open(PROJ / "uebergabe" / "ausgang" / "ohne-brand.txt", "a") as f:
            f.write(f"{time.strftime('%d.%m. %H:%M')}\t{pathlib.Path(v['datei']).name}\t{v['brand']}\n")


def rest_posten(p, d, start):
    v = {"datei": str(EG.EIN / d["datei"]), "kachel": d["kachel"], "produkt": d["produkt"],
         "tts_id": d.get("tts_link", "").rstrip("/").split("/")[-1], "button": d["button"],
         "text": EG.text_von(d), "brand": d["brand"], "handle": d.get("handle", "")}
    beschreiben_oder_ohne_brand(v)
    P.veroeffentlichen(); log("VERÖFFENTLICHT")
    subprocess.run(["zsh", str(HIER / "gepostet.sh"), "eintragen", v["datei"], d["account"]])
    P.eintragen_log(d["account"], v, start)
    EG.schreibe(p, d, "gepostet", "Einkaufswagen-Weg")


# ---------------------------------------------------------------- Account

def profil(account):
    for _ in range(3):                                           # direkt nach dem Posten reagiert der Reiter oft erst beim 2. Tipp
        taps(306, 681, "w1.8")
        if seh.finde("Nicht erlauben"):
            x, y = seh.finde("Nicht erlauben"); taps(x, y, "w1.2")
        if seh.warte("@" + account, 3):
            P.beitraege()
            return
        if [t for t in seh.lesen() if t[0].startswith("@") and t[2] < 200]:
            break                                                # anderes Profil sichtbar → wechseln
    name = [t for t in seh.lesen() if t[2] < 145 and t[1] < 220 and "@" not in t[0] and len(t[0]) > 4]
    muss(name, "Account-Name oben nicht gefunden")
    for _ in range(3):
        subprocess.run([sys.executable, str(HIER / "tap.py"), str(round(name[0][1])), str(round(name[0][2])), "w2.0"], capture_output=True)
        if seh.warte("Konto wechseln", 3):
            break
    muss(seh.warte("Konto wechseln", 3), "„Konto wechseln“ öffnet sich nicht")
    # 12.11.2026: Liste fährt animiert auf. Erst tippen, wenn die Zeile zweimal an derselben Stelle steht
    # (sonst lag beim Tipp schon „Konto hinzufügen“ dort → Registrieren-Seite).
    z, vorher = None, None
    for _ in range(12):
        time.sleep(0.5)
        tx = seh.lesen()
        z = seh.finde(account, tx, unter=330)
        if z and vorher and abs(z[1] - vorher[1]) < 3:
            neu = seh.finde("Konto hinzufügen", tx)
            if neu and abs(neu[1] - z[1]) < 35:
                raise Stopp("„Konto hinzufügen“ zu nah am Account – nicht getippt")
            break
        vorher, z = z, None
    z = muss(z, f"{account} nicht (ruhig) in „Konto wechseln“")
    subprocess.run([sys.executable, str(HIER / "tap.py"), str(round(z[0])), str(round(z[1])), "w4.0"], capture_output=True)
    if not seh.warte("@" + account, 4):
        subprocess.run([sys.executable, str(HIER / "tap.py"), str(round(z[0])), str(round(z[1])), "w4.0"], capture_output=True)
    muss(seh.warte("@" + account, 6), f"Account-Wechsel zu {account} hat nicht geklappt")
    P.beitraege()
    log(f"Account gewechselt: {account}")


def ein_post(p, d):
    start = time.time()
    v = {"datei": str(EG.EIN / d["datei"]), "kachel": d["kachel"], "produkt": d["produkt"],
         "tts_id": d.get("tts_link", "").rstrip("/").split("/")[-1], "button": d["button"],
         "text": EG.text_von(d), "brand": d["brand"], "handle": d.get("handle", "")}
    r = subprocess.run(["zsh", str(HIER / "gepostet.sh"), "pruefen", v["datei"]], capture_output=True, text=True)
    if r.returncode != 0:
        raise Stopp(f"Doppel-Schutz: {r.stdout.strip()}")
    tiktok_auf(); zu_tabs(); profil(d["account"]); log("Account ok")
    import os
    if os.environ.pop("OHNE_WAGEN_EINMAL", None):                # Produkt liegt schon im Wagen (Hand-Fortsetzung)
        weg = "wagen"; zu_tabs()
    else:
        weg = in_wagen(v["tts_id"])
    zu_tabs(); profil(d["account"])
    hochladen(v["kachel"]); log("Beitragsseite")
    if weg == "showcase":
        verlinken_showcase(v["produkt"], v["button"])
        log("Produkt verlinkt (Showcase)")
    else:
        verlinken_wagen(v["produkt"], v["button"]); log("Produkt verlinkt (Einkaufswagen)")
    beschreiben_oder_ohne_brand(v)
    P.veroeffentlichen(); log("VERÖFFENTLICHT")
    subprocess.run(["zsh", str(HIER / "gepostet.sh"), "eintragen", v["datei"], d["account"]])
    P.eintragen_log(d["account"], v, start)
    EG.schreibe(p, d, "gepostet", "Einkaufswagen-Weg")
    try:
        P.liken(d["account"], v["kachel"]); log("geliked + gespeichert")
    except Stopp as e:
        log(f"Hinweis: {e}")
    log(f"fertig in {time.time() - start:.0f} s")


def main(a):
    st = a[0]
    liste = [(p, d) for p, d in EG.alle() if d["status"] == "freigegeben" and d["stapel"] == st]
    liste.sort(key=lambda x: (EG.REIHENFOLGE.index(x[1]["account"]) if x[1]["account"] in EG.REIHENFOLGE else 99, x[1]["datei"]))
    P.front()
    for p, d in liste:
        log(f"── {d['datei']} → {d['account']}")
        try:
            ein_post(p, d)
        except Stopp as e:
            EG.schreibe(p, d, "fehler", str(e))
            sys.exit(f"STOPP bei {d['datei']}: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
