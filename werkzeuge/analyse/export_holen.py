#!/usr/bin/env python3
"""Partnerbestellungen-Export eines Accounts holen (iPhone am Kabel, TikTok) und per AirDrop auf den Mac.
  python3 werkzeuge/analyse/export_holen.py konto1 [konto2 …]     (Export + Guthaben)
  python3 werkzeuge/analyse/export_holen.py --guthaben konto1 …   (nur „Verfügbare Auszahlung“ ablesen)
  python3 werkzeuge/analyse/export_holen.py --praemien konto1 …   (Guthaben + Prämien aus „Belohnungen“ → praemien.json)
Ablauf: Profil → Konto wechseln → TikTok Shop für Creator*innen → Toolkit → Einnahmen → Partnerbestellungen →
Herunterladen → Bestätigen → Datei laden (Safari) → Downloads → Teilen → AirDrop „MacBook Pro von Andreas“.
Ergebnis: werkzeuge/analyse/exporte/<konto>.xlsx. Nie „Abheben“ tippen. Eine Zeile pro Konto, bei Problem STOPP."""
import os, sys, time, glob, shutil, pathlib
HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent))
import kabel as K, seh

EXP = HIER / "exporte"; DL = pathlib.Path.home() / "Downloads"
GEFAHR = ("abheben", "jetzt kaufen", "kasse", "posten", "veröffentlichen", "story", "folgen", "nachricht senden")
# Bildschirme, auf denen nie automatisch getippt wird → sofort STOPP (20.11.2026: Story wurde versehentlich gepostet)
SPERRE = ("veröffentlichen", "was läuft", "sichtbar", "zur story", "beschreibung hinzufügen", "aufnehmen", "vorlagen")


def gesperrt(tx):
    if any(t.strip() == "Posteingang" for t, _, _ in tx):   # Posteingang zeigt „Deine Story“, ist aber harmlos
        return None
    knopf = next((t for t, _, _ in tx if t.strip().lower() in ("posten", "deine story", "story", "teilen mit")), None)
    return knopf or next((t for t, _, _ in tx if any(w in t.lower() for w in SPERRE)), None)


class Stopp(Exception):
    pass


def rot_popup(tx):
    """Rotes Werbe-Popup im Creator-Bereich („Poste ein Video …“). Nie ein Knopf „Posten“/„Posteingang“ und nie,
    wenn ein Post-/Story-Bildschirm offen ist (20.11.2026)."""
    if gesperrt(tx):
        return None
    return next(((x, y) for t, x, y in tx if t.lower().startswith("poste ") and len(t) > 12), None)


def tipp(x, y, w=1.5):
    K.tipp(x, y); time.sleep(w)
    g = gesperrt(seh.lesen())        # nach jedem Tipp: Post-/Story-Bildschirm aufgegangen? → sofort aufhören
    if g:
        raise Stopp(f"Post-/Story-Bildschirm aufgegangen („{g}“) – tippe nichts mehr, Artur schaut")


POPUP = ("Jetzt nicht", "Später", "Nicht jetzt", "Schließen", "Abbrechen")


def warte(muster, sek=12, **kw):
    ende = time.time() + sek
    while True:
        tx = seh.lesen()
        p = seh.finde(muster, tx, **kw)
        if p:
            return p
        for w in POPUP:
            q = seh.finde(w, tx, genau=True)
            if q and w.lower() not in muster.lower():
                tipp(*q, 1.5)
                break
        if time.time() > ende:
            raise Stopp(f"„{muster}“ nicht gefunden")
        time.sleep(0.6)


def tipp_text(muster, sek=12, w=2, **kw):
    x, y = warte(muster, sek, **kw)
    tx = seh.lesen()
    for t, a, b in tx:
        if any(g in t.lower() for g in GEFAHR) and abs(b - y) < 12 and abs(a - x) < 60:
            raise Stopp(f"Gefahr neben „{muster}“: {t}")
    tipp(x, y, w)
    return x, y


def tiktok_profil():
    K.taste("home"); time.sleep(1.2)
    tipp_text("Suchen", w=1.2)
    K.text("TikTok"); time.sleep(1); K.taste("return"); time.sleep(4)
    if seh.finde("Siri-Vorschl"):     # Tippen ging daneben → TikTok-Symbol in den Vorschlägen
        x, y = warte("TikTok", 4, genau=True); tipp(x, y - 25, 4)
    for i in range(12):
        tx = seh.lesen()
        g = gesperrt(tx)
        if g:
            raise Stopp(f"Post-/Story-Bildschirm offen („{g}“) – tippe nichts, Artur schaut")
        # Eigenes Profil = „Gefolgt“ ohne „Nachricht“ (fremde Profile haben „Nachricht“); hier NIE oben links tippen (Stift = Story)
        if seh.finde("Gefolgt", tx) and not seh.finde("Nachricht", tx):
            return
        q = next((seh.finde(w, tx, genau=True) for w in POPUP if seh.finde(w, tx, genau=True)), None)
        if q:
            tipp(*q, 1.5)
        elif seh.finde("Posteingang", tx, genau=True) or seh.finde("Für dich", tx):
            tipp(299, 681, 2.5)       # Hauptseite mit unterer Leiste → Profil-Reiter (nur hier, sonst trifft der Tipp Inhalte)
        elif seh.finde("Exportverlauf", tx):
            tipp(310, 129, 1.5)       # Download-Blatt zu
        else:
            tipp(22, 58, 2.5)         # sonst immer zurück (oben links)
    raise Stopp("eigenes Profil nicht gefunden")


def konto_wechseln(konto):
    if not seh.finde("Konto wechseln"):
        konto_liste_oeffnen()
    warte("Konto wechseln", 6)
    p = seh.finde(konto, genau=True) or seh.aehnlich(konto, schwelle=0.8)   # OCR liest z. B. „andreastastlane“
    if not p:
        raise Stopp(f"Konto „{konto}“ nicht in der Liste")
    tipp(*p, 5)
    warte("Gefolgt", 15)


def konto_liste_oeffnen():
    x, y = warte("Gefolgt")
    tx = seh.lesen()
    h = [b for t, a, b in tx if t.startswith("@") and b < y]
    hy = h[0] if h else y - 50
    # Kontoname über dem @-Namen antippen (öffnet „Konto wechseln“); Lage je nach Profil-Layout links oder mittig (20.11.2026)
    # nur links (rechts sitzt die Status-Blase „Was läuft?“ → würde einen Post öffnen, 20.11.2026)
    name = [(a, b) for t, a, b in tx if 8 < hy - b < 40 and len(t.strip()) > 3 and a < 230 and "läuft" not in t.lower()]
    tipp(*(name[0] if name else (45, hy - 24)), 2)


AKTUELL = {"konto": None}


def guthaben():
    """„Verfügbare Auszahlung“ (= zur Auszahlung bereit) auf der Auszahlungsübersicht ablesen → exporte/<konto>.guthaben.json.
    Nur lesen – „Abheben“ liegt direkt darunter und wird nie getippt."""
    import json, re
    _, y = warte("Verfügbare Auszahlung", 10)
    for t, a, b in seh.lesen():
        m = re.search(r"([\d.]+,\d{2})", t.replace(" ", ""))
        if m and y < b < y + 45:
            wert = float(m.group(1).replace(".", "").replace(",", "."))
            json.dump({"konto": AKTUELL["konto"], "bereit": wert, "stand": time.strftime("%Y-%m-%d %H:%M")},
                      open(EXP / f"{AKTUELL['konto']}.guthaben.json", "w"))
            print(f"{AKTUELL['konto']}: bereit {wert:.2f} €", flush=True)
            return wert
    raise Stopp("Betrag „Verfügbare Auszahlung“ nicht lesbar")


def praemien():
    """Einnahmen → Betrag „Verfügbare Auszahlung“ → Auszahlungsverlauf → Reiter „Belohnungen“: alle „+x,xx €“ summieren
    → praemien.json (Zeile je Konto ersetzt). Nur lesen; „Abheben“ liegt 40 Punkte unter dem Betrag und wird nie getippt."""
    import json, re
    x, y = warte("Verfügbare Auszahlung", 10)
    betrag = [(a, b) for t, a, b in seh.lesen() if "€" in t and y < b < y + 45]
    if not betrag:
        raise Stopp("Betrag „Verfügbare Auszahlung“ fehlt")
    tipp(betrag[0][0] + 25, betrag[0][1], 3)
    _, ty = warte("Täglicher Umsatz", 10)
    K.ziehe(250, ty, 60, ty, 0.4); time.sleep(1.5)       # Reiter nach links schieben, „Belohnungen“ steht dann rechts
    tipp(298, ty, 3)
    # Kopf der Seite: „2 Prämien  €135.01 verdient“ (darunter je Art: Aufgaben €130, Geldaufteilung €5.01) – keine Einträge
    # → „Noch keine Transaktionen“. Beträge mit Punkt als Komma.
    def eur(t):
        t = t.replace("€", "").replace(" ", "")
        t = t.replace(",", "") if "." in t else t.replace(".", "").replace(",", ".")
        return float(t)
    for _ in range(8):
        tx = seh.lesen()
        if seh.finde("Noch keine Transaktionen", tx):
            summe, arten = 0.0, []
            break
        kopf = next((t for t, _, _ in tx if "verdient" in t.lower()), None)
        if kopf:
            summe = eur(re.search(r"€\s?([\d.,]+)", kopf).group(1))
            arten = [(t, a, b) for t, a, b in tx if t.strip() in ("Aufgaben", "Geldaufteilung", "Boni", "Bonus", "Prämien")]
            break
        time.sleep(1)
    else:
        raise Stopp("Belohnungen nicht lesbar")
    gesehen = arten
    pf = HIER / "praemien.json"
    d = json.load(open(pf)) if pf.exists() else {"rows": [], "meta": []}
    d["rows"] = [r for r in d["rows"] if r["konto"] != AKTUELL["konto"]]
    d["rows"].append({"konto": AKTUELL["konto"], "art": "Belohnungen", "betrag": round(summe, 2), "bestellungen": len(gesehen),
                      "stand": time.strftime("%Y-%m-%d")})
    json.dump(d, open(pf, "w"), ensure_ascii=False)
    print(f"{AKTUELL['konto']}: Prämien {summe:.2f} € ({len(gesehen)} Einträge, letzte 3 Monate)", flush=True)


def nur_guthaben():
    tipp_text("TikTok Shop für Creator", w=5)
    for _ in range(3):
        rot = rot_popup(seh.lesen())
        if not rot:
            break
        tipp(*rot, 3); tipp(22, 58, 3)
    warte("Hallo", 15)
    y = None
    for _ in range(6):
        q = seh.finde("TikTok Sh", unter=110, ueber=520)
        if q:
            y = q[1]; break
        K.ziehe(167, 500, 167, 340, 0.4); time.sleep(2)
    if y is None:
        raise Stopp("Toolkit nicht gefunden")
    pf = [(a, b) for t, a, b in seh.lesen() if t.strip() in (">", "›") and a > 290 and abs(b - y) < 25]
    tipp(*(pf[0] if pf else (314, y)), 3)
    if not seh.finde("Meistbesucht"):
        tipp(314, y, 3)
    warte("Meistbesucht", 8)
    tipp_text("Einnahmen", w=4)
    guthaben()
    if PRAEMIEN:
        praemien()


PRAEMIEN = "--praemien" in sys.argv


def export():
    tipp_text("TikTok Shop für Creator", w=5)
    for _ in range(3):                # Werbe-Popup (Artur 20.11.: auf Rot tippen, dann zurück)
        tx = seh.lesen()
        rot = rot_popup(tx) or seh.finde("Aufgaben anzeigen", tx)
        if not rot:
            break
        tipp(*rot, 3); tipp(22, 58, 3)
    warte("Hallo", 15)
    y = None
    for _ in range(6):                # Toolkit in die Mitte holen (unten liegt „Jetzt erstellen“), Lage je Konto anders
        q = seh.finde("TikTok Sh", unter=110, ueber=520)
        if q:
            y = q[1]; break
        K.ziehe(167, 500, 167, 340, 0.4); time.sleep(2)
    if y is None:
        raise Stopp("Toolkit nicht gefunden")
    pf = [(a, b) for t, a, b in seh.lesen() if t.strip() in (">", "›") and a > 290 and abs(b - y) < 25]
    tipp(*(pf[0] if pf else (314, y)), 3)
    if not seh.finde("Meistbesucht"):
        tipp(314, y, 3)
    warte("Meistbesucht", 8)
    tipp_text("Einnahmen", w=4)
    guthaben()
    tipp_text("Partnerbestell", w=4)
    warte("Bestell-ID", 15)
    tipp(310, 56, 3)
    tipp_text("Bestätigen", w=4)
    warte("Datei ist bereit", 90)
    _, y = seh.finde("Datei ist bereit")
    vorher = set(glob.glob(str(DL / "affiliate_orders_*.xlsx")))
    tipp(308, y - 9, 5)
    _, y = warte("Anzeigen", 40)      # Safari: „Anzeigen  Laden“ (OCR oft als eine Zeile) → rechts „Laden“
    tipp(280, y, 4)
    tipp(91, 681, 2)                  # Safari-Menü (Adressleiste links)
    tipp_text("Downloads", w=2)
    tipp_text("affiliate_orders", w=4)
    tipp(301, 57, 3)                  # Teilen
    tipp_text("AirDrop", w=4)
    x, y = warte("von Andreas", 10)
    tipp(x, y - 40, 2)                # Mac-Symbol über „MacBook Pro von Andreas“
    for _ in range(30):
        neu = set(glob.glob(str(DL / "affiliate_orders_*.xlsx"))) - vorher
        if neu:
            break
        time.sleep(2)
    else:
        raise Stopp("AirDrop-Datei kam nicht an")
    # aufräumen: AirDrop zu, Teilen zu, Vorschau zu, Downloads zu
    tipp(301, 73, 1.2); tipp(167, 588, 1.2); tipp(33, 57, 1.2); tipp(39, 371, 1)
    return neu.pop()


def main(konten):
    EXP.mkdir(exist_ok=True)
    nur = "--guthaben" in konten or "--praemien" in konten
    konten = [k for k in konten if not k.startswith("--")]
    for k in konten:
        AKTUELL["konto"] = k
        try:
            tiktok_profil(); konto_wechseln(k)
            if nur:
                nur_guthaben(); continue
            f = export()
            time.sleep(1); shutil.move(f, EXP / f"{k}.xlsx")
            print(f"{k}: ok", flush=True)
        except Stopp as e:
            K.foto(f"/tmp/export-stopp-{k}.png")
            print(f"STOPP {k}: {e} (Foto /tmp/export-stopp-{k}.png)", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
