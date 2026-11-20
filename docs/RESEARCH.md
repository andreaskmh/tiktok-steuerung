# Research auf Social1 (täglich, 7 / 13 / 19 Uhr)

Arturs Vorgaben (19.11.2026). Erst Deutschland, dann USA. Immer „Today“ + „Trending“, keine Kategorie, keine Produktsuche, gelesen bis Seite 100; BOF DE + SLIDES DE nehmen nur Videos bis Seite 50, Reactions DE, SLIDES USA, Quality USA bis Seite 100 (Artur 19.11. abends, `SEITEN_MAX` in research.py).
Werkzeug: `werkzeuge/research.py`, Regeln `werkzeuge/research_regeln.json`, Ablage `uebergabe/research/<JJJJ-MM-TT>/`.
Geplante Aufgabe „tiktok-research-taeglich“ (Claude-App, Auto-Modus) führt den Tageslauf unten aus.

## Was in welche Liste (Datum immer TT.MM.JJJJ von heute)
| Liste | Was rein | Was nie |
|---|---|---|
| `BOF DE <datum>` | Person redet übers Produkt (Green-Screen/Bild über dem Kopf, Preis-Deals) oder filmt es faceless mit den Händen; Supplements und Parfüm ok; Beauty nur, wenn über Produkt/Preis geredet wird | Sketche und Vergleiche (Armer/Reicher, IQ, A vs. B; Ausnahme > 1M +Views), Beauty nur angewendet (Wimpern, Haare, Make-up), reine Körper-Videos, Promis |
| `SLIDES DE <datum>` | Slideshow-Flag, KI-Flag (wird dabei geredet: zusätzlich BOF), Screenshots mit Pfeil/Preis, Cartoon/Animation, Videos nur mit Musik, in denen sich eine Person zeigt oder das Produkt präsentiert wird | – |
| `Reactions DE <datum>` | Promi-Videos (ChristianWolf, SinanMovez …), auf die wir reagieren (`<land>-promis.txt`) | – |
| `SLIDES USA <datum>` | Slideshow-/KI-Format-Ideen für DE – **Produkt egal** (Artur nimmt auch Mode, Beauty, Weihnachten, personalisierte Bücher, Plüsch) | Titten/Ärsche |
| `Quality USA <datum>` | Jemand zeigt das Produkt echt, **nur wenn es das Produkt oder etwas Ähnliches im TikTok Shop DE gibt**: Technik/Gadgets, Staubsauger, Haushalt, Schlafen, Gaming, Werkzeug, Auto | reine US-Marken/US-Mode, Damenmode, Deko-Kleinkram, Beauty; Produkt in DE nicht vorhanden |

- DE: Videos höchstens 1 Woche alt. USA: älter ist ok (Deutsche setzen langsam um), Sprache egal, nicht verfügbare Videos überspringen.
- Produkte, die schon öfter viral waren, mit **anderer Hook** wieder aufnehmen. Ein erledigtes Video kommt nie wieder (DE: Nicht-Erledigtes wird übernommen, s. Schritt 0); Rangliste markiert „Produkt schon gepostet“.
- Ersetzbare Produkte (Hosen, T-Shirts, Staubsauger, Nass-/Trockensauger …) zählen als „gibt es in DE“.
- Today/Yesterday haben bei Umsetzung und Produktbestellung absoluten Vorrang (Rangliste).

## Tageslauf (Befehle aus dem Projektordner; lange Schritte im Hintergrund, nur letzte Zeilen lesen)
Vorher: kein Posten-Stapel aktiv (`pgrep -f post_mensch.py`), keine Sperre `~/.tiktok-research/.laeuft` mit lebender PID.
Erster Lauf des Tages ohne `--frisch`, weitere Läufe am selben Tag mit `--frisch` (liest alles neu, alte Nummern bleiben).

**0. Gemacht-Abgleich (vor jedem Lauf):** `python3 werkzeuge/research.py gemacht-abgleich`. **Seit 20.11.2026 arbeitet Artur
unsere `BOF DE <datum>`-Listen ab** (einmalig zählte `eigene BOF 19.11.2026` komplett als erledigt). Was er dort seit der letzten
Momentaufnahme (`~/.tiktok-research/artur-listen.json`) rausgenommen hat = erledigt → `gemacht.json`, kommt nie wieder. Arturs
eigene Listen zählen nicht mehr. Momentaufnahme nach jedem Lauf (am Ende nochmal `gemacht-abgleich`, wenn die Listen fertig sind).
**Übernahme DE (Artur 20.11.):** Nicht Erledigtes aus unseren DE-Listen früherer Tage kommt wieder in die heutige Liste derselben
Art (`filtern de` trägt die Art in `de-sortiert.json` ein, nicht neu ansehen), solange es noch auf Social1 steht, ≤ 7 Tage alt und
bis Seite 50 (BOF/SLIDES) ist. USA: weiterhin nie zweimal.

**Deutschland**
1. `python3 werkzeuge/research.py lesen de [--frisch]`
2. `python3 werkzeuge/research.py filtern de`
3. Ohne Bild einsortieren: Slideshow-Flag → `"SLIDES"`, Promi (`de-promis.txt`) → `"REACTIONS"`. Dann
   `python3 werkzeuge/research.py blaetter de --neu` → Sammelbilder `de-blatt-neu-XX.jpg` (Nr + Alter + SLIDE/KI oben links).
   KI-Flag → `"SLIDES"`, wird geredet `"BOF+SLIDES"`. Rest nach der Tabelle oben: `"BOF"` / `"SLIDES"` in `de-sortiert.json`,
   Abgelehnte in `de-nein.json` (`{"nr": "Grund"}`).
4. `speichern de "BOF DE <datum>" "<nr …>"` (BOF + BOF+SLIDES), `"SLIDES DE <datum>"` (SLIDES + BOF+SLIDES),
   `"Reactions DE <datum>" "$(cat uebergabe/research/<datum>/de-promis.txt)"`. Videos, die 7 Tage alt werden, aus den Listen
   des Tages nehmen (Funktion `aus_liste_entfernen`, sichert vorher).
5. `python3 werkzeuge/research.py rangliste de`, dann `sortieren de "<Liste>"` für alle drei Listen
   (Platz 1 zuerst einlegen = oben in Social1; einzeln raus/rein, nie die ganze Liste auf einmal)

**USA**
1. `lesen us [--frisch]`, `filtern us`, `blaetter us --neu`
2. Sortieren: Slideshow-/KI-Flag mit übertragbarer Idee → `"SLIDES"` (Produkt egal). `"QUALITY?"` nur für Technik/Gadgets,
   Staubsauger & Co., Haushalt, Schlafen, Gaming, Werkzeug, Auto – nie US-Mode/US-Marken, Damenmode, Deko-Kleinkram;
   je Produkt höchstens 2 Videos. Rest in `us-nein.json`. Ziel: Quality eher 40–60 als 250.
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
6. Slideshow-Vorbilder (Artur 20.11., ~1 Min.): `python3 werkzeuge/research.py vorbilder` → `uebergabe/ausgang/social1-vorbilder.json`.
7. (weiter mit „Skripte“ unten)

**Skripte (nach DE und USA, Artur 19.11.)**
- **Nie Social1-„Transcribe“ benutzen (kostet Credits, Artur 19.11.).** Transkripte macht `werkzeuge/transkript.py` lokal:
  yt-dlp lädt das Video, Whisper (mlx, M1) erkennt Text + Sprache (~5 s/Video). Einrichtung in `~/.tiktok-research/venv`.
  Altersbeschränkte Videos („Log in for access“) werden übersprungen – nie Browser-Cookies verwenden.
- `python3 werkzeuge/research.py skripte de` und `… skripte us` (Top 30 je Liste, kein Safari nötig).
- Nur **fremdsprachige** Videos (auch Englisch) bekommen ein Skript, deutsch gesprochene nicht. Sie stehen in
  `uebergabe/research/<datum>/SKRIPTE <TT.MM.JJJJ>.md`. Jeden Platzhalter „**DEUTSCH:** _(Claude schreibt…)_“ ersetzen durch
  **Hook:** (1 Satz) + **Skript:** (kurze Sätze, so wie man es in DE sagt, nicht wörtlich übersetzt, Preis/Deal-Logik an DE anpassen).
- Am Ende **immer im Chat anhängen** (SendUserFile, Artur 19.11.): die Ranglisten je Liste (`de-rangliste-bof/-reactions/-slides.md`, `us-rangliste-quality/-slides.md`), `de-rangliste.html`, `us-rangliste.html` (mit Vorschaubildern, nur Videos, die in den Listen sind) und die SKRIPTE-Datei.

## Rangliste (Punkte)
Frische (Today 100, Yesterday 85, 2 Tage 55 … 7 Tage 12, danach weniger) + Tempo (+Views, log, max. 40) + Video-Umsatz (Social1 `gmv` des Videos, log: €1K → 6, €10K → 9, max. 15)
+ Likes/Kommentare pro View (max. 15). Seit 21.11. ohne Creator-GMV und ohne 🔥 (Artur 20.11.). Ausgabe `<land>-rangliste.md` + je Liste extra `<land>-rangliste-bof|reactions|slides|quality.md/.html` (Artur 20.11., Platz-Nr. je Datei neu).

## Zeiten
Start 7 / 13 / 19 Uhr. Stündliche Messung (`research.py messen`, launchd `de.tiktoksteuerung.research-messen`) protokolliert Seite 1
DE+US in `~/.tiktok-research/messung.jsonl` (läuft aus einer Kopie dort, nach Änderungen an research.py `zsh werkzeuge/research-messen-installieren.sh`); nach 2–3 Tagen `research.py messung` auswerten und die Zeiten auf die Social1-Aktualisierung legen.

## Lernen
Artur schickt seine eigene Research (Listen/Bildschirmaufnahme). Video für Video vergleichen, Unterschiede mit Grund hier unter „Gelernt“ eintragen.

### Gelernt
**Arturs Rückmeldung 19.11. abends (umgesetzt 19.11. spät, siehe unten „Umgesetzt“):**
- **Verstoß-Risiko-Filter weg** (erledigt: aus).
- **Promis nicht mehr wegwerfen:** Promi-Videos (ChristianWolf, SinanMovez …), auf die wir reagieren, kommen in eine eigene Liste
  **`Reactions DE <datum>`**.
- **Schon Gemachtes:** Artur entfernt erledigte Videos aus seinen Listen (Haken raus). Abgleich: was in seinen Listen fehlt, aber
  bei uns steht, ist erledigt → aus unseren Listen entfernen und dauerhaft als „gemacht“ merken (nie wieder aufnehmen, auch künftig).
- **Sortierung in Social1 wirkt nicht:** In der Social1-Ansicht steht die Liste nicht in Ranglisten-Reihenfolge (Alter durcheinander)
  → prüfen, wonach Social1 die Listenansicht wirklich sortiert (evtl. eigenes Datum beim ersten Hinzufügen / timePosted).
- **USA:** Artur hat 39 Quality-Videos, wir 249 – viel zu viele. Nur Produkte, die es im TikTok Shop DE gibt oder bei denen die
  Wahrscheinlichkeit hoch ist (andere Marke, Versand Übersee). **Reine US-Marken** (z. B. die Firma auf Platz 1 der US-Rangliste)
  nicht nehmen. Wichtige Konzepte: **Staubsauger, Nass-/Trockensauger-Vergleiche, Klone/Dupes, Videos, in denen das Produkt
  präsentiert wird.** `SLIDES USA`: auch Video-Ideen für neue Slideshows, die man auf neue Ideen in DE anwenden kann.
- Danach alle Listen (DE + USA, 19.11.) nach den Regeln überarbeiten. Arturs Listen: `eigene BOF 19.11.2026`,
  `eigene slides 19.11.2026 DE`, `reactions 19.11.26` (unsere heißen `BOF DE 19.11.2026` / `SLIDES DE 19.11.2026`) und seine USA-Listen (Namen per getVideoLists).

**Umgesetzt 19.11.2026 spät:**
- **Sortierung:** Social1 zeigt eine Liste in Hinzufüge-Reihenfolge, das **zuerst** Hinzugefügte steht **oben**. `sortieren` legt deshalb
  Platz 1 zuerst ein (einzeln raus + sofort rein), Videos ohne Rangliste kommen ans Ende.
- **Gemacht:** `uebergabe/research/gemacht.json` = alle Videos, die Artur aus seinen Listen entfernt hat. `filtern` wirft sie immer raus.
  Abgleich nach jedem Lauf siehe Tageslauf Schritt 0.
- **Promis** → `Reactions DE <datum>`, nicht mehr raus.
- **DE neu sortiert:** 19 alte Sketch-/Vergleichs-BOF raus (2 sehr virale mit > 1M +Views bleiben), Videos ab 7 Tagen raus,
  KI-Flag-Videos ohne Reden (Körper, Kleid) → SLIDES.
- **USA-Abgleich (Arturs `eigene qualität USA` 39 / `eigene Slides USA` 42 gegen unsere 249 / 11):**
  - Quality: 28 seiner 39 hatten wir auch. Er nimmt **Technik/Gadgets** (Digitalkamera, Monitor, Retro-Konsole, Sternen-Projektor,
    WLAN-Bilderrahmen, Fotodrucker, SSD, Powerstation), **Staubsauger/Nass-Trocken/Teppichreiniger/Saugroboter**, **Schlafen**
    (Matratzenauflage, Nackenkissen), Gaming-Stuhl, Arbeitshandschuhe, Einlegesohlen, Geldbörse, Parfüm, Pyjamahose, Squishies.
  - Er nimmt **nicht**: Mode von US-Marken (Comfrt, Pacsun, Cider, Dickies, Too Turnt, Fear of God, Birkenstock, Eddie Bauer …),
    Damenmode allgemein, Weihnachts-Deko-Kleinkram, Kinderspielzeug, mehrere Videos zum selben Produkt (höchstens 1–2).
  - Slides: Nur 15 seiner 42 waren überhaupt bei unseren Kandidaten (alte Klick-Lesung ohne Slideshows). Er nimmt Slideshows
    **quer durch alle Produkte** (Mode, Beauty, Weihnachten, personalisierte Bücher, Plüsch) – es zählt das Format, nicht das Produkt.
    `filtern us` wirft Slideshows deshalb nicht mehr wegen Beauty/Supplement raus.

**Abgleich mit Arturs eigener Research (19.11.2026, Deutschland, bis Seite 50) – gilt für DE, USA wird später überarbeitet:**
- **Alter:** Was eine Woche alt ist, fliegt raus (DE nur bis 6 Tage). Videos in älteren Listen, die 7 Tage alt werden, werden gelöscht.
- **BOF – Vorrang haben zwei Formate:** (1) klassisch: Bild/Green-Screen über dem Kopf, die Person redet über das Produkt;
  (2) faceless: die Person filmt das Produkt und zeigt es mit den Händen.
- **Vergleichsvideos und Sketche: nein.** Ausnahme: Sketche mit sehr hoher Viralität, bei denen Artur einfach selbst über das
  Produkt reden kann (Sketch muss nicht nachgespielt werden).
- **Beauty:** Nicht nehmen, wenn das Produkt nur benutzt und das Ergebnis gezeigt wird (z. B. Wimpern, Haare) – das lässt sich nicht
  als BOF nachstellen. **Nehmen, wenn über das Produkt geredet wird, vor allem über den Preis** – auch wenn es dabei angewendet
  und Vorher/Nachher gezeigt wird. Vorrang: die Person redet nur über das Produkt (auf ein eigenes BOF übertragbar).
- **(AUFGEHOBEN 19.11. abends – Artur überarbeitet Skripte selbst; Filter aus, `verstoss_risiko_aktiv: false`)** ~~Verstoß-Risiko → nie:~~ Heilversprechen, Rücken-/Nacken-/sonstige Schmerzen, Haare
  (Wachstum, Ausfall, Färben), riskanter Beauty-Kram (Anti-Aging, Falten, Akne, Cellulite …). Filter `verstoss_risiko` in
  research_regeln.json; was der Produktname nicht verrät, beim Sichten aussortieren.
- **Supplements sind in DE ok** (15 in Arturs BOF-Liste), „keine Supplements“ gilt nur für USA.
- **Technik-Befund:** Die alte Klick-Lesung hat Foto-Slideshows fast komplett verschluckt (kein Vorschaubild → keine Video-Nummer →
  als „doppelt“ verworfen): 67 von Arturs Slides fehlten deshalb. Seit der direkten Lesung (getTopVideos) sind sie drin.
- **Handy-Videos, die auf dem Handy-Bildschirm den Preis zeigen** (gefilmt, nicht animiert) → **kein SLIDES**, sondern **BOF**
  (weil gesprochen wird).
- **SLIDES – Arten (alle rein):**
  - *Normale Slideshows* (erkennbare Bildfolgen): werden teils komplett übernommen, nur der Text wird geändert. Bei „Prominenten“-
    Slideshows (Gesichter, Texte, Nachrichten, WhatsApp-Verläufe u. Ä.) immer komplett übernehmen, nur Text ändern.
  - *KI-Videos*: daraus eigene Slideshows (ChatGPT + Claude) – entweder neu nach der Idee (andere Gesichter, Trend setzen) oder
    komplett übernommen und in eine Slideshow umgewandelt (Trend folgen).
  - *Creator-Gesicht als animierter Cartoon* in der Slideshow → gleiches Konzept, aber mit unseren eigenen Gesichtern.
  - *Normale Videos nur mit Musik*, in denen sich eine Person zeigt oder das Produkt präsentiert (z. B. Frau zeigt Kleid, sagt nichts)
    → daraus eine animierte Cartoon-Slideshow mit eigener (per ChatGPT erstellter) Person.
  - Regel: höchstens 5 Bilder pro Slideshow.
- **Beides (BOF + SLIDES):** Produkt im KI-Video-Stil präsentiert UND es wird sinngemäß darüber gesprochen → in beide Listen.
- **Reihenfolge in Social1** soll der Rangliste entsprechen (Platz 1 oben): `research.py sortieren` (Social1 zeigt zuerst
  Hinzugefügtes oben).

- 19.11.: Parfüm darf rein. Reine Vorführungen ohne Gesicht gehören in BOF DE. (Sketche/Vergleiche: später am 19.11. auf „nein“ geändert.)

## Technik
- **Social1 bremst** bei vielen schnellen Anfragen („Too many requests“, 429): s1_viele wartet und versucht es bis zu 6× erneut.
  Am 19.11. gingen beim ersten Sortier-Versuch (alles raus, alles rein) 180 von 362 BOF-Videos kurz verloren → aus der
  Sicherung vollständig wiederhergestellt; seitdem sortiert `sortieren` nur noch einzeln (raus + sofort rein) mit Sicherungsdatei.
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

## Slideshow-Vorbilder (20.11.2026)
`python3 werkzeuge/research.py vorbilder [--min 30000]` – Hits der Slideshow-Accounts aus research_regeln.json („vorbilder“)
→ `uebergabe/ausgang/social1-vorbilder.json` für das Slideshow-Auto (Editing System, Liste „vorbilder“). Hintergrund:
docs/SLIDESHOW-ANALYSE.md. Nicht während eines Posten-Stapels starten (öffnet ein Safari-Fenster).
