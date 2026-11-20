# Stand Analyse / statsKMH – 20.11.2026, ca. 04:00

## Fertig
- App **statsKMH** (Projekt `app/kmhview`, Bundle de.kammerloch.kmhview, Team S5LVJTLB67, Personal Team → iPhone-App 7 Tage):
  iPhone 15 Pro Max + Mac (/Applications/statsKMH.app). Browser: https://claude.ai/artifact/XVnK7tCrYwqgy499zy6pjS
  (aus `app/web/vorlage.html` via `werkzeuge/analyse/web.py` → `app/web/statsKMH.html`, mit `url` neu veröffentlichen).
- Daten: `werkzeuge/analyse/` – `export_holen.py` (iPhone 11, AirDrop), `baue.py`, `app_daten.py` (→ iCloud `statsKMH/provision.json`).
- Zeiträume Heute/Gestern/3/7/30 Tage/eigener Zeitraum (Datum klar angezeigt, „letzte N Tage“ = rollierend inkl. heute).
- Kacheln: Bereits ausgezahlt (≈ abgerechnet + Prämien − bereit), Zur Auszahlung bereit („Verfügbare Auszahlung“ abgelesen:
  anduri 1880,12 / ella 1760,25 / artur 381,84; andreasfastlane + andreas.testet fehlen noch), Noch offen, Abgerechnet gesamt,
  Prämien, Nicht berechtigt. Diagramme interaktiv (Wert beim Antippen/Hover).
- Video-Performance (Sales/GMV je Video aus Export); **Aufrufe fehlen noch**.

## Erkenntnis 20.11. (wichtig)
TikTok-App: Creator-Bereich („TikTok Shop für Creator*innen“) → Pfeil rechts neben „Heute | Letzte 7 Tage“ → Seite **„Daten“**
mit Heute/Gestern/7 Tage/Benutzerdefiniert. Dort offiziell: Schlüsseldaten (GMV, Verkaufte Artikel, Produkt-Sichtkontakte,
Produktklicks, **Vorauss. Provisionen**) und **Inhalts-Performance → Video** (GMV, **Ansichten**, Verkaufte Artikel, Top-Videos mit
GMV/Aufrufe/Artikel, „Alle anzeigen“). Beispiel anduri gestern 19.11.: Vorauss. Provisionen 114,76 € (Export-Rechnung 113,09 €),
GMV 958,76 €, 76 Artikel, Ansichten 207,2K. Artur rechnet mit **dieser** Zahl (Summe aller Accounts gestern laut Artur 305,01 €;
Export-Rechnung 298,94 €) → Export weicht ab, weil TikTok einen Teil später „nicht berechtigter“ Bestellungen mitzählt.

## Nächste Schritte
1. `werkzeuge/analyse/daten_holen.py`: pro Account die „Daten“-Seite ablesen (Heute, Gestern, 7 Tage, Benutzerdefiniert 3 + 30 Tage)
   – Schlüsseldaten + Video (Ansichten, GMV, Artikel) + Top-Videos-Liste („Alle anzeigen“). Speichern `exporte/<konto>.daten.json`
   + Tagesverlauf (jeder Lauf hängt „Gestern“ an `exporte/<konto>.tage.json` an). App/Web: Vorauss. Provision Heute/Gestern/7 Tage
   aus diesen offiziellen Zahlen, Aufrufe/Likes/Kommentare in Video-Performance.
2. Prämien pro Account: Einnahmen → Pfeil bei „Verfügbare Auszahlung“ → Auszahlungsverlauf → Reiter „Belohnungen“ (ablesen).
3. Guthaben für andreasfastlane, andreas.testet: `export_holen.py --guthaben andreasfastlane andreas.testet`.
4. Viral-Regeln fürs Research-System (eigene Daten, 691 Videos mit Verkauf): Top 10 % ≥ 14 Bestellungen / ≥ 39 € Provision in den
   ersten 3 Tagen, Top 5 % ≥ 32 Bestellungen / ≥ 63 € (Top 5 % = 50 % aller Bestellungen). Mit Ansichten ergänzen
   (z. B. ≥ 50K Aufrufe in 3 Tagen + ≥ 0,05 % Kaufquote). Liste „Nochmal machen“ → Übergabe an Research-System (Social1-Listen) – mit
   der Research-Session abstimmen, deren Dateien nicht selbst ändern.
5. Live ohne Handy: TikTok Display API (developers.tiktok.com, Login Kit + Scope video.list → view/like/comment_count je Video;
   Artur legt Entwickler-App an und meldet jeden Account einmal an) für Aufrufe. Sales: kein bestätigter Creator-API-Zugang →
   weiter per iPhone, aber automatisch morgens/abends planen.
6. Danach: `sync.sh sichern`, Eintrag in AENDERUNGEN.md.
