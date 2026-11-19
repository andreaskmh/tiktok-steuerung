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
