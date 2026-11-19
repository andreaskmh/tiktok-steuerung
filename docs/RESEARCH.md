# Research auf Social1 (täglich)

Arturs Vorgaben vom 19.11.2026. Ablauf: erst Deutschland, dann USA. Immer „Today“ + „Trending“, keine Kategorie, bis Seite 50.

## Befehle (`werkzeuge/research.py`, Ablage `uebergabe/research/<JJJJ-MM-TT>/`)
1. `lesen de` – alle Seiten lesen (im Hintergrund, fortsetzbar)
2. `filtern de` – raus: älter als 7 Tage (DE), Promis, Beauty, Supplements (`research_regeln.json`); Rest = Kandidaten mit Nr
3. `blaetter de` – Sammelbilder (20 Vorschaubilder je Bild, Nr + Alter) → Claude sortiert in `de-sortiert.json`
   (`{"nr": "BOF" | "SLIDES" | "QUALITY"}`)
4. `speichern de "BOF DE 19.11.2026" <nr …>` – in die Social1-Liste (legt sie bei Bedarf an)
5. `rangliste de` – Punkte und Platzierung → `de-rangliste.md`

## Listen
- DE: `BOF DE <datum>` (jemand spricht übers Produkt, keine Promis), `SLIDES DE <datum>` (Slideshows + KI-animierte Videos)
- USA: `SLIDES USA <datum>` (übertragbar auf andere Produkte), `Quality USA <datum>` (Produkt wird echt gezeigt, auch
  Vergleiche/Dupes; nur wenn es das Produkt – oder ein ähnliches/anderer Marke – im TikTok Shop DE gibt → dann Amazon.es
  suchen und in den Einkaufswagen legen, nie kaufen)
- Nie: Beauty/Frauenprodukte, Supplements, nackte Haut (USA). Fremdsprachige US-Videos sind ok. Nicht verfügbare Videos überspringen.

## Rangliste (Punkte)
Frische (Today 100, Yesterday 85, 2 Tage 55 … 7 Tage 12) + Tempo (+Views) + Creator-Umsatz + Likes/Kommentare pro View
+ 🔥-Bonus. Today/Yesterday haben bei der Umsetzung immer Vorrang.

## Offen
- Zeiten: Social1-Aktualisierung erst messen (2–3 Tage), Start-Vermutung 7 / 13 / 19 Uhr.
- USA-Ablauf (Produktcheck DE, Amazon.es), deutsche Skripte über „Transcribe“.
- Lernen: Arturs Listen mit meinen vergleichen, Gründe als Regeln hier eintragen.
