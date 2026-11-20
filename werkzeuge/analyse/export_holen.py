#!/usr/bin/env python3
"""Partnerbestellungen-Export eines Accounts holen (iPhone am Kabel, TikTok) und per AirDrop auf den Mac.
  python3 werkzeuge/analyse/export_holen.py konto1 [konto2 …]     (Export + Guthaben)
  python3 werkzeuge/analyse/export_holen.py --guthaben konto1 …   (nur „Verfügbare Auszahlung“ ablesen)
Ablauf: Profil → Konto wechseln → TikTok Shop für Creator*innen → Toolkit → Einnahmen → Partnerbestellungen →
Herunterladen → Bestätigen → Datei laden (Safari) → Downloads → Teilen → AirDrop „MacBook Pro von Andreas“.
Ergebnis: werkzeuge/analyse/exporte/<konto>.xlsx. Nie „Abheben“ tippen. Eine Zeile pro Konto, bei Problem STOPP."""
import os, sys, time, glob, shutil, pathlib
HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent))
import kabel as K, seh

EXP = HIER / "exporte"; DL = pathlib.Path.home() / "Downloads"
GEFAHR = ("abheben", "jetzt kaufen", "kasse")


class Stopp(Exception):
    pass


def tipp(x, y, w=1.5):
    K.tipp(x, y); time.sleep(w)


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
    for i in range(10):
        tx = seh.lesen()
        if seh.finde("Gefolgt", tx):
            return
        q = next((seh.finde(w, tx, genau=True) for w in POPUP if seh.finde(w, tx, genau=True)), None)
        rot = seh.finde("Poste", tx)
        if rot:                       # Werbe-Popup (Artur 20.11.: auf Rot tippen, dann zurück)
            tipp(*rot, 3); tipp(22, 58, 3)
        elif q:
            tipp(*q, 1.5)
        elif seh.finde("Exportverlauf", tx):
            tipp(310, 129, 1.5)       # Download-Blatt zu
        elif i >= 6 and not seh.finde("Wachstum", tx):
            tipp(299, 681, 2.5)       # Profil-Reiter
        else:
            tipp(22, 58, 2.5)         # zurück / X oben links
    warte("Gefolgt", 5)


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
    tipp(45, (h[0] if h else y - 50) - 24, 2)


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


def nur_guthaben():
    tipp_text("TikTok Shop für Creator", w=5)
    for _ in range(3):
        rot = seh.finde("Poste")
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


def export():
    tipp_text("TikTok Shop für Creator", w=5)
    for _ in range(3):                # Werbe-Popup (Artur 20.11.: auf Rot tippen, dann zurück)
        tx = seh.lesen()
        rot = seh.finde("Poste", tx) or seh.finde("Aufgaben anzeigen", tx)
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
    nur = "--guthaben" in konten
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
