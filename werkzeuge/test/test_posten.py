#!/usr/bin/env python3
"""Offline-Tests fürs Posten (post_mensch.py, bildschirm.py) – ohne iPhone, ohne Kabel (Artur 15.11.2026).

  python3 werkzeuge/test/test_posten.py          # alle Tests, Ausgabe ✓/✗ + Summe, Exit 1 bei Fehler

Grundlage: echte Bildschirmtexte (OCR) aus den Läufen 10.–15.11.2026 in test/bildschirme/faelle.json
(gebaut von test/bildschirme/faelle_bauen.py aus roh.json). Simulationen ersetzen lesen/tipp/ziehen durch ein
Bildschirm-Modell und prüfen: kommt an, tippt nie oben links im Feed/LIVE, nie auf LIVE-/System-Seiten.
"""
import json, pathlib, sys, time, traceback

H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent))
import bildschirm as B
import post_mensch as P
import kabel as _KB
import seh as _SEH


# 16.11.2026: Tests dürfen NIE das echte iPhone bedienen (Lehre aus dem Tempo-Versuch: Stopp-Fotos/Tipps aus Testläufen,
# während Artur steuerte). Alles, was nicht simuliert ist, bricht hier ab, statt ans Kabel zu gehen.
def _nie(*a, **k):
    raise RuntimeError("Test wollte das echte iPhone benutzen – gesperrt")


class _KeinIPhone:
    def __getattr__(self, n):
        _nie()


_KB._get = _KB._post = _nie
_SEH._KABEL = _KeinIPhone()

FAELLE = json.loads((H / "bildschirme" / "faelle.json").read_text())
ERG = {"ok": 0, "fehler": []}


def check(name, bed, info=""):
    if bed:
        ERG["ok"] += 1
    else:
        ERG["fehler"].append(f"{name} {info}")
        print(f"✗ {name} {info}")


def fall(anfang):
    f = next(f for f in FAELLE if f["datei"].startswith(anfang))
    return [tuple(t) for t in f["tx"]]


SYNTH = {   # Bildschirme ohne echtes Foto im Test-Set (Texte wie in TikTok)
    B.DLG_VERWERFEN: [("Video verwerfen?", 167, 330), ("Verwerfen", 167, 400), ("Abbrechen", 167, 450)],
    B.DLG_ZUSTIMMEN: [("Zustimmen und posten", 167, 600), ("Abbrechen", 167, 650)],
    B.LINK_BLATT: [("#superdeals", 52, 96), ("MORE 7ER FÜR 50€?!", 274, 135), ("Cover", 274, 186), ("bearbeiten", 274, 199),
                   ("# Hashtags", 51, 242), ("Link hinzufügen", 80, 373), ("Produkte und mehr. ›", 256, 373),
                   ("Link hinzufügen", 166, 563), ("Produkt", 76, 600), ("Veröffentliche ein Produkt in deinem Video", 151, 619),
                   ("LIVE Events", 85, 651), ("Veröffentliche einen Link in deinem LIVE", 144, 668)],   # echt, 15.11. 20:44
    B.DLG_OEFFNEN: [("In „TikTok“ öffnen?", 167, 330), ("Abbrechen", 110, 400), ("Öffnen", 225, 400)],
}


def beispiel(zustand):
    if zustand in SYNTH:
        return SYNTH[zustand]
    """Erster echter Bildschirm dieses Zustands (für Simulationen)."""
    for f in FAELLE:
        if f["soll"] == zustand and f["datei"][:8] >= "20261112":
            return [tuple(t) for t in f["tx"]]
    for f in FAELLE:
        if f["soll"] == zustand:
            return [tuple(t) for t in f["tx"]]
    return [("x", 100, 300)]


# ================================================================ 1) Bildschirm-Erkennung
def test_erkennung():
    falsch = []
    for f in FAELLE:
        ist = B.erkenne([tuple(t) for t in f["tx"]])
        if ist != f["soll"]:
            falsch.append((f["datei"][:15], f["soll"], ist))
    check("Erkennung: alle Fälle", not falsch, f"{len(falsch)} falsch: {falsch[:5]}")
    hand = [f for f in FAELLE if f["hand"]]
    check("Erkennung: Hand-geprüfte Fälle vorhanden", len(hand) >= 12, str(len(hand)))
    # kritische Einzelfälle
    check("LIVE-Auswahl erkannt", B.erkenne(fall("20261115-145557")) == B.LIVE)
    check("LIVE-Event-Bereich erkannt", B.erkenne(fall("20261112-164314")) == B.LIVE)
    check("Bewerben-Blatt ist kein LIVE", B.erkenne(fall("20261115-161703")) == B.BEWERBEN)
    check("Beitrag mit Tastatur", B.erkenne(fall("20261115-152413")) == B.BEITRAG)
    check("Gesamtlikes-Popup", B.erkenne(fall("20261115-175225")) == B.DLG_OK)
    check("Upload-läuft-Dialog", B.erkenne(fall("20261113-165602")) == B.DLG_UPLOAD)
    check("Produkt nicht verfügbar (Dialog)", B.erkenne(fall("20261113-232805")) == B.DLG_VERSTANDEN)
    check("Produktfotos Vollbild", B.erkenne(fall("20261113-013523")) == B.PRODUKT_BILDER)
    check("Home", B.erkenne(fall("20261115-175231")) == B.HOME)
    check("Spotlight", B.erkenne(fall("20261115-175245")) == B.SUCHE)
    check("Fotos „Zuletzt gesichert“", B.erkenne(fall("20261115-181304")) == B.FOTOS_ALBUM)
    check("Shop-Reiter = Feed (LIVE oben links)", B.erkenne(fall("20261115-154018")) == B.FEED)
    check("CAPTCHA-Wort", B.erkenne([("Ziehe den Schieberegler", 160, 400)]) == B.CAPTCHA)
    check("„Von TikTok verifiziert“ ist kein CAPTCHA",
          B.erkenne([("Von TikTok verifiziert", 160, 300), ("Kasse", 260, 680), ("Einkaufswagen", 90, 680)]) == B.PRODUKTSEITE)
    lb = [("Link hinzufügen", 80, 373), ("Link hinzufügen", 166, 563), ("Produkt", 76, 600),
          ("Veröffentliche ein Produkt in deinem Video", 151, 619), ("LIVE-Events", 85, 651),
          ("Veröffentliche einen Link in deinem LIVE", 144, 668)]
    check("Link-Blatt mit „LIVE-Events“ ist kein LIVE", B.erkenne(lb) == B.LINK_BLATT)
    lb2 = [("Link hinzufügen", 80, 417), ("Link hinzufügen", 166, 464), ("Produkt", 76, 501),
           ("Veröffentliche ein Produkt in deinem Video", 151, 519), ("LIVE gehen", 84, 553),
           ("Inspiriere andere, LIVE zu gehen, und erhalte ...", 161, 571), ("LIVE Events", 85, 601),
           ("Veröffentliche einen Link in deinem LIVE", 144, 619), ("Hol dir LIVE Studio", 106, 652)]   # echt 21:25
    check("Link-Blatt andreasfastlane (mit „LIVE gehen“) = Link-Blatt", B.erkenne(lb2) == B.LINK_BLATT)
    check("„LIVE gehen“ ist nicht zu nah an „Produkt“", not any(P._gefahr(t) and ((x - 76) ** 2 + (y - 501) ** 2) ** 0.5 < 38
                                                             for t, x, y in lb2))
    check("echte LIVE-Seite bleibt LIVE", B.erkenne([("LIVE gehen", 160, 600), ("Titel hinzufügen", 160, 200)]) == B.LIVE)
    check("Produktseite mit hochgezogenem Werbeblatt (Roxlin 21:27)", B.erkenne([("Roxlin GmbH", 104, 58),
          ("Bestseller-Nr.: 10", 58, 158), ("Verdiene 1 € pro Verkauf", 80, 177), ("Mehrere Einnahmequellen anzeigen", 100, 194),
          ("Einkaufswagen", 165, 673)]) == B.PRODUKTSEITE)
    check("„Exklusive Produktvorteile“ → Schließen", B.erkenne([("Exklusive Produktvorteile", 160, 300),
          ("Gutschein", 160, 360), ("Schließen", 167, 620), ("Kasse", 240, 680), ("Einkaufswagen", 90, 680)]) == B.DLG_SCHLIESSEN)
    check("Login → eigener Zustand", B.erkenne(fall("20261112-164038")) == B.LOGIN)


# ================================================================ 2) Sicherungen (reine Funktionen)
def test_sicherungen():
    # LIVE oben links
    check("_feed: Shop-Reiter", P._feed(fall("20261115-154018")))
    check("_feed: Feed „ÇIVE“", P._feed(fall("20261113-223254")))
    check("_feed: Beitrag nicht", not P._feed(fall("20261115-161902")))
    for t in ("LIVE", "_IVE", "ÇIVE", "LIV", "Live"):
        check(f"_gefahr {t}", P._gefahr(t))
    for t in ("Kasse", "Jetzt kaufen", "Konto hinzufügen", "LIVE gehen"):
        check(f"_gefahr {t}", P._gefahr(t))
    check("_gefahr Hinzufügen nein", not P._gefahr("Hinzufügen"))
    # OCR-Lesefehler beim Hook-Vergleich
    check("_passt kyrillisch З0", P._passt("30-TEILIGES BESTECK", "З0-TEILIGES BESTECK"))
    check("_passt ×", P._passt("2 PAAR HANDSCHUHE", "2 PAAR HANDSCHUHE ×"))
    check("_passt Emoji-Rest", P._passt("LIP PLUMPER FÜR 1,32€?! 😍", "LIP PLUMPER FÜR 1,32€?! ©"))
    check("_passt anderes Video nein", not P._passt("NIE MEHR KALTE FÜSSE", "46 TEILE FÜR 1,20€?!"))
    # Beschreibung: nur Hashtags, keine Marken, keine Preise
    d = {"datei": "Video 143 - 07 Nike Air Max Plus - V3.mp4", "brand": "KIX DE", "produkt": "NIKE GOLF Nike Air Max Plus",
         "hashtags": ["#nike", "#airmax", "#sneaker", "#tiktokshop"], "titel": "Air Max für unter 50 Euro"}
    t = P.beschreibung_text(d)
    # Artur 16.11.2026: kurzer simpler Text (klein, ohne Preis/Versprechen) + Hashtags
    vorn = t.split("#")[0].strip()
    check("Beschreibung: kurzer Text klein vorn, dann nur Hashtags", vorn and vorn == vorn.lower() and len(vorn.split()) <= 8
          and all(w.startswith("#") for w in t[len(vorn):].split()), t)
    d2 = dict(d, text="Nur 9,99€ heute!")
    check("Text mit Preis → Standardsatz", P.kurztext(d2) in P.KURZTEXTE)
    d3 = dict(d, text="Mega praktisch für die Küche 😍")
    check("Text klein, ohne Emoji", P.kurztext(d3) == "mega praktisch für die küche", P.kurztext(d3))
    check("Beschreibung ohne Marke", "nike" not in t.lower() and "airmax" not in t.lower(), t)
    check("Beschreibung Pflicht-Hashtags (bis 30.11.)", all(h in t for h in P.PFLICHT) or time.strftime("%m%d") > "1130", t)
    check("Beschreibung eigener Hashtag", "#sneaker" in t, t)
    d2 = dict(d, hashtags=["#redbull", "#energy"], brand="Red Bull", produkt="Red Bull Adventskalender",
              datei="Video 1 - 01 Red Bull Kalender - V1.mp4")
    check("Marke Red Bull raus", "redbull" not in P.beschreibung_text(d2).lower())
    for bad in ("Air Max für 49,99 €", "nur 1 Cent", "Bald vergriffen", "Deal des Jahres", "jetzt reduziert"):
        try:
            P.pruefe_verboten(bad, "Test"); ok = False
        except P.Sperre:
            ok = True
        check(f"Verboten: {bad}", ok)
    try:
        P.pruefe_verboten("#superdeals #livedeals #tiktokshopblackfriday #sneaker", "Test"); ok = True
    except P.Stopp:
        ok = False
    check("Erlaubt: nur Hashtags", ok)
    # Cover-Prüfung mit echten Beitragsseiten
    check("Cover passt (kyrillisch)", P.cover_passt(fall("20261115-170801"), "30-TEILIGES BESTECK")[0])
    check("Cover falsches Video", not P.cover_passt(fall("20261115-170801"), "NIE MEHR KALTE FÜSSE")[0])
    check("Cover Handschuhe", P.cover_passt(fall("20261114-004610"), "2 PAAR HANDSCHUHE 😍")[0])
    # Beschreibung am Bildschirm (Auto-Korrektur „Beklagte“, Produktname statt nur Hashtags)
    soll = "#lipplumper #tiktokshopblackfriday #superdeals #livedeals "
    P.lesen = lambda: fall("20261115-152413")
    check("Beschreibung „Beklagte …“ wird abgelehnt", not P.beschreibung_stimmt(soll))
    P.lesen = lambda: fall("20261115-165341")
    check("Beschreibung mit Produktname wird abgelehnt", not P.beschreibung_stimmt("#esn #tiktokshopblackfriday #superdeals #livedeals "))
    P.lesen = lambda: [("#superdeals #livedeals", 120, 80), ("#tiktokshopblackfriday", 100, 97), ("#heizdecke", 60, 113),
                       ("BEHEIZTE DECKE", 270, 140)]
    P.lesen = lambda: [("fivedeals #superdeals #tiktokshopblackfriday", 120, 96), ("#winterstiefel", 60, 112)]
    check("OCR „fivedeals“ = #livedeals wird angenommen",
          P.beschreibung_stimmt("#livedeals #superdeals #tiktokshopblackfriday #winterstiefel "))
    P.lesen = lambda: [("Beklagte Lip Plumper #lipplumper", 113, 96), ("#tiktokshopblackfriday", 84, 111),
                       ("#superdeals #livedeals", 83, 126)]
    check("„Lip“/„Plumper“ zählen nicht als Teil von #lipplumper", not P.beschreibung_stimmt(soll))
    P.lesen = lambda: [("#superdeals #livedeals #nike", 120, 96), ("#tiktokshopblackfriday", 84, 111)]
    check("fremder Marken-Hashtag wird abgelehnt", not P.beschreibung_stimmt("#superdeals #livedeals #tiktokshopblackfriday "))
    P.lesen = lambda: [("#superdeals #livedeals", 120, 80), ("#tiktokshopblackfriday", 100, 97), ("#heizdecke", 60, 113),
                       ("BEHEIZTE DECKE", 270, 140)]
    check("Beschreibung richtig wird angenommen", P.beschreibung_stimmt("#heizdecke #superdeals #livedeals #tiktokshopblackfriday "))
    # Produkt: nur oberstes, nie suchen
    hin, block = P.oberstes_produkt(fall("20261115-164350"))
    check("oberstes Showcase-Produkt gefunden", hin and abs(hin[0][2] - 239) < 3, str(hin and hin[0]))
    check("oberstes passt (Honig)", P.produkt_passt(block, "Energy & Vitalität Honigmischung für Männer"))
    check("oberstes passt nicht (Eiskratzer)", not P.produkt_passt(block, "LYVANAS Eiskratzer fürs Auto"))
    check("Umlaute egal (OCR Vitalitat)", P.produkt_passt("energy & vitalitat honig", "Vitalität Kapseln"))
    # Galerie-Kachel: Länge UND Hook
    g = fall("20261115-170640")
    check("Kachel Besteck (0:09)", P.galerie_kachel(g, "30-TEILIGES BESTECK", 9) is not None)
    check("Kachel Männer-Honig (0:33)", P.galerie_kachel(g, "MÄNNER-HONIG FÜR IHN", 33) is not None)
    k46 = P.galerie_kachel(g, "46 TEILE FÜR 1,20€?!", 18)
    check("Kachel 46 Teile = neueste (unten)", k46 and k46[1] > 240, str(k46))
    check("gleiche Länge, falscher Hook → keine Kachel", P.galerie_kachel(g, "EISKRATZER FÜRS AUTO", 18) is None)
    check("richtiger Hook, falsche Länge → keine Kachel", P.galerie_kachel(g, "30-TEILIGES BESTECK", 18) is None)
    # Fotos-Album: Sammel-Löschen findet nur Stapel-Videos
    al = fall("20261115-181304")
    tr = P.album_treffer(al, [("MORE 7ER FÜR 50€?! 😍", 10), ("TRAUM PULLOVER", 18), ("NICHT DA", 12)])
    check("Album: 2 Treffer", sorted(k for _, _, k in tr) == ["MORE 7ER FÜR 50€?! 😍", "TRAUM PULLOVER"], str(tr))
    check("Album: falsche Länge kein Treffer", not P.album_treffer(al, [("MORE 7ER FÜR 50€?!", 26)]))
    check("Album: Zähler lesen", P._ausgewaehlt([("3 Videos ausgewählt", 160, 60)]) == 3)
    # Umbenennen: richtiger Name trotz Auswahl-Griffen / Zähler
    P._BUTTON = "Geringer Bestand"
    check("Name ok (gelesen)", P.name_ok([("Produktname", 52, 307), ("0/30", 305, 306), ("Geringer Bestand", 61, 366)], 307))
    check("Name ok (Griffe mitgelesen)", P.name_ok([("Produktname", 52, 307), ("•Geringer Bestand|", 61, 366)], 307))
    check("Name ok (Zähler 16/30)", P.name_ok([("Produktname", 52, 307), ("16/30", 305, 306), ("Gerin", 61, 366)], 307, "Bellaré Lip Plumper"))
    P._BUTTON = "Bald vergriffen"
    check("Name ok trotz veralteter Lage (21:21 Belibuy)", P.name_ok([("Verdiene €2.08", 140, 248), ("Produktname", 52, 307),
                                                                     ("15/30", 305, 306), ("Bald vergriffen", 60, 366)], 200))
    P._BUTTON = "Geringer Bestand"
    check("Name falsch (alter Name)", not P.name_ok([("Produktname", 52, 307), ("WMF Aparto Topfset Induktion", 100, 366)], 307))
    check("Name falsch (doppelt)", not P.name_ok([("Produktname", 52, 307), ("Geringer BestandGeringer Bestand", 100, 366)], 307))
    # Produkt-Chip am Beitrag: umbenannt oder richtiges Produkt mit Originalnamen
    alt_l = P.lesen
    P.lesen = lambda: [("Link hinzufügen", 80, 373), ("Geringer Bestand X", 86, 405)]
    check("Chip umbenannt erkannt", P.produkt_am_beitrag(0, "WMF Aparto Topfset"))
    P.lesen = lambda: [("Link hinzufügen", 80, 373), ("WMF Aparto Topfs... X", 94, 405)]
    check("Chip richtiges Produkt (nicht umbenannt) zählt", P.produkt_am_beitrag(0, "WMF Aparto Topfset Induktion"))
    check("Chip fremdes Produkt zählt nicht", not P.produkt_am_beitrag(0, "Nivea Men Set"))
    P.lesen = alt_l
    # Konto-Pfeil: Lauf am Namen, nicht die Sprechblase rechts
    namen = [93, 101, 103, 111, 117, 131, 141, 143, 145, 151, 153, 163, 166]          # gemessen 15.11. (artur.official ▾)
    check("Pfeil ▾ am Namen", P.pfeil_x(namen, 93) == 163)
    check("Pfeil ▾: Sprechblase rechts zählt nicht", P.pfeil_x(namen + [250, 262, 280], 93) == 163)
    check("Pfeil ▾ ohne Treffer → Name+60", P.pfeil_x([], 93) == 153)
    # eingefrorenes Bild
    import datetime
    jetzt = datetime.datetime.now()
    uhr = f"{(jetzt.hour % 12) or 12}:{jetzt.minute:02d}"
    check("Uhr aktuell", P._bild_aktuell([(uhr, 42, 21)]))
    alt = jetzt - datetime.timedelta(minutes=7)
    check("Uhr 7 min alt = eingefroren", not P._bild_aktuell([(f"{(alt.hour % 12) or 12}:{alt.minute:02d}", 42, 21)]))

    class KAlt:
        def bild_alter(self): return 9000
    alt_k = P.seh.kabel
    P.seh.kabel = lambda: KAlt()
    check("Bild-Alter 9 s = eingefroren", P._eingefroren([(uhr, 42, 21)]))
    P.seh.kabel = alt_k
    # Zwischenablage gesperrt
    import kabel
    try:
        kabel.einfuegen("x"); ok = False
    except kabel.KabelFehler:
        ok = True
    check("Zwischenablage gesperrt", ok)
    # Tippen menschlich (Artur 16.11.2026: seine Geschwindigkeit ~9–10 Zeichen/s, kleine zufällige Pausen):
    # Wortstücke 2–6 Zeichen mit Tastenabstand 30–90 ms, nie der ganze Text in einem Befehl
    pausen = [kabel.tipp_pause(c) for c in "#tiktokshopblackfriday #superdeals #livedeals" * 20]
    check("Tippen: Pausen zwischen Stücken", min(pausen) >= 0.02 and 0.04 <= sum(pausen) / len(pausen) <= 0.2,
          f"Ø {sum(pausen)/len(pausen):.2f}")
    gesendet = []
    alt_aktion = kabel.aktion
    alt_sleep = kabel.time.sleep
    kabel.aktion = lambda op, **a: gesendet.append((a.get("keys"), a.get("pause")))
    kabel.time.sleep = lambda s: None
    txt = "#tiktokshopblackfriday #superdeals #livedeals"
    try:
        kabel.text(txt, menschlich=True)
    finally:
        kabel.aktion = alt_aktion; kabel.time.sleep = alt_sleep
    check("Tippen: Stücke 4–10 Zeichen, alle Zeichen, Tastenabstand 15–50 ms",
          sum(len(k) for k, _ in gesendet) == len(txt) and all(1 <= len(k) <= 10 for k, _ in gesendet)
          and len(gesendet) >= len(txt) // 10 and all(0.015 <= p <= 0.05 for _, p in gesendet), str(gesendet[:3]))
    check("Social1-Liste fest", P.SOCIAL1_LISTE == "6af5c87e84c1d2f55b052550")
    check("nicht vorrätig erkannt", P.nicht_vorraetig([("Der Artikel ist nicht vorrätig", 160, 640)]))
    check("vorrätig = nicht ausverkauft", not P.nicht_vorraetig([("Auf Lager", 160, 640), ("Kasse", 240, 680)]))
    check("Showcase voll erkannt", P.showcase_voll([("Dein Showcase ist voll", 160, 300)]))


# ================================================================ 3) Wiederaufnahme-Plan
def test_plan():
    def F(**kw):
        f = {"konto": True, "produkt": None, "beitrag": False, "cover": False, "text": False, "link": False,
             "ohne_link": False, "erstellen_offen": False}
        f.update(kw); return f
    f = F(produkt="showcase", beitrag=True, cover=True, text=True)
    check("Plan: Hänger in Showcase-Liste → weiter", P.naechster_schritt(f, B.SHOWCASE_LISTE) == "weiter" and f["text"])
    f = F(produkt="wagen", beitrag=True, cover=True)
    check("Plan: Beitrag → weiter", P.naechster_schritt(f, B.BEITRAG) == "weiter")
    f = F(produkt="showcase")
    check("Plan: Galerie → weiter", P.naechster_schritt(f, B.GALERIE) == "weiter")
    f = F(produkt="showcase", beitrag=True, cover=True, text=True)
    check("Plan: Beitrag verloren (Feed) → Hauptseite + neu ab „+“",
          P.naechster_schritt(f, B.FEED, True) == "hauptseite" and not f["beitrag"] and not f["text"] and f["produkt"] == "showcase")
    f = F(produkt="erstellen", beitrag=True, cover=True)
    check("Plan: „Jetzt erstellen“-Beitrag verloren → Produkt neu",
          P.naechster_schritt(f, B.HOME) == "hauptseite" and f["produkt"] is None)
    f = F(produkt="erstellen", erstellen_offen=True)
    check("Plan: Umbenennen im Erstellen-Weg → weiter", P.naechster_schritt(f, B.UMBENENNEN) == "weiter")
    f = F(produkt="erstellen", erstellen_offen=True)
    check("Plan: Erstellen-Weg verloren (Feed) → Produkt neu über Social1",
          P.naechster_schritt(f, B.FEED, True) == "hauptseite" and f["produkt"] is None and not f["erstellen_offen"])
    f = F()
    check("Plan: Produktseite ohne Produkt-Schritt → weiter", P.naechster_schritt(f, B.PRODUKTSEITE) == "weiter")
    f = F(produkt="showcase")
    check("Plan: LIVE → Hauptseite", P.naechster_schritt(f, B.LIVE) == "hauptseite")


# ================================================================ 4) Simulationen (Zustandsmaschinen)
class Sim:
    """Bildschirm-Modell: Zustand → echter OCR-Bildschirm; Aktionen schalten nach UEBERGANG weiter."""

    def __init__(self, start, uebergang, tabs=(B.FEED, B.PROFIL, B.TIKTOK), bilder=None):
        self.z = start; self.ue = uebergang; self.tabs_bei = tabs; self.log = []; self.bilder = bilder or {}

    def tx(self):
        return self.bilder.get(self.z) or beispiel(self.z if self.z != B.TIKTOK else B.PROFIL)

    def gehe(self, art):
        self.log.append((self.z, art))
        n = self.ue.get((self.z, art), self.ue.get((self.z, "*")))
        if n:
            self.z = n

    # Ersatz für post_mensch-Funktionen
    def tipp(self, x, y, tx=None, was="", **kw):
        if x < 70 and y < 110 and self.z in (B.FEED, B.LIVE, B.TIKTOK):
            raise AssertionError(f"Tipp oben links auf {self.z} ({was})")
        if self.z in (B.LIVE, B.SYSTEM):
            raise AssertionError(f"Tipp auf {self.z} ({was})")
        self.gehe("tipp:" + (was or "").split(" (")[0])

    def ziehe(self, x1, y1, x2, y2, dauer=0.3):
        self.gehe("wisch" if x1 < 10 else ("runter" if y2 > y1 else "hoch"))

    def taste(self, k):
        self.gehe("taste:" + k)

    def app(self, name, erzwingen=False):
        self.gehe("app:" + name)


def mit_sim(sim, fn, *a, **kw):
    alt = {n: getattr(P, n) for n in ("lesen", "_tabs", "tipp", "K", "app", "ruhe", "neu_laden_tippen")}
    alt_sleep = P.time.sleep
    try:
        P.lesen = sim.tx
        P._tabs = lambda tx=None: sim.z in sim.tabs_bei
        P.tipp = sim.tipp
        P.K = lambda: sim
        P.app = sim.app
        P.ruhe = lambda *x, **y: None
        P.neu_laden_tippen = lambda tx: (sim.gehe("tipp:Neu laden") or True)
        P.time.sleep = lambda s: None
        return fn(*a, **kw)
    finally:
        for n, v in alt.items():
            setattr(P, n, v)
        P.time.sleep = alt_sleep


HAUPT = {
    (B.BEITRAG, "tipp:Zurück"): B.EDITOR, (B.EDITOR, "tipp:Zurück"): B.DLG_VERWERFEN,
    (B.DLG_VERWERFEN, "tipp:Verwerfen"): B.TIKTOK, (B.LIVE, "wisch"): B.FEED, (B.LIVE, "runter"): B.FEED,
    (B.SHOWCASE_LISTE, "tipp:Zurück"): B.BEITRAG, (B.WAGEN_LISTE, "tipp:Zurück"): B.BEITRAG,
    (B.UMBENENNEN, "tipp:Zurück"): B.SHOWCASE_LISTE, (B.PRODUKTSEITE, "tipp:Produktseite zu"): B.TIKTOK,
    (B.BEWERBEN, "tipp:Blatt zu"): B.PRODUKTSEITE, (B.WERBE_BLATT, "runter"): B.PRODUKTSEITE,
    (B.VARIANTEN, "runter"): B.PRODUKTSEITE, (B.KAMERA, "tipp:Kamera zu"): B.TIKTOK,
    (B.GALERIE, "tipp:Galerie zu"): B.KAMERA, (B.HOME, "app:TikTok"): B.TIKTOK, (B.SAFARI_SOCIAL1, "app:TikTok"): B.TIKTOK,
    (B.DLG_OK, "tipp:OK"): B.PROFIL, (B.SYSTEM, "taste:home"): B.HOME, (B.SUCHE, "taste:home"): B.HOME,
    (B.UNBEKANNT, "wisch"): B.TIKTOK, (B.PRODUKT_BILDER, "runter"): B.PRODUKTSEITE,
    (B.DLG_VERSTANDEN, "tipp:OK, verstanden"): B.PRODUKTSEITE, (B.FOTOS_VOLLBILD, "app:TikTok"): B.TIKTOK,
    (B.TEILEN, "runter"): B.FOTOS_VOLLBILD, (B.KONTO_WECHSELN, "runter"): B.PROFIL, (B.VORSCHAU, "tipp:Zurück"): B.GALERIE,
    (B.NICHT_VERFUEGBAR, "wisch"): B.TIKTOK, (B.LINK_BLATT, "tipp:Link-Blatt zu"): B.BEITRAG, (B.TIKTOK_SONST, "wisch"): B.PROFIL, (B.DLG_UPLOAD, "tipp:Bestätigen"): B.PROFIL,
}


def test_hauptseite():
    for start in (B.BEITRAG, B.LIVE, B.UMBENENNEN, B.BEWERBEN, B.GALERIE, B.HOME, B.SYSTEM, B.DLG_OK, B.PRODUKT_BILDER,
                  B.UNBEKANNT, B.WERBE_BLATT, B.VARIANTEN, B.DLG_VERSTANDEN, B.TEILEN, B.KONTO_WECHSELN, B.SUCHE,
                  B.TIKTOK_SONST, B.DLG_UPLOAD, B.NICHT_VERFUEGBAR, B.LINK_BLATT):
        sim = Sim(start, HAUPT)
        try:
            mit_sim(sim, P.zur_hauptseite)
            check(f"Hauptseite von „{start}“", sim.z in (B.FEED, B.PROFIL, B.TIKTOK), str(sim.log))
        except Exception as e:
            check(f"Hauptseite von „{start}“", False, f"{e} {sim.log[-4:]}")
    # hängender Bildschirm (reagiert auf nichts) → nach 3× App neu, dann klappt es
    sim = Sim(B.UNBEKANNT, {(B.UNBEKANNT, "app:TikTok"): B.TIKTOK})
    try:
        mit_sim(sim, P.zur_hauptseite)
        check("Hauptseite: hängender Bildschirm → App neu", sim.z == B.TIKTOK, str(sim.log))
    except Exception as e:
        check("Hauptseite: hängender Bildschirm → App neu", False, str(e))
    # Produktseite: Wisch blättert nur das Produktbild, „TikTok neu“ landet wieder dort → nur X oben links hilft
    sim = Sim(B.PRODUKTSEITE, {(B.PRODUKTSEITE, "tipp:Produktseite zu"): B.TIKTOK}, bilder={B.PRODUKTSEITE: fall("20261113-092128")})
    try:
        mit_sim(sim, P.zur_hauptseite)
        check("Produktseite: X oben links, kein Wisch, kein App-Neustart", sim.z == B.TIKTOK and
              not any(a in ("wisch", "app:TikTok") for _, a in sim.log), str(sim.log))
    except Exception as e:
        check("Produktseite: X oben links", False, f"{e} {sim.log}")
    # Produktblatt über dem Shop-Reiter (LIVE oben links) → nur runterwischen, nie X oben links
    sim = Sim(B.PRODUKTSEITE, {(B.PRODUKTSEITE, "runter"): B.TIKTOK}, bilder={B.PRODUKTSEITE: fall("20261115-145050")})
    try:
        mit_sim(sim, P.zur_hauptseite)
        check("Produktblatt über Shop: runterwischen, kein Tipp", sim.z == B.TIKTOK and
              not any(a.startswith("tipp") for _, a in sim.log), str(sim.log))
    except Exception as e:
        check("Produktblatt über Shop", False, f"{e} {sim.log}")
    # Login → harter STOPP
    sim = Sim(B.LOGIN, {})
    try:
        mit_sim(sim, P.zur_hauptseite); ok = False
    except P.Hart:
        ok = True
    check("Login → Hart", ok)
    # LIVE nie antippen (Sim wirft bei Tipp auf LIVE)
    sim = Sim(B.LIVE, {(B.LIVE, "wisch"): B.LIVE, (B.LIVE, "runter"): B.LIVE, (B.LIVE, "app:TikTok"): B.TIKTOK})
    try:
        mit_sim(sim, P.zur_hauptseite)
        check("LIVE bleibt hängen → kein Tipp, App neu", sim.z == B.TIKTOK and not any(a.startswith("tipp") for _, a in sim.log),
              str(sim.log))
    except Exception as e:
        check("LIVE bleibt hängen → kein Tipp, App neu", False, str(e))


def test_zum_beitrag():
    P._SOLL_DAUER = 9
    bilder = {B.GALERIE: fall("20261115-170640"), B.BEITRAG: fall("20261115-170801"), B.VORSCHAU: fall("20261113-162733"),
              B.EDITOR: fall("20261115-163957"), B.KAMERA: fall("20261115-161755")}
    ue = {(B.TIKTOK, "tipp:+"): B.KAMERA, (B.KAMERA, "tipp:Galerie unten links"): B.DLG_OK, (B.DLG_OK, "tipp:OK"): B.GALERIE,
          (B.GALERIE, "tipp:Video-Kachel"): B.VORSCHAU, (B.VORSCHAU, "tipp:Auswählen"): B.VORSCHAU,
          (B.VORSCHAU, "tipp:Weiter"): B.EDITOR, (B.EDITOR, "tipp:Weiter"): B.BEITRAG}
    sim = Sim(B.TIKTOK, ue, bilder=bilder)
    try:
        mit_sim(sim, P.zum_beitrag, "30-TEILIGES BESTECK")
        check("zum_beitrag: + → Kamera → (Popup) → Galerie → Vorschau → Editor → Beitrag", sim.z == B.BEITRAG, str(sim.log))
    except Exception as e:
        check("zum_beitrag Durchlauf", False, f"{e} {sim.log}")
    # Fortsetzen mitten in der Galerie (nach Hänger)
    sim = Sim(B.GALERIE, ue, bilder=bilder)
    try:
        mit_sim(sim, P.zum_beitrag, "30-TEILIGES BESTECK")
        check("zum_beitrag: Fortsetzen in der Galerie", sim.z == B.BEITRAG and sim.log[0][0] == B.GALERIE, str(sim.log))
    except Exception as e:
        check("zum_beitrag Fortsetzen", False, f"{e} {sim.log}")
    # falsches Video nie antippen: Hook fehlt → Sperre nach Wartezeit, kein Kachel-Tipp
    sim = Sim(B.GALERIE, ue, bilder=bilder)
    try:
        mit_sim(sim, P.zum_beitrag, "EISKRATZER FÜRS AUTO", None, 0)
        ok = False
    except P.Sperre:
        ok = not any(a == "tipp:Video-Kachel" for _, a in sim.log)
    except Exception as e:
        ok = False; print(e)
    check("zum_beitrag: Video nicht da → Sperre, keine Kachel getippt", ok, str(sim.log))
    P._SOLL_DAUER = None


# ================================================================ 5) Ablauf eines Videos mit eingebauten Hängern
class Ablauf:
    """Ersetzt die Schritt-Funktionen; fehler = {schritt: [Ausnahme, …]} wird der Reihe nach geworfen."""

    def __init__(self, fehler=None, schirm=B.BEITRAG):
        self.fehler = fehler or {}; self.aufrufe = []; self.schirm = schirm; self.entwurf = None; self.neu = 0

    def schritt(self, name, rueck=None):
        def f(*a, **kw):
            self.aufrufe.append(name)
            if self.fehler.get(name):
                raise self.fehler[name].pop(0)
            return rueck
        return f


def mit_ablauf(ab, d, entwurf=False):
    namen = ("konto", "zum_produkt", "showcase_oder_wagen", "zum_beitrag", "cover_pruefen", "beschreiben", "verlinken",
             "schluss_pruefung", "abschluss", "lage", "zur_hauptseite", "zurueck_zum_beitrag", "erstellen_route",
             "aufraeumen", "schreibe", "eintragen", "lesen", "log", "lade", "warenkorb_leeren", "in_wagen")
    alt = {n: getattr(P, n) for n in namen}
    alt_run, alt_k, alt_sleep = P.subprocess.run, P.seh.kabel, P.time.sleep
    try:
        P.konto = ab.schritt("konto")
        P.zum_produkt = ab.schritt("zum_produkt", [("pro Verkauf", 100, 500)])
        P.showcase_oder_wagen = ab.schritt("showcase", "showcase")
        P.zum_beitrag = ab.schritt("zum_beitrag")
        P.cover_pruefen = ab.schritt("cover")
        P.beschreiben = ab.schritt("beschreiben")
        P.verlinken = ab.schritt("verlinken")
        P.schluss_pruefung = ab.schritt("schluss")
        P.erstellen_route = ab.schritt("erstellen")
        P.zurueck_zum_beitrag = ab.schritt("zurueck_zum_beitrag")
        P.warenkorb_leeren = ab.schritt("leeren")
        P.in_wagen = ab.schritt("in_wagen")

        def abschluss(e):
            ab.aufrufe.append("abschluss"); ab.entwurf = e
        P.abschluss = abschluss
        P.lage = lambda tx=None: (ab.schirm, [], ab.schirm in (B.FEED, B.PROFIL, B.TIKTOK))
        P.zur_hauptseite = ab.schritt("hauptseite")
        P.aufraeumen = lambda *a, **k: None
        P.schreibe = lambda *a, **k: None
        P.eintragen = lambda *a, **k: None
        P.lesen = lambda: [("pro Verkauf", 100, 500)]
        P.log = lambda m: None
        P.subprocess.run = lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "NEU"})()

        class K:
            def neu_verbinden(s): ab.neu += 1
        P.seh.kabel = lambda: K()
        P.time.sleep = lambda x: None
        P._konto = None
        return P.ein_video(pathlib.Path("/dev/null"), d, entwurf=entwurf, aufr=False)
    finally:
        for n, v in alt.items():
            setattr(P, n, v)
        P.subprocess.run, P.seh.kabel, P.time.sleep = alt_run, alt_k, alt_sleep


def test_ablauf():
    d = {"datei": "Video 143 - 26 Garnier Hair Food - V2.mp4", "account": "artur.official", "produkt": "Garnier Fructis",
         "tts_link": "https://shop/1729", "kachel": "2 MASKEN FÜR 1,20€?! 😍", "button": "Wenige verfügbar",
         "hashtags": ["#haarmaske"], "stapel": "test"}
    ab = Ablauf()
    mit_ablauf(ab, d)
    check("Weg 1/2: Showcase/Wagen + Verlinken", ab.aufrufe == ["konto", "zum_produkt", "showcase", "hauptseite", "zum_beitrag",
                                                               "cover", "beschreiben", "verlinken", "schluss", "abschluss"],
          str(ab.aufrufe))
    # Artur 17.11.: Hänger beim Verlinken → Beitrag verwerfen, Video einmal komplett neu (nicht am Bildschirm weiter)
    ab = Ablauf({"verlinken": [P.Stopp("Verlinken kam nicht weiter (60 s)")]}, schirm=B.SHOWCASE_LISTE)
    mit_ablauf(ab, d)
    check("Hänger Verlinken: Beitrag verwerfen + Video neu", ab.aufrufe.count("verlinken") == 2 and ab.aufrufe.count("beschreiben") == 2
          and ab.aufrufe.count("zum_produkt") == 2 and ab.entwurf is False and ab.aufrufe[-1] == "abschluss", str(ab.aufrufe))
    # Artur 21:10: oberstes Listen-Produkt passt nicht → Beitrag verwerfen, Produkt neu, „Jetzt erstellen“
    ab = Ablauf({"verlinken": [P.ListeFalsch("oberstes Produkt passt nicht")]}, schirm=B.SHOWCASE_LISTE)
    mit_ablauf(ab, d)
    check("Liste falsch → Jetzt erstellen (nicht leeren)", "erstellen" in ab.aufrufe and "leeren" not in ab.aufrufe
          and ab.aufrufe.count("zum_produkt") == 2 and ab.aufrufe.count("verlinken") == 1 and ab.entwurf is False,
          str(ab.aufrufe))
    # Beitrag verloren (Feed) → Video komplett neu (Artur 17.11.)
    ab = Ablauf({"beschreiben": [P.Stopp("Beschreibungsfeld nicht gefunden")]}, schirm=B.FEED)
    mit_ablauf(ab, d)
    check("Beitrag verloren: Video komplett neu", ab.aufrufe.count("zum_beitrag") == 2 and ab.aufrufe.count("zum_produkt") == 2
          and ab.aufrufe.count("cover") == 2, str(ab.aufrufe))
    # Produkt beim Verlinken nicht verfügbar → Entwurf ohne Link
    ab = Ablauf({"verlinken": [P.Entwurf("nicht vorrätig → Entwurf")]})
    mit_ablauf(ab, d)
    check("Entwurf: zurück zum Beitrag + als Entwurf", "zurueck_zum_beitrag" in ab.aufrufe and ab.entwurf is True, str(ab.aufrufe))
    ab = Ablauf({"zum_produkt": [P.Entwurf("Produkt nicht verfügbar")]}, schirm=B.NICHT_VERFUEGBAR)
    mit_ablauf(ab, d)
    check("Produkt weg: Entwurf ohne Link", ab.entwurf is True and "verlinken" not in ab.aufrufe, str(ab.aufrufe))
    # Sperre (falsches Cover) → sofort raus, nie veröffentlichen
    ab = Ablauf({"cover": [P.Sperre("Cover zeigt nicht …")]})
    try:
        mit_ablauf(ab, d); ok = False
    except P.Sperre:
        ok = "abschluss" not in ab.aufrufe and ab.aufrufe.count("cover") == 1
    check("Sperre: kein zweiter Versuch, nicht gepostet", ok, str(ab.aufrufe))
    import kabel
    ab = Ablauf({"zum_beitrag": [kabel.KabelFehler("drag: Connection was terminated abruptly.")]}, schirm=B.TIKTOK)
    mit_ablauf(ab, d)
    check("Kabel-Abriss: Server neu + weiter", ab.neu == 1 and ab.entwurf is False, str(ab.aufrufe))
    ab = Ablauf({"verlinken": [P.Stopp("x")] * 20}, schirm=B.BEITRAG)
    try:
        mit_ablauf(ab, d); ok = False
    except P.Stopp as e:
        ok = "2. Versuch" in str(e) and "abschluss" not in ab.aufrufe and ab.aufrufe.count("verlinken") == 2
    check("Dauer-Hänger: nach 2. Versuch Fehler, nicht gepostet (keine Schleife)", ok, str(ab.aufrufe))
    # Artur 17.11.: Verbindungswechsel (Kabel ab / WLAN↔USB) mitten im Post → Verbindungswechsel → Beitrag neu
    class KW:
        WECHSEL = 0
        art = "Connected over USB"
        def steuerung_art(s): return s.art
    kw = KW(); alt_k = P.seh.kabel; P.seh.kabel = lambda: kw
    try:
        P.verbindung_merken(); kw.WECHSEL = 1
        try:
            P.verbindung_pruefen(); ok1 = False
        except P.Verbindungswechsel:
            ok1 = True
        P.verbindung_merken(); kw.art = "Connected over Wi-Fi"; P._VB["zuletzt"] = 0
        try:
            P.verbindung_pruefen(); ok2 = False
        except P.Verbindungswechsel:
            ok2 = True
        P.verbindung_merken(False); kw.WECHSEL = 5
        P.verbindung_pruefen(); ok3 = True                       # außerhalb eines Posts: nichts
    finally:
        P.seh.kabel = alt_k; P._VB["aktiv"] = False
    check("Verbindungswechsel: Zähler + WLAN↔USB erkannt, außerhalb Post still", ok1 and ok2 and ok3)
    # 17.11.: neue Auswahl-Ansicht „Ausgewählt 1“ + „Weiter (1)“ (Foto unbekannt-133429.png, 147-24)
    tx = [('1:34', 47, 17), ('Ausgewahlt', 289, 65), ('Doppelklick', 188, 650), ('PUTARE SCROLL-RING +', 40, 680),
          ('00:29', 49, 711), ('AutoCut', 106, 755), ('Weiter (1)', 276, 755)]
    ok = P.auswahl_weiter(tx, 'PUTARE SCROLL-RING 😍', 29.17) == (276, 755) \
        and P.auswahl_weiter(tx, 'UNO NO MERCY FÜR 1 CENT 😍', 29.17) is None and P.auswahl_weiter(tx, 'PUTARE SCROLL-RING 😍', 12) is None
    try:
        P.auswahl_weiter([x if x[0] != 'Weiter (1)' else ('Weiter (2)', 276, 755) for x in tx], 'PUTARE SCROLL-RING 😍', 29.17); ok = False
    except P.Sperre:
        pass
    check("Auswahl-Ansicht: Weiter (1) nur bei Hook + Länge, 2 gewählt = Sperre, nie AutoCut", ok)
    # Weg 4: Neukunden-Hinweis auch nach dem Leeren (More 7er, 21:05) → „Jetzt erstellen“, kein Verlinken über Listen
    ab = Ablauf()
    alt_schritt = Ablauf.schritt

    def schritt2(self, name, rueck=None):
        if name in ("showcase", "in_wagen"):
            def sw(tx=None):
                self.aufrufe.append(name); P._NEUKUNDE = True; return "wagen"
            return sw
        return alt_schritt(self, name, rueck)
    Ablauf.schritt = schritt2
    try:
        mit_ablauf(ab, d)
    finally:
        Ablauf.schritt = alt_schritt
    check("Neukunden-Hinweis → direkt Jetzt erstellen (nicht leeren)", "leeren" not in ab.aufrufe and "erstellen" in ab.aufrufe
          and "verlinken" not in ab.aufrufe and ab.entwurf is False, str(ab.aufrufe))
    # Preis im Produktnamen → Sperre vor allem anderen
    ab = Ablauf()
    try:
        mit_ablauf(ab, dict(d, button="Nur 9,99 €")); ok = False
    except P.Sperre:
        ok = ab.aufrufe == []
    check("Produktname mit Preis → Sperre, nichts getippt", ok)


def test_hauptschleife():
    """main(): Sperre → nächstes Video; 3 Fehler hintereinander → STOPP; Hart → STOPP."""
    import eingang as EG
    liste = [(pathlib.Path(f"/dev/null"), {"datei": f"V{i}.mp4", "account": "anduri.official", "status": "freigegeben",
                                          "stapel": "t", "kachel": f"K{i}"}) for i in range(5)]
    def lauf(verhalten):
        alt = {n: getattr(P, n) for n in ("ein_video", "airdrop_einmal", "dauer_text", "icloud_holen", "schreibe",
                                          "zur_hauptseite", "fotos_aufraeumen", "log")}
        alt_alle, alt_run = EG.alle, P.subprocess.run
        gemacht = []
        try:
            EG.alle = lambda: iter(liste)
            def ev(p, d, e, a):
                gemacht.append(d["datei"]); v = verhalten.get(d["datei"])
                if v:
                    raise v
                return 60
            P.ein_video = ev
            P.airdrop_einmal = lambda d: None
            P.dauer_text = lambda v: 10
            P.icloud_holen = lambda p: True
            P.schreibe = lambda *a: None
            P.zur_hauptseite = lambda **k: None
            P.fotos_aufraeumen = lambda v: None
            P.log = lambda m: None
            P.subprocess.run = lambda *a, **k: None
            try:
                P.main(["--stapel", "t", "--ohne-airdrop"]); code = 0
            except SystemExit as e:
                code = str(e.code)
            return gemacht, code
        finally:
            for n, v in alt.items():
                setattr(P, n, v)
            EG.alle, P.subprocess.run = alt_alle, alt_run
    g, c = lauf({"V1.mp4": P.Sperre("Cover falsch")})
    check("Hauptschleife: Sperre → weiter mit allen", g == [f"V{i}.mp4" for i in range(5)] and c == 0, f"{g} {c}")
    g, c = lauf({"V0.mp4": P.Stopp("a"), "V1.mp4": P.Stopp("b"), "V2.mp4": P.Stopp("c")})
    check("Hauptschleife: 3 Fehler hintereinander → STOPP", g == ["V0.mp4", "V1.mp4", "V2.mp4"] and "hintereinander" in str(c), f"{g} {c}")
    g, c = lauf({"V0.mp4": P.Stopp("a"), "V2.mp4": P.Stopp("c")})
    check("Hauptschleife: einzelne Fehler → weiter", len(g) == 5 and c == 0, f"{g} {c}")
    g, c = lauf({"V1.mp4": P.Hart("Showcase voll")})
    check("Hauptschleife: Hart → sofort STOPP", g == ["V0.mp4", "V1.mp4"] and "Showcase voll" in str(c), f"{g} {c}")
    import kabel
    g, c = lauf({"V1.mp4": kabel.KabelFehler("x")})
    check("Hauptschleife: fremde Ausnahme stürzt nicht ab", len(g) == 5 and c == 0, f"{g} {c}")


def test_erstellen_weg():
    """Artur 15.11.2026: Zum Showcase hinzufügen → Jetzt erstellen (nie „Mehr erkunden“) → Videos → Kamera."""
    w1 = [("Informationen zur Werbeaktion", 160, 120), ("Verdiene 1,31 € pro Verkauf", 150, 160),
          ("Zum Showcase hinzufügen", 165, 670)]
    w2 = [("Informationen zur Werbeaktion", 160, 120), ("Mehr erkunden", 156, 669)]
    w3 = [("Informationen zur Werbeaktion", 160, 120), ("Jetzt erstellen", 165, 670)]
    bilder = {"w1": w1, "w2": w2, "w3": w3, B.BEWERBEN: fall("20261115-161703"), B.KAMERA: fall("20261115-161755"),
              B.PRODUKTSEITE: fall("20261115-161633")}
    ue = {("w1", "tipp:Zum Showcase hinzufügen"): "w2", ("w2", "runter"): B.PRODUKTSEITE,
          (B.PRODUKTSEITE, "tipp:pro Verkauf"): "w3", ("w3", "tipp:Jetzt erstellen"): B.BEWERBEN,
          (B.BEWERBEN, "tipp:Videos"): B.KAMERA}
    sim = Sim("w1", ue, bilder=bilder)
    try:
        mit_sim(sim, P.erstellen_route)
        taps = [a for _, a in sim.log]
        check("Erstellen-Weg: Showcase → „Mehr erkunden“ NIE antippen → pro Verkauf neu → Jetzt erstellen → Videos → Kamera",
              sim.z == B.KAMERA and "tipp:Zum Showcase hinzufügen" in taps and "tipp:Jetzt erstellen" in taps
              and not any("Mehr erkunden" in t for t in taps), str(sim.log))
    except Exception as e:
        check("Erstellen-Weg", False, f"{e} {sim.log}")
    sim = Sim("w1", ue, bilder=bilder)
    try:
        mit_sim(sim, P.erstellen_route, True); ok = False
    except P.Entwurf:
        ok = [a for _, a in sim.log] == ["tipp:Zum Showcase hinzufügen"]
    check("Erstellen-Weg ausverkauft: nur Showcase, dann Entwurf", ok, str(sim.log))


def test_szenarien():
    """Artur 16.11.2026 – drei Bildschirmaufnahmen (Showcase neu / schon im Showcase → Einkaufswagen / Neukunden →
    „Jetzt erstellen“)."""
    # --- Neukunden-Hinweis: nur der echte Hinweis, nicht die normalen „Neukund“-Texte
    check("Neukunden-Hinweis (Pukka, echt) erkannt", P.neukunde_hinweis(fall("20261113-000003")))
    check("„Neukunden-Angebot“ auf Produktseite ≠ Hinweis", not P.neukunde_hinweis(fall("20261115-153737")))
    check("„Funde für Neukund*innen“ (Shop-Reiter) ≠ Hinweis", not P.neukunde_hinweis(fall("20261110-180548")))
    check("„Angebot für Neukund*innen“ in der Liste ≠ Hinweis", not P.neukunde_hinweis(fall("20261115-164350")))
    seite = fall("20261115-153737")
    toast = seite + [("Zum Einkaufswagen hinzugefügt", 167, 360)]
    check("Wagen-Ergebnis: Toast → ok", P.wagen_ergebnis(toast) == "ok")
    check("Wagen-Ergebnis: Neukunden → neukunde", P.wagen_ergebnis(fall("20261113-000003")) == "neukunde")
    check("Wagen-Ergebnis: nichts → None", P.wagen_ergebnis(seite) is None)

    # --- Einkaufswagen ohne Varianten: graues „Einkaufswagen“ genau EINMAL antippen
    def wagen_lauf(nachher):
        bilder = [seite, nachher, nachher, nachher]
        taps = []
        alt = {n: getattr(P, n) for n in ("lesen", "tipp", "ruhe", "log")}
        alt_sleep = P.time.sleep
        try:
            P.lesen = lambda: bilder.pop(0) if len(bilder) > 1 else bilder[0]
            P.tipp = lambda x, y, tx=None, was="", **k: taps.append(was)
            P.ruhe = lambda *a, **k: None
            P.log = lambda m: None
            P.time.sleep = lambda s: None
            P._NEUKUNDE = False
            P.in_wagen(seite)
            return taps, P._NEUKUNDE
        finally:
            for n, v in alt.items():
                setattr(P, n, v)
            P.time.sleep = alt_sleep
    taps, nk = wagen_lauf(toast)
    check("Szenario 2: Wagen-Knopf nur 1× (Toast)", taps == ["Einkaufswagen (grau)"] and not nk, str(taps))
    taps, nk = wagen_lauf(fall("20261113-000003"))
    check("Szenario 3: Neukunden-Hinweis → Jetzt-erstellen-Weg, 1 Tipp", taps == ["Einkaufswagen (grau)"] and nk, str(taps))
    taps, nk = wagen_lauf(seite)
    check("Kein Hinweis gelesen → nicht nochmal tippen", taps == ["Einkaufswagen (grau)"] and not nk, str(taps))
    P._NEUKUNDE = False

    # --- Showcase-Liste: erst entscheiden, wenn sie fertig geladen und ruhig ist (Szenario 1: kurz alte Reihenfolge)
    def zeile(name, y):
        return [(name, 210, y - 60), ("Verdiene 0,04 €", 150, y - 5), ("Hinzufügen", 266, y)]
    laedt = [("Wird geladen...", 167, 59), ("Q Produkte suchen", 75, 96), ("Dein Showcase", 72, 140)] \
        + zeile("NIKE GOLF Nike Air Max Plus TN Sneaker...", 239) + zeile("More Nutrition 7er-Bundle", 347)
    fertig = [("Produktlinks hinzufügen", 166, 52), ("Aus dem Showcase", 165, 65), ("Q Produkte suchen", 75, 96),
              ("Dein Showcase", 72, 140)] + zeile("Automotive Handheld Oil Flmr Cream", 239) + zeile("NIKE GOLF Nike Air", 347)
    check("Liste lädt erkannt", P.liste_laedt(laedt) and not P.liste_laedt(fertig))

    def link_lauf(bilder, weg, produkt):
        taps = []
        alt = {n: getattr(P, n) for n in ("lesen", "tipp", "ruhe", "log", "nach_hinzufuegen", "neu_laden_tippen")}
        alt_sleep = P.time.sleep
        try:
            P.lesen = lambda: bilder.pop(0) if len(bilder) > 1 else bilder[0]
            P.tipp = lambda x, y, tx=None, was="", **k: taps.append((was, round(y)))
            P.ruhe = lambda *a, **k: None
            P.log = lambda m: None
            P.nach_hinzufuegen = lambda w: taps.append(("fertig", 0))
            P.neu_laden_tippen = lambda tx: False
            P.time.sleep = lambda s: None
            P.verlinken(weg, produkt)
        except Exception as e:
            taps.append((type(e).__name__, 0))
        finally:
            for n, v in alt.items():
                setattr(P, n, v)
            P.time.sleep = alt_sleep
        return taps
    taps = link_lauf([laedt, laedt, fertig, fertig, fertig], "showcase", "Automotive Handheld Oil Flmr Cream")
    check("Szenario 1: wartet aufs fertige Showcase, nimmt das neue Produkt oben",
          taps == [("Hinzufügen", 239), ("fertig", 0)], str(taps))
    # Nike-Produkt: während des Ladens stünde ein ALTES Nike oben – darf nicht genommen werden
    taps = link_lauf([laedt, laedt, laedt, fertig, fertig], "showcase", "Nike Air Max Plus TN")
    check("Szenario 1: kein Tipp auf altes Produkt während „Wird geladen“", ("Hinzufügen", 239) not in taps[:1]
          or taps[0] != ("Hinzufügen", 239), str(taps))

    # --- Szenario 2: Blatt „Hinzufügen von“ → nur „Einkaufswagen“, nie die verdeckte „Weitere Produkte“-Zeile
    blatt = [("Produktlinks hinzufügen", 166, 52), ("Dein Showcase", 72, 140), ("Hinzufügen von", 167, 507),
             ("Kooperationen", 80, 556), ("Produkt-Marktplatz", 90, 598), (": Einkaufswagen", 76, 639),
             ("Gekaufte Produkte", 88, 685)]
    wagen = [("Einkaufswagen", 167, 52), ("Q Produkte suchen", 75, 101),
             ("Hast du interessante Produkte in TikTok gefunden?", 140, 140),
             ("Lege sie in den Einkaufswagen und bewerbe sie später. Mehr erfahren", 150, 170),
             ("ESN Vitamin D3+K2 Daily Tabletten 300er-Pack", 200, 221), ("Gratismuster", 150, 240),
             ("Verdiene 0,79 €", 150, 290), ("Hinzufüg...", 280, 303)]
    taps = link_lauf([blatt, wagen, wagen, wagen], "wagen", "ESN Vitamin D3+K2 Daily Tabletten")
    check("Szenario 2: „Hinzufügen von“ → Einkaufswagen → oberstes Produkt",
          [w for w, _ in taps] == ["Einkaufswagen (Liste)", "Hinzufügen", "fertig"], str(taps))

    # --- Szenario 3: X am „Wie möchtest du …“-Blatt folgt dem Titel; Produktname-Zeile lesen
    check("Bewerben-X oben (Titel 121 → 87)", round(P.bewerben_x_y(fall("20261115-161703"))) == 87)
    tief = [("Wie möchtest du Produkte", 167, 445), ("bewerben?", 167, 462), ("Videos", 118, 590)]
    check("Bewerben-X tief (nach Entwurf, Titel 445 → 411)", P.bewerben_x_y(tief) == 411)
    um = [("Produkt umbenennen", 167, 57), ("Produktname", 50, 307), ("30/30", 315, 307),
          ("Der Produktname wird im Video angezeigt. Bei weniger als 20", 160, 322),
          ("Zeichen wird er möglicherweise besser dargestellt.", 150, 334), ("Sf3500 Retro-Handheld-Spielkon", 100, 366)]
    alt_b = P._BUTTON
    P._BUTTON = "Wenige verfügbar"
    um16 = [("Produkt umbenennen", 167, 57), ("Produktname", 50, 307), ("16/30", 315, 307), ("E1 Max Schrauber", 80, 366)]
    neu16 = [("Produkt umbenennen", 167, 57), ("Produktname", 50, 307), ("16/30", 315, 307), ("Wenige verfügbar", 80, 366)]
    kaputt = [("Produkt umbenennen", 167, 57), ("Produktname", 50, 307), ("16/30", 315, 307), ("Wenge verfgbar|", 80, 366)]
    check("Fanttik 17:31: alter Name mit gleicher Länge ≠ umbenannt", not P.name_ok(um16, 307, "E1 Max Schrauber"))
    check("Neuer Name erkannt", P.name_ok(neu16, 307, "E1 Max Schrauber"))
    check("Zähler hilft nur, wenn Feld sich geändert hat", P.name_ok(kaputt, 307, "E1 Max Schrauber")
          and not P.name_ok(kaputt, 307, None) is None)
    P._BUTTON = alt_b
    pop = [("Exklusiver Gutschein", 167, 300), ("5 € Rabatt", 167, 350), ("Jetzt anfordern", 167, 520)]
    check("Popup „Jetzt anfordern“ erkannt", B.erkenne(pop + seite) == B.DLG_ANFORDERN)
    check("X unter „Jetzt anfordern“ (ohne gelesenes X: 60 darunter)", P.anfordern_x(pop, (167, 520)) == (167, 580))
    check("X unter „Jetzt anfordern“ (gelesenes ×)", P.anfordern_x(pop + [("×", 168, 575)], (167, 520)) == (168, 575))
    tast = um + [(c, 20 + i * 30, 600) for i, c in enumerate("qwertzuiop")] + [("123", 30, 700)]
    check("Tastatur offen erkannt", P.tastatur_offen(tast) and not P.tastatur_offen(um))
    sc = [("Entdecken", 128, 53), ("Verwalten", 208, 53), ("Games Console", 90, 92), ("Suchen", 290, 92),
          ("Produkt-Rangliste", 45, 172), ("Für dich empfohlen", 80, 447), ("Super Deals", 80, 481)]
    check("Showcase-Seite „Entdecken | Verwalten“ ≠ Feed", B.erkenne(sc) == B.SHOWCASE_SEITE and not B.feed_oben(sc)
          and not P._feed(sc))
    check("Feed mit „Entdecken“ bleibt Feed", B.feed_oben([("Entdecken", 100, 60), ("Für dich", 250, 60)]))
    widget = [("What Live do you want to watch?", 145, 63), ("following Live", 86, 109), ("trending Live", 84, 158),
              ("recommend Live", 97, 207), ("Shoptester1107", 94, 256), ("Mail", 52, 366), ("Notizen", 128, 366),
              ("Erinnerungen", 205, 366), ("Uhr", 281, 366), ("TV", 52, 448), ("Spiele", 128, 448), ("App Store", 205, 448),
              ("a Suchen", 166, 606)]
    check("Home mit TikTok-Widget „What Live …“ = Home, nicht LIVE", B.erkenne(widget) == B.HOME)
    check("echte LIVE-Auswahl ohne Home bleibt LIVE", B.erkenne(widget[:5]) == B.LIVE)
    check("Produktname-Zeile gelesen", P.feldzeile(um, 307) == "Sf3500 Retro-Handheld-Spielkon", P.feldzeile(um, 307))


def test_tempo_16_11():
    """16.11.2026 abends (Tempo ohne Hänger): Varianten-Wahl, AirDrop-Merkliste, Hook-Toleranz, Social1-Liste."""
    # Varianten: Tatort-artig („Fall:“ mit Bildern, „Menge:“ + Hinweis darunter) → Bildkacheln ÜBER Menge/Hinweis
    syn = [("Tatort Escape Adventskalender", 150, 300), ("Fall:", 30, 470), ("Menge:", 41, 600), ("1", 273, 600),
           ("+", 305, 600), ("Der Artikel ist nicht vorrätig", 167, 634), ("Einkaufswagen", 167, 673)]
    gr, opt = P.varianten_optionen(syn)
    check("Varianten: Gruppe „Fall:“, nicht „Menge:“", gr == (30, 470), gr)
    check("Varianten: Bildkacheln über „Menge“", opt and all(o[2] < 590 for o in opt), opt)
    check("Varianten-Blatt mit „Menge:“ + „Fall:“ erkannt", B.erkenne(syn) == B.VARIANTEN, B.erkenne(syn))
    syn_ohne_knopf = [t for t in syn if t[0] != "Einkaufswagen"] + [("In den Warenkorb", 167, 673)]
    check("Varianten-Blatt auch ohne Knopf „Einkaufswagen“", B.erkenne(syn_ohne_knopf) == B.VARIANTEN, B.erkenne(syn_ohne_knopf))
    syn2 = [("Farbe: Schwarz", 50, 420), ("Schwarz", 50, 455), ("Weiß", 120, 455), ("Größe", 30, 520), ("S", 40, 560),
            ("M", 90, 560), ("Menge:", 41, 610), ("+", 305, 610), ("-", 230, 610), ("Der Artikel ist nicht vorrätig", 167, 640),
            ("Einkaufswagen", 167, 673)]
    gr, opt = P.varianten_optionen(syn2)
    check("Varianten: nie „+“/„-“/Menge/Hinweis", [o[0] for o in opt] == ["S", "M"], opt)
    gr, opt = P.varianten_optionen(syn2, {(40, 560), (90, 560)})
    check("Varianten: alle Texte probiert → keine blinden Bildtipps", opt == [], opt)
    for f in FAELLE:
        if f["soll"] == B.VARIANTEN and any("vorrätig" in t[0] for t in f["tx"]):
            gr, opt = P.varianten_optionen([tuple(t) for t in f["tx"]])
            check(f"Varianten echt {f['datei'][:15]}: Optionen über dem Hinweis",
                  opt and all(o[2] < 625 and o[0] not in ("Einkaufswagen", "+") for o in opt), opt)
    pr = fall("20261113-011840")                                  # Produktseite mit „nicht vorrätig“ + Kasse ≠ Varianten
    check("Produktseite mit Hinweis bleibt Produktseite", B.erkenne(pr) == B.PRODUKTSEITE, B.erkenne(pr))
    # AirDrop-Merkliste: Ankunft gesehen ≠ nur angeklickt
    import tempfile
    t = pathlib.Path(tempfile.mkdtemp()) / "a.txt"
    check("AirDrop: keine Merkliste → nicht da", not P.airdrop_schon_da("x.mp4", t))
    t.write_text("Video 1 - 04 A - V1.mp4\n")
    check("AirDrop: Zeile genau", P.airdrop_schon_da("Video 1 - 04 A - V1.mp4", t)
          and not P.airdrop_schon_da("Video 1 - 04 A - V1", t))
    # Hook-Toleranz kurze Hooks (genau 1 Buchstabe), fremde Hooks nie
    check("Hook kurz: 1 Lesefehler ok", P._passt("EISTEE?! 😍", "EISTEF?!"))
    check("Hook kurz: anderer Hook nein", not P._passt("EISTEE?! 😍", "MILKA?!") and not P._passt("TATORT 😍", "TOTARS"))
    check("Hook lang: fremd nein", not P._passt("PURELEI ARMBAND -50%?! 😍", "PURELEI FÜR DIE HÄLFTE?!"))
    ok, _c = P.cover_passt([("8ESTES", 270, 120), ("GESCHENK FUR", 270, 135), ("ELTERN", 270, 150)], "BESTES GESCHENK FÜR ELTERN 😍")
    check("Cover: Hook über 3 Zeilen", ok)
    ok, _c = P.cover_passt([("PURELEI", 270, 120), ("ARMBAND", 270, 135)], "BESTES GESCHENK FÜR ELTERN 😍")
    check("Cover: fremder Hook über 2 Zeilen nein", not ok)
    # Social1-Liste: JSON-Feld > Link > neueste Liste mit dem Produkt > Standard
    check("Liste aus JSON", P.liste_fuer({"social1_liste": "abc"}) == "abc")
    check("Liste aus social1_link", P.liste_fuer({"social1_link": "https://www.social1.ai/saved-videos/6afb1c70204ef09999b79488"})
          == "6afb1c70204ef09999b79488")
    if (P.AUS / "social1-bof.json").exists():
        check("Liste per Produkt (Tatort → bof)", P.liste_fuer({"tts_link": "https://shop.tiktok.com/view/product/1729954254982650611"})
              == "6afb1c70204ef09999b79488", P.liste_fuer({"tts_link": "https://shop.tiktok.com/view/product/1729954254982650611"}))
    check("Liste unbekanntes Produkt → Standard", P.liste_fuer({"tts_link": "x/1"}) == P.SOCIAL1_LISTE)


def main():
    for t in (test_erkennung, test_sicherungen, test_plan, test_hauptseite, test_zum_beitrag, test_ablauf, test_hauptschleife, test_erstellen_weg, test_szenarien,
              test_tempo_16_11):
        try:
            t()
        except Exception:
            ERG["fehler"].append(f"{t.__name__}: Absturz")
            traceback.print_exc()
    n = ERG["ok"] + len(ERG["fehler"])
    print(f"\n{ERG['ok']}/{n} Tests grün" + ("" if not ERG["fehler"] else f" – {len(ERG['fehler'])} rot"))
    sys.exit(1 if ERG["fehler"] else 0)


if __name__ == "__main__":
    main()
