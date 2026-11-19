# Research auf Social1 (täglich, 7 / 13 / 19 Uhr)

Arturs Vorgaben (19.11.2026). Erst Deutschland, dann USA. Immer „Today“ + „Trending“, keine Kategorie, keine Produktsuche, bis Seite 100 (Artur 19.11.).
Werkzeug: `werkzeuge/research.py`, Regeln `werkzeuge/research_regeln.json`, Ablage `uebergabe/research/<JJJJ-MM-TT>/`.
Geplante Aufgabe „tiktok-research-taeglich“ (Claude-App, Auto-Modus) führt den Tageslauf unten aus.

## Was in welche Liste (Datum immer TT.MM.JJJJ von heute)
| Liste | Was rein | Was nie |
|---|---|---|
| `BOF DE <datum>` | Jemand spricht übers Produkt, Sketche („Armer/Reicher Freund“, IQ-Vergleiche), Vergleiche, Tier-Lists, Green-Screen-Deals, **auch reine Vorführungen ohne Gesicht**, Parfüm ist ok | Promis (ChristianWolf, SinanMovez), Supplements, Make-up/Haare/Wimpern/Hautpflege, reine Körper-/Po-Videos |
| `SLIDES DE <datum>` | Slideshows (Fotos/Screenshots mit Text, Produktbilder mit Pfeil/Preis), **KI-animierte Videos** (Pixar-Stil, Skelette, Grafiken) | wie oben |
| `SLIDES USA <datum>` | Slideshows + KI-animierte Videos, deren Idee man auf andere Produkte übertragen kann | Beauty/Frauenprodukte, Supplements, Titten/Ärsche |
| `Quality USA <datum>` | Jemand hat das Produkt echt und zeigt es (auch Vergleiche, Dupes/„Doppelgänger“), **nur wenn es das Produkt oder etwas Ähnliches/andere Marke im TikTok Shop DE gibt** (egal ob Versand Übersee) | wie oben; Produkt in DE in keiner Form vorhanden |

- DE: Videos höchstens 1 Woche alt. USA: älter ist ok (Deutsche setzen langsam um), Sprache egal, nicht verfügbare Videos überspringen.
- Produkte, die schon öfter viral waren, mit **anderer Hook** wieder aufnehmen. Dasselbe Video kommt nie zweimal (auch nicht nach dem Nachmachen/Abhaken); Rangliste markiert „Produkt schon gepostet“.
- Ersetzbare Produkte (Hosen, T-Shirts, Staubsauger, Nass-/Trockensauger …) zählen als „gibt es in DE“.
- Today/Yesterday haben bei Umsetzung und Produktbestellung absoluten Vorrang (Rangliste).

## Tageslauf (Befehle aus dem Projektordner; lange Schritte im Hintergrund, nur letzte Zeilen lesen)
Vorher: kein Posten-Stapel aktiv (`pgrep -f post_mensch.py`), keine Sperre `~/.tiktok-research/.laeuft` mit lebender PID.
Erster Lauf des Tages ohne `--frisch`, weitere Läufe am selben Tag mit `--frisch` (liest alles neu, alte Nummern bleiben).

**Deutschland**
1. `python3 werkzeuge/research.py lesen de [--frisch]`
2. `python3 werkzeuge/research.py filtern de`
3. `python3 werkzeuge/research.py blaetter de --neu` → Sammelbilder `de-blatt-neu-XX.jpg` ansehen (Nr + Alter oben links).
   Pro Nr entscheiden und in `de-sortiert.json` ergänzen (`{"nr": "BOF"|"SLIDES"}`), Abgelehnte in `de-nein.json` (`{"nr": "Grund"}`).
4. `python3 werkzeuge/research.py speichern de "BOF DE <datum>" "<nr nr …>"` und dasselbe für `"SLIDES DE <datum>"`
5. `python3 werkzeuge/research.py rangliste de`

**USA**
1. `lesen us [--frisch]`, `filtern us`, `blaetter us --neu`
2. Sortieren: `"SLIDES"` oder `"QUALITY?"` (Kandidat) in `us-sortiert.json`, Rest in `us-nein.json`.
3. Für jeden `QUALITY?`: Produktnamen (Social1, englisch) in 1–3 kurze Suchwörter übersetzen (Gattung, z. B. „Nass Trockensauger“, „heated jacket“)
   → alle Suchwörter in eine Datei (eine Zeile pro Wort) und **auf einmal** prüfen:
   `python3 werkzeuge/research.py de-suche --datei <woerter.txt>` (TikTok Shop DE über Social1 direkt, Bestseller zuerst, ~1–2 s/Wort).
   Einzeln geht auch: `de-suche <suchwort>`.
   Gibt es das Produkt oder etwas Ähnliches/andere Marke → `"QUALITY"`, sonst in `us-nein.json` („nicht in DE“). Treffer (Name, id, verkauft)
   in `us-quality.json` notieren (`{"nr": {"de_produkt": …, "de_id": …, "amazon": ASIN}}`).
   **Bildvergleich (Artur 19.11., Pflicht):** Bildersuche nur bei TikTok Shop und Amazon.es, **nie Google/Lens**. Für alle `QUALITY?`
   Gesucht wird automatisch mit dem **kopierten Social1-Produktnamen** (Amazon: voller Name; TikTok Shop DE über Social1: Name + kürzer,
   weil Social1 streng sucht) – dazu je Produkt 1–3 **kurze deutsche Gattungswörter** in `wuensche.json` (`{"nr": ["wort", …]}`)
   → `python3 werkzeuge/research.py bildvergleich us wuensche.json` → Sammelbilder `us-vergleich-XX.jpg` (Zeile = US-Bild + TT1… TikTok
   Shop DE nach Verkäufen + AZ1… Amazon.es, wenn aktiv). Am Bild entscheiden: gleich / ähnlich-andere Marke → `QUALITY` mit gewähltem
   TT/AZ in `us-quality.json` (Treffer-Details in `us-vergleich.json`), sonst `us-nein.json`. Echte Foto-Suche gibt es nur in den Apps.
4. **Zurzeit deaktiviert (Artur 19.11.: `amazon_aktiv: false` in research_regeln.json – Schritt auslassen).** Nur für `QUALITY`: Amazon.es suchen (`amazon <spanisches/englisches Suchwort>`), passendstes Produkt (gute Bewertungen, Preis passt) →
   `wagen <ASIN>`. **Nie kaufen, nie zur Kasse, nie „Comprar ya“.** Captcha/Login → STOPP, Artur.
5. `speichern us "SLIDES USA <datum>" …` und `speichern us "Quality USA <datum>" …`, dann `rangliste us`.
6. (weiter mit „Skripte“ unten)

**Skripte (nach DE und USA, Artur 19.11.)**
- **Nie Social1-„Transcribe“ benutzen (kostet Credits, Artur 19.11.).** Transkripte macht `werkzeuge/transkript.py` lokal:
  yt-dlp lädt das Video, Whisper (mlx, M1) erkennt Text + Sprache (~5 s/Video). Einrichtung in `~/.tiktok-research/venv`.
  Altersbeschränkte Videos („Log in for access“) werden übersprungen – nie Browser-Cookies verwenden.
- `python3 werkzeuge/research.py skripte de` und `… skripte us` (Top 30 je Liste, kein Safari nötig).
- Nur **fremdsprachige** Videos (auch Englisch) bekommen ein Skript, deutsch gesprochene nicht. Sie stehen in
  `uebergabe/research/<datum>/SKRIPTE <TT.MM.JJJJ>.md`. Jeden Platzhalter „**DEUTSCH:** _(Claude schreibt…)_“ ersetzen durch
  **Hook:** (1 Satz) + **Skript:** (kurze Sätze, so wie man es in DE sagt, nicht wörtlich übersetzt, Preis/Deal-Logik an DE anpassen).
- Am Ende **immer im Chat anhängen** (SendUserFile, Artur 19.11.): `de-rangliste.md`, `us-rangliste.md` und die SKRIPTE-Datei.

## Rangliste (Punkte)
Frische (Today 100, Yesterday 85, 2 Tage 55 … 7 Tage 12, danach weniger) + Tempo (+Views, log) + Creator-Umsatz (log)
+ Likes/Kommentare pro View + 🔥-Bonus. Ausgabe `<land>-rangliste.md`.

## Zeiten
Start 7 / 13 / 19 Uhr. Stündliche Messung (`research.py messen`, launchd `de.tiktoksteuerung.research-messen`) protokolliert Seite 1
DE+US in `~/.tiktok-research/messung.jsonl` (läuft aus einer Kopie dort, nach Änderungen an research.py `zsh werkzeuge/research-messen-installieren.sh`); nach 2–3 Tagen `research.py messung` auswerten und die Zeiten auf die Social1-Aktualisierung legen.

## Lernen
Artur schickt seine eigene Research (Listen/Bildschirmaufnahme). Video für Video vergleichen, Unterschiede mit Grund hier unter „Gelernt“ eintragen.

### Gelernt
- 19.11.: Parfüm darf rein. Sketche/Vergleiche und reine Vorführungen ohne Gesicht gehören in BOF DE.

## Technik
- **Seit 19.11.2026 spricht research.py direkt mit Social1** (Server-Aktionen der Webseite, im eingeloggten Safari-Fenster ausgeführt –
  keine Cookies, keine Klicks): Lesen = `getTopVideos` (100 Seiten DE in ~2 Min. statt ~40), Speichern = `addVideoToList` gebündelt
  (prüft die echte Liste, legt fehlende Listen per `createVideoList` an), DE-Check = `searchProducts`. Die Aktions-IDs liest das
  Werkzeug bei jedem Lauf aus den Programmdateien von Social1 (sie ändern sich bei Updates); findet es sie nicht → STOPP „Social1 umgebaut?“.
- **Amazon.es direkt (19.11., Schritt zurzeit deaktiviert):** `amazon --datei <woerter.txt>` sucht viele Wörter auf einmal (Suchseite im
  Hintergrund geladen, ~3 s/Wort), `wagen <ASIN> [<ASIN> …]` lädt die Produktseite im Hintergrund und sendet NUR das Formular
  „In den Einkaufswagen“ (Ziel `handle-buy-box`/`add-to-cart`, nie Kasse/„Comprar ya“), danach Kontrolle im Einkaufswagen.
  `wagen <ASIN> --pruefen` = nur prüfen, nichts senden. Robot-Prüfung (Captcha) → STOPP, Artur. Einschalten: `amazon_aktiv: true`.
- Social1 liefert pro Video auch `slideshow` / `ki` (Social1-Einstufung) und `time_posted`; die Sammelbilder zeigen „SLIDE“ / „KI“ an.
- research.py nutzt sein eigenes Safari-Fenster (Social1-Videoseite `social1.ai/?…`) und für Amazon ein eigenes. Die Listen-Tabs von
  post_mensch (`saved-videos/…`) werden nie angefasst. Die Region wird bei jedem Aufruf mitgegeben (kein Umstellen mehr nötig).
- Alte Klick-Wege bleiben als Reserve: `speichern_klick`, Sicherung `werkzeuge/research.py.bak-20261119-direkt`.

## Direkter Weg zu Social1 (Untersuchung 19.11.2026, Artur: „schneller“) – eingebaut, Notizen
Social1 ist eine Next.js-Seite; Speichern läuft über **Server-Aktionen** (POST auf die aktuelle Seiten-URL, Header
`Accept: text/x-component`, `next-action: <id>`, `next-router-state-tree`, `x-deployment-id`; Body = JSON-Array). Mitgeschnitten
per fetch-Hook im Safari-Tab (Aktions-IDs ändern sich bei jedem Social1-Update → zur Laufzeit neu ermitteln, nicht fest einbauen):
- **Hinzufügen** (19.11.: `600257693932abc498c5df86eb9d6bab714907eddc`): `[listId, {videoId, isAd:0|1, description:null, handle,
  timePosted:"JJJJ-MM-TT hh:mm:ss", product:{productId, name, priceDisplay:"", imgUrl}}]`
- **Entfernen** (`60c2803ebd4f09b1ff11ae8cd3a72d63b28d469282`): `[listId, [videoId, …]]` (mehrere auf einmal)
- **Listen holen** (`0031ae1a8160653183a350a3d6af68883aa113bc11`): `[]` → alle Listen mit `_id`, `name`
- **Eine Liste holen** (`40ce278ef0cb2208c4bf937eb78aee80e14306455b`): `[listId]` → Videos der Liste (inkl. timePosted)
- Neue Liste anlegen: noch nicht mitgeschnitten. Listen-ID BOF DE 19.11.2026 = `6afe48ed035d76b7459d173f`.
- **Seiten lesen (gelöst):** `getTopVideos({limit:12, page:<ab 0>, region:"de"|"us"})`; Standard = Today + Trending (geprüft gegen die
  Seite). Weitere Felder: tsStart/tsEnd, performanceFilter, sortBy, isSlideshow, isAi, category, lang. Antwort `results[]`, `has_more`.
- **DE-Check (gelöst):** `searchProducts({query, region:"de"})` → product_name, units_sold, gmv, price_value …
- Früher: Die Videos stehen NICHT im RSC-Seitenpayload (`/?page=N` mit `RSC: 1` hat keine Video-IDs); sie werden
  nachgeladen. Ein fetch-Hook nach dem Laden sah beim Klick auf Seite „2“ keine Anfrage (Next nutzt evtl. eine früh gemerkte
  fetch-Referenz). Nächster Versuch: in den JS-Chunks nach `createServerReference(` suchen (Aktions-ID + Name, z. B. getVideos)
  oder XMLHttpRequest/`performance`-Einträge prüfen; Argumente (Region, Seite, Zeitraum, Performance) aus dem Chunk ablesen.
- Geprüft 19.11.: Durch das Klick-Speichern fehlten in BOF DE 25 protokollierte Videos → 22 direkt nachgetragen (Liste 363),
  1 ohne Video-Nummer, 2 nicht mehr unter den Kandidaten. SLIDES DE war vollständig.
