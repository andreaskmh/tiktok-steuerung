#!/usr/bin/env python3
"""Bildschirm-Erkennung fürs Posten (post_mensch.py) – reine Funktion, offline testbar (Artur 15.11.2026: „einwandfrei
laufendes System“). Eingabe = OCR-Liste [(text, x, y)] in Punkten 334×735 (seh.lesen), optional Pixel-Merkmale.

  erkenne(tx, tabs=None) -> Name des Bildschirms (Konstante unten)

Reihenfolge der Regeln = Vorrang: Gefahr/CAPTCHA vor Dialogen vor Blättern vor ganzen Seiten. Ein Dialog liegt über der
Seite darunter und muss zuerst weg, darum gewinnt er. Test-Set: werkzeuge/test/bildschirme/faelle.json
(python3 werkzeuge/test/test_bildschirm.py).
"""
import re

# ---------------------------------------------------------------- Bildschirme
CAPTCHA = "captcha"
LIVE = "live"                        # LIVE-Seite / LIVE-Event geöffnet (versehentlich) → nur Wisch zurück
DLG_BEDINGUNGEN = "dlg_bedingungen"  # 18.11.: „Nur noch ein Schritt zum Bewerben der Produkte von <Shop>“ (Shop-AGB)
                                     # → nie selbst „Hinzufügen“ (Zustimmung = Artur), melden + warten
LIVE_WAHL = "live_wahl"              # 18.11.: System-Blatt „What Live do you want to watch?“ (TikTok-Kurzbefehl WatchLive)
                                     # → nur oben über dem Blatt tippen (Statusleiste), nie eine Zeile
DLG_VERSTANDEN = "dlg_verstanden"    # „OK, verstanden“ (Produkt nicht verfügbar / nicht hinzugefügt)
DLG_ZUM_VIDEO = "dlg_zum_video"      # „Produkt zum Video hinzufügen?“ → Hinzufügen
DLG_VERWERFEN = "dlg_verwerfen"      # „Verwerfen“ / „Neu beginnen“ (Beitrag abbrechen)
DLG_UPLOAD = "dlg_upload"            # „momentan ein Video …“ (Kontowechsel während Upload) → Bestätigen
DLG_ZUSTIMMEN = "dlg_zustimmen"      # „… zustimmen und posten“
DLG_OK = "dlg_ok"                    # Info-Popup mit „OK“ (Gesamtlikes, Kamera-Hinweis …)
DLG_ANFORDERN = "dlg_anfordern"      # Gutschein-/Angebots-Popup „Jetzt anfordern“ → transparentes X darunter (Artur 16.11.)
DLG_SCHLIESSEN = "dlg_schliessen"    # Info-Popup mit „Schließen“ (z. B. „Exklusive Produktvorteile“) → Schließen
DLG_ERLAUBEN = "dlg_erlauben"        # „Nicht erlauben“ (Mitteilungen/Kontakte)
DLG_OEFFNEN = "dlg_oeffnen"          # Safari: „In TikTok öffnen?“ / Banner „ÖFFNEN“
LADEFEHLER = "ladefehler"            # „Erneut versuchen“ …
HOME = "home"                        # iPhone-Home (Suchen unten)
SAFARI_SOCIAL1 = "safari_social1"    # social1.ai/products/… mit „View on TikTok Shop“
SAFARI = "safari"                    # Safari sonst (Social1 lädt, andere Seite)
FOTOS_MEDIATHEK = "fotos_mediathek"
FOTOS_ALBUM = "fotos_album"          # „Zuletzt gesichert“ o. ä. Album / Auswählen
FOTOS_VOLLBILD = "fotos_vollbild"
UMBENENNEN = "umbenennen"            # „Produkt umbenennen“ (Hinzufügen rot unten)
BEWERBEN = "bewerben"                # Blatt „Wie möchtest du Produkte bewerben?“ (Lade ein Video hoch / LIVE gehen)
WERBE_BLATT = "werbe_blatt"          # Blatt „Informationen zur Werbeaktion“ / „Zum Showcase hinzufügen“ / „Jetzt erstellen“
VARIANTEN = "varianten"              # Varianten-Blatt (Bitte auswählen / rotes Einkaufswagen unten)
NICHT_VERFUEGBAR = "nicht_verfuegbar"  # Produkt-/Artikel nicht verfügbar (Seite)
PRODUKTSEITE = "produktseite"        # TikTok-Shop-Produkt (Kasse + Einkaufswagen unten)
SHOWCASE_LISTE = "showcase_liste"    # Link → Produkt → „Dein Showcase“
WAGEN_LISTE = "wagen_liste"          # Link → Produkt → Einkaufswagen-Reiter („Produkte suchen“)
LINK_BLATT = "link_blatt"            # „Link hinzufügen“-Blatt mit „Produkt“
BEITRAG = "beitrag"                  # Beitragsseite (Veröffentlichen + Entwürfe unten)
EDITOR = "editor"                    # Video-Editor (Weiter rechts unten, AutoCut/Story links)
VORSCHAU = "vorschau"                # Galerie-Vorschau mit „Auswählen“
GALERIE = "galerie"                  # TikTok-Galerie (Kacheln mit Dauer)
KAMERA = "kamera"                    # TikTok-Kamera („Sound hinzufügen“)
KONTO_WECHSELN = "konto_wechseln"
PROFIL = "profil"
SHOWCASE_SEITE = "showcase_seite"    # Showcase-Seite „Entdecken | Verwalten“ (nach „Zum Showcase hinzufügen“) → Zurück-Pfeil
FEED = "feed"                        # Startseite (Für dich …) – oben links LIVE!
TIKTOK = "tiktok"                    # TikTok-Hauptseite mit Leiste, sonst unklar (nur Pixel)
TIKTOK_SONST = "tiktok_sonst"        # TikTok-Unterseite ohne Aufgabe (Bestellung, Profilaufrufe, Warenkorb, Entwürfe) → Wisch zurück
PRODUKT_BILDER = "produkt_bilder"    # Produktfotos im Vollbild („1/7“) → nach unten wischen
SUCHE = "suche"                      # Spotlight-Suche (Toptreffer / Siri-Vorschläge)
SYSTEM = "system"                    # Mitteilungszentrale, Kontrollzentrum, Einstellungen → nie tippen, Home
OFFLINE = "offline"                  # kein Internet (Safari-Fehlerseite) → warten
LOGIN = "login"                      # TikTok ausgeloggt / Registrieren → harter STOPP (Artur)
TEILEN = "teilen"                    # iOS-Teilen-Blatt → nach unten wegwischen
LADEN = "laden"                      # „Wird geladen …“ → warten
UNBEKANNT = "unbekannt"

ALLE = [v for k, v in dict(globals()).items() if k.isupper() and isinstance(v, str) and k != "ALLE"]


def _t(tx):
    return [(t.strip(), x, y) for t, x, y in tx]


def hat(tx, muster, genau=False, unter=None, ueber=None, links=None, rechts=None):
    """Erster Treffer (x, y) oder None. unter/ueber = y-Grenzen (y > unter, y < ueber) wie seh.finde."""
    m = muster.lower()
    for t, x, y in tx:
        s = t.lower().strip()
        if (s == m if genau else m in s) and (unter is None or y > unter) and (ueber is None or y < ueber) \
           and (links is None or x < links) and (rechts is None or x > rechts):
            return x, y
    return None


CAPTCHA_WORTE = ("puzzle", "schieberegler", "captcha", "verifizier", "ziehe den", "drag the slider", "sicherheitsüberprüfung",
                 "bestätige, dass du", "bist du ein mensch", "füge das puzzle", "wähle alle")


def captcha_wort(tx):
    alles = " ".join(t.lower() for t, _, _ in tx)
    alles = re.sub(r"verifiziert\w*", "", alles)        # „Von TikTok verifiziert“ (Shop-Abzeichen) ist kein CAPTCHA
    alles = re.sub(r"spiele\s*(&|und)\s*puzzles?|puzzles?\s*(&|und)\s*\w+|bestseller[^,]{0,40}|\w*puzzles\b", "", alles)
    # 17.11.2026 (147-25 UNO): Kategorie „Bestseller-Nr. 3 · Spiele & Puzzles“ ist kein CAPTCHA
    return next((w for w in CAPTCHA_WORTE if w in alles), None)


DAUER = re.compile(r"\d{1,2}:\d{2}")


def dauer_text(t):
    """„~00:09“, „•00:13“, „-00:13“ (OCR liest Schatten/Punkt mit) → „00:09“; sonst None."""
    t = t.strip().lstrip("~•·-–—$| ").strip()
    if len(t) == 6 and t[0] in "1lI|!" and t[1:3] == "00" and t[3] == ":":   # 17.11.2026 (147-13): „100:29“ = Zeichen
        t = t[1:]                                                # vor „00:29“ mitgelesen (Kachel nie erkannt)
    return t if DAUER.fullmatch(t) else None


def dauern(tx):
    """Galerie-Kacheln: Dauer-Labels „0:18“ im Raster (nicht die Uhr oben links), Vorzeichen-Lesefehler bereinigt."""
    return [(dauer_text(t), x, y) for t, x, y in tx if 120 < y < 650 and dauer_text(t)]


FEED_WORTE = ("für dich", "gefolgt", "in der nähe", "entdecken", "freund*innen", "following")


def showcase_seite(tx):
    """16.11.2026 (artur.official, nach „Zum Showcase hinzufügen“): Seite mit Reitern „Entdecken | Verwalten“ oben und
    Zurück-Pfeil oben links – KEIN Feed (dort steht kein LIVE)."""
    return bool(hat(_t(tx), "Verwalten", genau=True, ueber=110) and hat(_t(tx), "Entdecken", genau=True, ueber=110))


def home_bildschirm(tx):
    """iPhone-Home: „Suchen“ unten + mind. 3 bekannte App-Namen."""
    return suchen_unten(tx) and sum(bool(hat(tx, a, genau=True)) for a in (
        "FaceTime", "Kalender", "Kamera", "Uhr", "Karten", "App Store", "Wetter", "Einstellungen", "Mail", "Notizen",
        "Erinnerungen", "TV", "Spiele", "Health", "Wallet", "News", "Fotos")) >= 3


def feed_oben(tx):
    """Startseite/Freunde/Shop-Reiter: oben links liegt LIVE → dort nie tippen."""
    if showcase_seite(tx):
        return False
    return any(f in t.lower() for t, _, y in tx if y < 110 for f in FEED_WORTE)


def suchen_unten(tx):
    return any(re.fullmatch(r"(\W|[qa]\.?)?\s*suchen", t.lower().strip()) and y > 550 for t, _, y in tx)


def fotos_datum_oben(tx):
    """Fotos-Vollbild: oben „Heute“/„Gestern“/Datum, darunter Uhrzeit „5:53 PM“."""
    tag = any(re.fullmatch(r"(heute|gestern|\d{1,2}\. \w+\.?( \d{4})?|\w+tag)", t.lower().strip()) and 30 < y < 80 for t, _, y in tx)
    zeit = any(re.fullmatch(r"\d{1,2}:\d{2}(\s?(am|pm))?", t.lower().strip()) and 40 < y < 90 for t, _, y in tx)
    return tag and zeit


def bilderzaehler(tx):
    return any(re.fullmatch(r"\d{1,2}/\d{1,2}", t.strip()) for t, _, _ in tx)


def shop_bedingungen(tx):
    """Reine Funktion: Blatt „Nur noch ein Schritt zum Bewerben der Produkte von …“ (Zustimmung zu den
    Geschäftsbedingungen eines Shops) offen. 18.11.2026 (148-35 Maybelline)."""
    tx = _t(tx)
    return bool(hat(tx, "Schritt zum Bewerben") or hat(tx, "Nur noch ein Schritt")
                or (hat(tx, "Geschäftsbedingungen") and hat(tx, "einverstanden")))


def live_wahl(tx):
    """Reine Funktion: Auswahl-Blatt „What Live do you want to watch?“ (following/trending/recommend Live) offen."""
    tx = _t(tx)
    return bool(hat(tx, "what live do you want") or (hat(tx, "following Live") and hat(tx, "trending Live"))
                or (hat(tx, "trending Live") and hat(tx, "recommend Live")))


def erkenne(tx, tabs=None):
    """→ Bildschirm-Name. tabs = TikTok-Leiste mit „+“ (Pixel türkis/pink) erkannt (None = unbekannt)."""
    tx = _t(tx)
    if captcha_wort(tx):
        return CAPTCHA
    # ---- 18.11.2026 (Artur): System-Blatt des TikTok-Kurzbefehls „WatchLive“ (liegt über JEDER App, auch über Home,
    # bleibt nach Home-Taste stehen) → eigener Bildschirm mit Vorrang, Rückweg = über dem Blatt tippen, nie eine Zeile
    if live_wahl(tx):
        return LIVE_WAHL
    if shop_bedingungen(tx):                                     # vor „verstanden“: „…einverstanden.“ steht im Text
        return DLG_BEDINGUNGEN
    # ---- Dialoge (liegen über allem)
    if hat(tx, "verstanden"):
        return DLG_VERSTANDEN
    if hat(tx, "zum Video hinzufügen") or (hat(tx, "zum Video") and hat(tx, "Hinzufügen", genau=True)):
        return DLG_ZUM_VIDEO
    if hat(tx, "momentan ein Video"):
        return DLG_UPLOAD
    if hat(tx, "Verwerfen", genau=True) or hat(tx, "Neu beginnen", genau=True) or hat(tx, "Video verwerfen") \
       or hat(tx, "Bearbeitungen verwerfen"):
        return DLG_VERWERFEN
    if hat(tx, "zustimmen") and not hat(tx, "Produkt umbenennen"):
        return DLG_ZUSTIMMEN
    if hat(tx, "Nicht erlauben", genau=True):
        return DLG_ERLAUBEN
    if hat(tx, "Jetzt anfordern"):
        return DLG_ANFORDERN                                     # Artur 16.11.2026: nie „anfordern“, nur das X darunter
    if hat(tx, "Schließen", genau=True) and not hat(tx, "LIVE gehen") and not hat(tx, "Veröffentlichen", unter=600):
        return DLG_SCHLIESSEN                                    # Artur 15.11. 21:38: „Exklusive Produktvorteile“
    if hat(tx, "In „TikTok“ öffnen") or hat(tx, "in TikTok öffnen") or (hat(tx, "Öffnen", genau=True) and hat(tx, "Abbrechen", genau=True)):
        return DLG_OEFFNEN
    ok = hat(tx, "OK", genau=True)
    if ok and (hat(tx, "Gesamtlikes") or 250 < ok[1] < 700) and not hat(tx, "Veröffentlichen", unter=600):
        return DLG_OK
    # ---- Link-Blatt („Produkt“ / „LIVE Events“ bzw. „LIVE-Events“) ist KEINE LIVE-Seite (15.11. 21:24 andreasfastlane)
    # andreasfastlane: zusätzlich „LIVE gehen“ + „Hol dir LIVE Studio“ im Blatt → trotzdem Link-Blatt (nur „Produkt“ tippen,
    # Abstandsschutz zu „LIVE gehen“ bleibt in post_mensch.tipp)
    if hat(tx, "Produkt", genau=True) and hat(tx, "Link hinzufügen") and hat(tx, "Veröffentliche ein Produkt"):
        return LINK_BLATT
    # ---- Gefahr: LIVE-Seite
    if hat(tx, "LIVE gehen") and not hat(tx, "bewerben?") and not hat(tx, "Lade ein Video hoch"):
        return LIVE
    if hat(tx, "LIVE-Event") or hat(tx, "Event erstellen") or hat(tx, "Event-Bereich") or hat(tx, "Deine Events") \
       or hat(tx, "nächstes LIVE") or hat(tx, "LIVE-Aufnahme beenden") or hat(tx, "LIVE beenden"):
        return LIVE
    if hat(tx, "hat dem LIVE") and not home_bildschirm(tx):
        return LIVE                                              # 16.11.: TikTok-Widget „What Live …“ auf dem Home-Bildschirm
                                                                 # ist keine LIVE-Seite (getippt wird dort nur unten „Suchen“)
    if hat(tx, "Bei TikTok registrieren") or hat(tx, "Bei TikTok anmelden") or hat(tx, "Melde dich bei TikTok an"):
        return LOGIN
    # ---- System (nie etwas antippen)
    if hat(tx, "Mitteilungszentrale") or (hat(tx, "Flugmodus") and hat(tx, "WLAN")) or hat(tx, "SIM fehlt") \
       or (hat(tx, "Fokus") and len(tx) <= 8) or hat(tx, "Bedienungshilfen", ueber=120):
        return SYSTEM
    if hat(tx, "nicht mit dem Internet") or hat(tx, "Keine Internetverbindung") or hat(tx, "Kein Netzwerk"):
        return OFFLINE
    if hat(tx, "Toptreffer") or hat(tx, "Siri-Vorschläge"):
        return SUCHE
    if home_bildschirm(tx):
        return HOME
    # ---- Fotos (vor TikTok: Fotos-Raster hat auch Dauer-Labels)
    if (hat(tx, "ausgewählt") or hat(tx, "ausgewahlt")) and hat(tx, "Optionen"):
        return TEILEN                                            # Teilen-Blatt („3 Videos ausgewählt, Optionen ›“)
    if hat(tx, "Zuletzt gesichert") and (hat(tx, "Objekte") or hat(tx, "Auswählen") or hat(tx, "Auswahlen")):
        return FOTOS_ALBUM
    if hat(tx, "Mediathek", unter=650) and hat(tx, "Sammlungen", unter=650):
        return FOTOS_MEDIATHEK
    if hat(tx, "Synchronisierung") and hat(tx, "Mediathek"):
        return FOTOS_MEDIATHEK
    if fotos_datum_oben(tx):
        return FOTOS_VOLLBILD
    # ---- TikTok-Blätter
    if hat(tx, "Produkt umbenennen") or (hat(tx, "Produktname", genau=True) and hat(tx, "/30")):
        return UMBENENNEN
    if hat(tx, "bewerben?") or hat(tx, "Lade ein Video hoch"):
        return BEWERBEN
    if hat(tx, "nicht mehr verfügbar") or hat(tx, "Produkt nicht verfügbar") or hat(tx, "Artikel nicht verfügbar") \
       or hat(tx, "Artikel nicht verfugbar") or hat(tx, "Produkt nicht verfugbar"):
        return NICHT_VERFUEGBAR
    if hat(tx, "Informationen zur Werbeaktion") or hat(tx, "Showcase hinzufügen") or hat(tx, "Jetzt erstellen") \
       or hat(tx, "Mehr erkunden"):
        return WERBE_BLATT
    rot_wagen = [t for t in tx if t[2] > 600 and t[0] == "Einkaufswagen"]
    if hat(tx, "Bitte auswählen") or (rot_wagen and not hat(tx, "Kasse", unter=600) and (hat(tx, "Menge") or hat(tx, "Größe")
                                                                                         or hat(tx, "Farbe") or hat(tx, "nicht vorrätig")
                                                                                         or any(re.match(r"^[A-Za-zÄÖÜäöü][\w ]{1,20}:", t[0].strip()) for t in tx))):
        # 16.11.2026 (Tatort): Blatt mit „Fall:“ + „Der Artikel ist nicht vorrätig“ blieb „unbekannt“ → nie weggeklickt
        return VARIANTEN
    menge = any(re.match(r"(?i)\W*menge\s*:", t[0]) and t[2] > 450 for t in tx)
    if menge and not hat(tx, "Kasse", unter=600) and not hat(tx, "Veröffentlichen", unter=600) \
       and (hat(tx, "nicht vorrätig", unter=450) or any(re.match(r"^[A-Za-zÄÖÜäöü][\w ]{1,20}:", t[0].strip()) and 250 < t[2] < 650
                                                          and not re.match(r"(?i)\W*menge", t[0].strip()) for t in tx)):
        return VARIANTEN                                         # 16.11.2026 (Tempo): Varianten-Blatt, dessen roter Knopf
                                                                 # anders heißt/nicht gelesen wurde – „Menge:“ + Gruppe
    # ---- Link-Listen (vor Beitrag: Liste liegt als Seite darüber)
    if hat(tx, "Dein Showcase") or hat(tx, "Aus dem Showcase"):
        return SHOWCASE_LISTE
    if hat(tx, "Einkaufswagen", ueber=160) and hat(tx, "Produkte suchen"):
        return WAGEN_LISTE
    if hat(tx, "Produkt", genau=True) and (hat(tx, "Link hinzufügen") or hat(tx, "Linktyp") or hat(tx, "Link-Typ")) \
       and not hat(tx, "Veröffentlichen", unter=600):
        return LINK_BLATT
    if hat(tx, "Veröffentlichen", unter=600) and hat(tx, "Entwürfe", unter=600):
        return BEITRAG
    if (hat(tx, "Cover", genau=True) and hat(tx, "bearbeiten", genau=True)) or \
       (hat(tx, "# Hashtags") and hat(tx, "Link hinzufügen")) or (hat(tx, "Erwähnung") and hat(tx, "Link hinzufügen")):
        return BEITRAG                                           # Tastatur offen / gescrollt: Knöpfe unten verdeckt
    if hat(tx, "Sortieren nach") or re.search(r"entwürfe\s*•", " ".join(t.lower() for t, _, _ in tx)):
        return TIKTOK_SONST                                      # Entwürfe-Liste im Profil
    if hat(tx, "Kasse", unter=600) and hat(tx, "Einkaufswagen", unter=600):
        return PRODUKTSEITE
    if hat(tx, "pro Verkauf", ueber=300) and hat(tx, "Einkaufswagen", genau=True, unter=600) and not feed_oben(tx):
        return PRODUKTSEITE                                      # Werbeblatt hochgezogen, unten nur „Einkaufswagen“ (21:27)
    # ---- Erstellen
    if hat(tx, "Auswählen", genau=True) and not hat(tx, "Mehrere auswählen"):
        return VORSCHAU
    w = hat(tx, "Weiter", genau=True, unter=600)
    if w and (hat(tx, "AutoCut") or hat(tx, "Deine Story") or hat(tx, "Vorlagen") or hat(tx, "Effekte")
              or hat(tx, "Text", genau=True) or hat(tx, "Sticker")) and not hat(tx, "Beschreibung"):
        return EDITOR
    if hat(tx, "Mehrere auswählen") or (len(dauern(tx)) >= 2 and (hat(tx, "Alle", genau=True) or hat(tx, "Videos", genau=True)
                                                                  or hat(tx, "Zuletzt", ueber=160))):
        return GALERIE
    # 18.11.2026 (148-23/24): Shop-Reiter mit Produkt „SnapBliss Mini-Kamera“ + „LIVE-Auktion“ wurde als Kamera erkannt
    # (Teilwort) → Rückweg wollte das X oben links tippen (dort LIVE). Jetzt nur die exakten Modus-Wörter unten.
    if hat(tx, "Sound hinzufügen") or (hat(tx, "KAMERA", genau=True, unter=600)
                                       and (hat(tx, "VORLAGEN", genau=True) or hat(tx, "LIVE", genau=True, unter=600))):
        return KAMERA
    # ---- TikTok-Hauptseiten
    if hat(tx, "Konto wechseln") or hat(tx, "Konto hinzufügen"):
        return KONTO_WECHSELN
    if hat(tx, "Follower", genau=False) and (hat(tx, "Folge ich") or hat(tx, "Likes") or hat(tx, "Profil bearbeiten")
                                             or hat(tx, "TikTok Studio")):
        return PROFIL
    if hat(tx, "TikTok Studio") and hat(tx, "Showcase"):
        return PROFIL
    if showcase_seite(tx):
        return SHOWCASE_SEITE
    if feed_oben(tx):
        return FEED
    if bilderzaehler(tx) and not hat(tx, "Kasse", unter=600):
        return PRODUKT_BILDER
    if hat(tx, "Bestell-ID") or hat(tx, "Profilaufrufe") or (hat(tx, "Einkaufswagen", ueber=90) and len(tx) <= 6):
        return TIKTOK_SONST
    # ---- Safari / Home
    if hat(tx, "View on TikTok Shop"):
        return SAFARI_SOCIAL1
    if hat(tx, "social1") or hat(tx, "Promote S1") or hat(tx, "Saved Videos"):
        return SAFARI
    if hat(tx, "Erneut versuchen") or hat(tx, "Tippe, um es erneut") or hat(tx, "Neu laden", genau=True) \
       or hat(tx, "Wiederholen", genau=True):
        return LADEFEHLER
    if hat(tx, "Wird geladen") and len(tx) <= 6:
        return LADEN
    if hat(tx, "Aufrufe für") or (hat(tx, "Teilen", genau=True) and hat(tx, "Anzeige", genau=True)):
        return TIKTOK_SONST                                      # eigenes Video im Vollbild
    if hat(tx, "Letzte Sucheinträge"):
        return SAFARI
    if tabs:
        return TIKTOK
    if len(tx) <= 6:
        return FOTOS_VOLLBILD if hat(tx, "Bearbeiten") or hat(tx, "Heute") or hat(tx, "Gestern") else UNBEKANNT
    return UNBEKANNT
