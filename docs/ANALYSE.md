# Account-Analyse (Provision selbst rechnen) – Stand 19.11.2026

Ziel (Artur): morgens + abends pro Account die **echten** Zahlen, weil TikToks Einnahmenanalyse
(„Bestellung erstellt“ / „abgeschlossen“) nicht stimmt. Rechnung nach Artur:
- **Tatsächliche Provision** = tägliche Auszahlungen („Täglicher Umsatz“).
- **Voraussichtliche Provision** = bezahlte Bestellungen aus „Partnerbestellungen“ (nicht Einnahmenanalyse).
- Prämien getrennt ausweisen. Auszahlung i. d. R. 14 bzw. 30 Tage nach Zustellung; bei Rückgabe-Anfrage erst,
  wenn die Frist abläuft oder die Rückgabe abgelehnt wird.

## Weg in der App (getestet an andrucha.official, iPhone 15 Pro Max)

Profil → „TikTok Shop für Creator*innen“ → Toolkit-Pfeil → **Einnahmen** = „Auszahlungsübersicht“.
**Nie „Abheben“ tippen.**
- Pfeil neben „Verfügbare Auszahlung“ → **Auszahlungsverlauf**, Reiter: Täglicher Umsatz (Tag → jede Bestellung mit
  Bestell-ID, Video, vorauss./tats. Provision → „Details anzeigen“: bestellt/bezahlt/versendet/zugestellt/abgewickelt),
  Pauschalgebühr, Auszahlungen (= Abhebungen aufs Konto, keine Einnahmen), Verstöße (Abzüge), **Belohnungen** (Prämien).
- **Partnerbestellungen** → Download-Symbol oben rechts → Filter (Datum: erstellt/ausgeglichen/Zahlung; Status;
  Quelle; Bonus) → Bestätigen → Exportverlauf → Datei laden (öffnet Safari → „Laden“) → landet per iCloud auf dem Mac in
  `~/Library/Mobile Documents/com~apple~CloudDocs/Downloads/affiliate_orders_*.xlsx`. Dateien 7 Tage im Exportverlauf.

## Export `affiliate_orders_*.xlsx` (1 Blatt, 1 Zeile pro Bestellposition)

Wichtige Spalten: Bestell-ID, Produktname, Produkt-ID, Preis, Verkaufte/Rückerstattete Artikel, Shop-Name,
Art der Bestellung (Shop-Anzeigen / Affiliate), **Abrechnungsstatus** (Bezahlt / Ausstehend / Ungeeignet),
Inhaltstyp + **Inhalts-ID (= Video-ID)**, Vorauss. Provisionsrate/Standardprovision/Shop-Anzeigen/Bonus,
Tatsächliche Provisionsrate, Standardprovision, **Endgültig verdienter Gesamtbetrag**, Bestelldatum,
**Abrechnungsdatum der Provision** („/“ = noch offen). Zahlen mit Komma, Datum TT/MM/JJJJ hh:mm:ss.
Kein Zustelldatum im Export (nur in den Bestell-Details der App).

**Geprüft 19.11.:** Summe „Endgültig verdienter Gesamtbetrag“ je Abrechnungsdatum = „Täglicher Umsatz“ der App
auf den Cent (6.11.–19.11.). Die Prämie aus „Belohnungen“ (5 €) steht **nicht** im Export → separat ablesen.

## Technik

- Server bedient nur **ein** iPhone per USB. Zum Testen iPhone 11 per `DELETE /api/devices/<id>` raus, 15 Pro Max
  (UDID 00008130-00163088368A001C) per `POST /api/devices {"udid":…}` rein; Werkzeuge mit `TS_IPHONE_UDID=…`.
  Vor dem nächsten Posten iPhone 11 (00008030-00096C8621C3402E) wieder einbinden.

## kmhview (Stand 20.11.2026)

Eine Ansicht der Provisionszahlen, drei Wege: **iPhone-App** und **Mac-App** `kmhview` (`app/kmhview`, SwiftUI, ein Ziel für
iOS + macOS, Personal Team → iPhone-App 7 Tage gültig) und **Browser**: https://claude.ai/artifact/XVnK7tCrYwqgy499zy6pjS.

Ablauf (Morgen/Abend):
1. `TS_IPHONE_UDID=00008030-00096C8621C3402E python3 werkzeuge/analyse/export_holen.py <konten…>` – am iPhone 11 (Kabel)
   pro Account: Konto wechseln → Creator-Bereich → Toolkit → Einnahmen → Partnerbestellungen → Export → Safari „Laden“ →
   Downloads → Teilen → AirDrop an „MacBook Pro von Andreas“ (iPhone 11 hat andere iCloud, darum AirDrop) →
   `werkzeuge/analyse/exporte/<konto>.xlsx`. Werbe-Popups: rot tippen, dann zurück (Artur). Nie „Abheben“.
2. `python3 werkzeuge/analyse/baue.py` → `bestellungen.json` (alle Konten).
3. `python3 werkzeuge/analyse/app_daten.py` → `provision.json` in iCloud Drive `kmhview/` (Mac-App liest direkt, iPhone-App
   nach einmaliger Ordnerwahl) + hier.
4. `python3 werkzeuge/analyse/web.py` → `app/web/kmhview.html`, als Artifact (gleiche URL) neu veröffentlichen.

Konten auf dem iPhone 11: anduri.official, ella_robinson2, artur.official, andreasfastlane, andreas.testet
(leonida.highlightss ist kein Shop-Account → nicht exportieren). andrucha.official nur auf dem iPhone 15 Pro Max (Export vom 19.11.). Profilbilder: `avatare/`.
„Voraussichtlich“ (heute/gestern/7/30 Tage) = ausgezahlte + offene Provision nach Bestelldatum, ohne „nicht berechtigt“.
