# Research auf Social1 (täglich, 7 / 13 / 19 Uhr)

Arturs Vorgaben (19.11.2026). Erst Deutschland, dann USA. Immer „Today“ + „Trending“, keine Kategorie, keine Produktsuche, bis Seite 50.
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
   → `python3 werkzeuge/research.py de-suche <suchwort>` (TikTok Shop DE über Social1, Land DE, Bestseller zuerst).
   Gibt es das Produkt oder etwas Ähnliches/andere Marke → `"QUALITY"`, sonst in `us-nein.json` („nicht in DE“). Treffer (Name, id, verkauft)
   in `us-quality.json` notieren (`{"nr": {"de_produkt": …, "de_id": …, "amazon": ASIN}}`).
4. Nur für `QUALITY`: Amazon.es suchen (`amazon <spanisches/englisches Suchwort>`), passendstes Produkt (gute Bewertungen, Preis passt) →
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
- Die Datei am Ende **im Chat anhängen** (SendUserFile).

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
- research.py nutzt ein eigenes Safari-Fenster (Social1-Videoseite `social1.ai/?…`), DE-Check ein eigenes (`social1.ai/products`), Amazon ein eigenes.
  Die Listen-Tabs von post_mensch (`saved-videos/…`) werden nie angefasst. Land wird nach jedem Lauf auf DE zurückgestellt.
- Klicks immer per `setTimeout`; hängt der Tab, schließt research.py ihn selbst und macht weiter (fortsetzbar).
