# Posten wie Artur – `werkzeuge/post_mensch.py` (seit 12.11.2026 abends)

Folgt Arturs eigenem Ablauf aus seinen Bildschirmaufnahmen (Editing System `eigene/POSTEN-ABLAUF.md`).
Ersetzt `post_wagen.py`/`posten.py` beim Posten (`eingang.py posten` ruft es auf; alter Weg nur mit `TS_ALT=1`).

```bash
python3 werkzeuge/post_mensch.py --stapel <stapel>                 # alle „freigegeben“, Account für Account, AirDrop vorher
python3 werkzeuge/post_mensch.py <eingang.json>                    # ein Video
python3 werkzeuge/post_mensch.py <json> --entwurf --ohne-airdrop   # Test: bis „Entwürfe“, nichts veröffentlichen
python3 werkzeuge/post_mensch.py --aufraeumen <json>               # nur Social1-Lesezeichen + Fotos
python3 werkzeuge/post_mensch.py --fotos <stapel>                  # Gepostete des Stapels aus Fotos löschen
```
Ausgabe: eine Zeile pro Schritt mit Sekunden seit Start, je Video `✓ … 84 s`, am Ende `FERTIG x/y, Ø … s`. `STOPP …` → Foto
(`python3 werkzeuge/kabel.py foto`), Ursache beheben, denselben Befehl neu starten (Gepostete überspringt der Stapel über den Status).

## Seit 15.11.2026 abends: Zustandsmaschine
- `werkzeuge/bildschirm.py` erkennt jeden Bildschirm aus dem OCR-Text (Dialoge vor Seiten, LIVE/System nie antippen).
- `zur_hauptseite()`: von jedem Bildschirm mit genau einem Schritt je Bildschirm zurück (ersetzt tiktok_hauptseite/beitrag_abbrechen).
- `ein_video` merkt sich den Fortschritt; Hänger → `fortsetzen_planen` liest den Bildschirm und macht dort weiter (bis 6×).
- Fehlerarten: `Stopp` (weiter am Bildschirm), `Sperre` (falsches Video/Produkt/Text → verwerfen, nächstes Video),
  `Hart` (Lauf stoppt), `Entwurf` (nicht verfügbar → ohne Link). 3 gescheiterte Videos in Folge → STOPP + Foto.
- Schluss-Prüfung (Cover + Beschreibung) vor jedem Veröffentlichen/Entwurf. Beschreibung = nur Hashtags.
- Tests: `python3 werkzeuge/test/test_posten.py` (offline, 646 echte Bildschirme), Trockenlauf `post_mensch.py --wo`.
- Details + Lehren: Editing System `eigene/TIKTOK-STEUERUNG.md` §2 „15.11.2026 19:00“.
Die Schritt-Beschreibung unten gilt weiter, Fotos: zuerst Sammel-Löschen in „Zuletzt gesichert“.
- Seit 16.11.2026 23:30 (Tempo): AirDrop kommt nicht an → sofort nochmal (vor TikTok), „schon da“ nur nach gesehener Ankunft
  (`ausgang/airdrop-<stapel>-da.txt`); Social1-Abhaken läuft im Hintergrund (Mac) ohne Neuladen; Übergänge warten auf den
  nächsten Bildschirm statt fester Pausen. Details `docs/AENDERUNGEN.md`.

## Ablauf pro Video
1. **Account** (nur beim 1. Video und bei Wechsel): TikTok → Profil (300/681) → `@account`? sonst Name oben links → „Konto wechseln“ →
   Account erst antippen, wenn die Liste ruht (nie „Konto hinzufügen“).
2. **Produkt:** Home → Suche „Safari“ → ⌘L → `social1.ai/products/<id>` → warten bis Produktname da → „View on TikTok Shop“ →
   Banner „ÖFFNEN“ / Dialog „Öffnen“ / „TikTok öffnen“ antippen, bis die Produktseite (Einkaufswagen + Kasse) mit dem Shop da ist.
3. **Showcase:** „Verdiene … pro Verkauf“ → „Zum Showcase hinzufügen“. Steht dort „Mehr erkunden“ (schon drin) oder fehlt der Streifen →
   **Einkaufswagen** (grau, links; Lage gegen „Kasse“ geprüft) → erste verfügbare Variante → rotes „Einkaufswagen“ → „hinzugefügt“.
4. Blatt runterwischen, Produktseite X → „+“ (erkannt an türkis/pink Rand, Pixel) → Galerie unten links → Kachel mit Hook-Titel
   (Kabel-OCR) → Vorschau → „Auswählen“ → „Weiter“ → Editor „Weiter“ → **Vorschaubild muss den Hook-Titel zeigen** (sonst STOPP).
5. „Beschreibung hinzufügen“ → menschlich tippen (Häppchen 2–5 Zeichen). Text: `beschreibung` aus der JSON, sonst
   1 Produkt-Hashtag (erster eigener aus `hashtags`) + `#tiktokshopblackfriday #superdeals #livedeals` (bis 30.11.2026) in
   wechselnder Reihenfolge, optional `kurz` (1–2 Wörter) davor.
6. „Link hinzufügen“ → „Produkt“ → warten bis „Dein Showcase“ geladen → Showcase: oberstes Produkt prüfen (Name) → „Hinzufügen“;
   Wagen: „Weitere Produkte hinzufügen“ → „Einkaufswagen“ → oberstes → „Hinzufügen“. Dialog „zum Video hinzufügen?“ → Hinzufügen.
   „Produkt umbenennen“: **nicht umbenennen**, warten bis „Hinzufügen“ kräftig rot ist (blass = lädt), dann tippen. „zustimmen“ → tippen.
   Pilot-Hinweis „noch x von 3“ wird geloggt.
7. **@Brand** nur mit `handle` und wenn genau dieser Nutzername in der Trefferliste steht; sonst zurück, ohne Brand.
   Brands ohne Konto merkt sich `uebergabe/ausgang/brand-konten.json` (dann keine Suche mehr, spart ~10 s).
8. **Veröffentlichen** erst, wenn der Knopf kräftig rot ist (Pixel). `--entwurf` / `ausverkauft` → „Entwürfe“ (links geprüft).
9. **Aufräumen:** Social1 am **Mac** (Safari, Liste offen in einem Tab `social1.ai/saved-videos/<liste>`): Karte mit der Produkt-ID →
   Lesezeichen „Save to list“ → Haken der offenen Liste raus → „Done“ (per JavaScript, nie „Delete“). Spart den App-Wechsel am iPhone.
   **Fotos gesammelt am Stapel-Ende** (einmal Fotos öffnen statt pro Video, spart ~10 s je Video): Mediathek → Kachel mit dem
   Hook-Titel (im Raster lesbar) → Vollbild prüfen → Mülleimer (289/684, 1. Tipp kommt oft nicht an → bis 4×) → „Video löschen“
   (30 Tage in „Zuletzt gelöscht“). Getestet 12.11.: 17 s fürs erste Video inkl. App öffnen, danach ~8 s je Video.
   Bricht der Stapel ab: `post_mensch.py --fotos <stapel>`.

## Gefahren-Sperre (jeder Tipp)
- Kein Tipp, wenn im Umkreis von ~38 Pkt ein Label steht: Kasse, Jetzt kaufen, LIVE (auch OCR „ÇIVE“/„LIV“), LIVE gehen/Event,
  Konto hinzufügen, Delete, Registrieren, Abmelden, Event erstellen.
- **Nie oben links tippen, wenn der Feed oben steht** („Für dich/Gefolgt/In der Nähe/Entdecken“): dort liegt das LIVE-Symbol.
  (Ursache der LIVE-Event-Seite am 12.11.: blinder Zurück-Tipp 23/57 im Feed.)
- CAPTCHA-/Prüfungs-Wörter irgendwo am Bildschirm → sofort STOPP (Artur löst).
- Tipp-Punkte ±3 Pkt zufällig, Pausen ±25 %, Tippen in Häppchen → kein gleiches Muster.
- Doppel-Schutz (`gepostet.sh`), Tageslimit andreas.testet 3 (Zähler `posts-<tag>.json`), Status in der Eingang-JSON.

## Messwerte (12.11.2026, anduri.official, Testvideo „Beheizte Decke“, als Entwurf)
| Schritt | Showcase-Weg (Einzelschritte) | Wagen-Weg (am Stück) |
|---|---|---|
| Account prüfen | 10 s | 10 s |
| Social1 → Produktseite | 24 s | 20 s |
| Showcase / Wagen | 4 s | 20 s |
| „+“ → Beitragsseite | 19 s | 21 s |
| Beschreibung tippen | 13 s | 13 s |
| Link | 8 s | 17 s |
| Brand (nicht gefunden) | 10 s | 10 s |
| Entwürfe | 3 s | 5 s |
| **Summe** | **~91 s** | **116 s** |
Im Stapel fallen Account-Prüfung (außer beim 1. Video eines Accounts) und bekannte Brands ohne Konto weg → Showcase-Weg ~70 s,
Wagen-Weg ~95 s.

## Bekannte Stolpersteine
- Steuerverbindung reißt manchmal ab („Connection was terminated abruptly“, Bild läuft weiter) → `open-iphone-use stop`,
  `python3 werkzeuge/kabel/waechter.py einmal`.
- Reißt die Steuerverbindung ab, liefert der Server weiter das **letzte** Bild (sah aus wie ein hängendes Teilen-Blatt in Fotos) →
  Server neu starten, dann neu schauen.
- TikTok-Leiste unten hat keine Texte → Hauptseite über die Farben des „+“ (`bin/pixel`, Swift, `zsh werkzeuge/build.sh`).

## Freigabe
Gepostet wird nur nach Arturs Abnahme der Videos im Chat („passt“, `/fertig`). Danach **keine weitere Abfrage**, auch nicht beim
ersten Post eines Stapels (Artur 12.11.2026) – Stapel im Hintergrund starten, nur bei `STOPP` eingreifen.

## Drei Produkt-Szenarien (Artur 16.11.2026, Bildschirmaufnahmen)
1. **Noch nie im Showcase:** „pro Verkauf“ → „Zum Showcase hinzufügen“ → Produktseite zu → „+“ → … → Link → Produkt →
   Showcase (warten bis „Wird geladen“ weg + Liste ruhig) → oberstes → umbenennen → Hinzufügen.
2. **Schon im Showcase** („Jetzt erstellen“/„Mehr erkunden“ im Werbe-Blatt): Blatt zu → Einkaufswagen (1 Tipp, Toast abwarten)
   → „+“ → … → Link → Produkt → „Weitere Produkte hinzufügen“ → „Einkaufswagen“ → oberstes → Dialog „Hinzufügen“ → umbenennen.
3. **Kann nicht in den Einkaufswagen** (Neukunden-Hinweis): „pro Verkauf“ → „Jetzt erstellen“ → „Videos“ → umbenennen (nicht
   änderbar → Standard-Namen) → Hinzufügen → Galerie unten rechts → Video → Beitrag (Produkt schon verlinkt).

**17.11.2026 19:10 – Umbenennen mit ungültigen Zeichen (Video 148-01 ESN, Steuer-Chat):** Shop-Name „ESN Vitamin D3+K2 …“ → TikTok zeigt „Ungültige Zeichen entfernen: +“, Hinzufügen bleibt blass. Der Einkaufswagen-/Showcase-Weg wartete vor dem Umbenennen auf das rote Hinzufügen → nie umbenannt → „nach dem Verlinken nicht zurück“ (2×). Jetzt: steht „Ungültige“ da, wird sofort umbenannt; danach neu lesen, Hinzufügen erst bei Rot. Leeren robust (`feld_leeren`): Feld antippen, ⌘A, ⌘→ (Cursor ans Ende), Löschen × (Zeichen + 5), am Bildschirm 0/30 prüfen (bis 3×), erst dann den Button-Text tippen und mit `name_ok` prüfen. Gilt auch für den „Jetzt erstellen“-Weg. Backup `werkzeuge/post_mensch.py.bak-20261117-1905-plus`.

**17.11.2026 19:35 – Tageslimit zeigt sich als Hänger beim Verlinken (Artur, Video 148-51):** Bei anduri.official (23 Posts + 1 Entwurf heute) blieb das 25. Video auf „Produkt umbenennen“ hängen („nach dem Verlinken nicht zurück auf der Beitragsseite“). Laut Artur heißt das: Tageslimit von 25 erreicht, Entwürfe zählen offenbar mit bzw. der eigene Zähler weicht ab. Dann nicht nochmal versuchen, Beitrag verwerfen, der Account ist für heute fertig, das Video auf einen anderen Account umhängen oder in REST-POSTEN für morgen. Seit 17.11. sichert post_mensch bei diesem Hänger ein Foto (`uebergabe/ausgang/verlinken-haenger-*.png`).

**17.11.2026 19:40 – Limit-Hinweis lesen statt auf Hänger warten (Artur: „achte lieber auf den Hinweis“):** Den genauen Wortlaut bei 148-51 (anduri) haben wir nicht festgehalten: kein Foto, und der Bildschirmtext wurde nicht geloggt. Neu in post_mensch: Beim Verlinken wird jede Runde zuerst der Bildschirmtext auf einen Limit-Hinweis geprüft (`limit_hinweis`: „Limit“/„Tageslimit“/„Limit erreicht“, „maximale Anzahl“, „heute keine/nicht mehr“, „morgen erneut/wieder“, „daily limit“, „noch 0 von“; „limitiert“/„Limited“ zählen nicht). Treffer → Foto `limit-*.png`, Bildschirmtext ins Log, `✗ … LIMIT <account>`, Beitrag verwerfen, alle weiteren Videos dieses Accounts heute überspringen (Status fehler „LIMIT“), weiter mit dem nächsten Account. Hänger beim Verlinken loggen jetzt den ganzen Bildschirmtext + Foto. Sobald der echte Wortlaut bekannt ist: hier eintragen und `LIMIT_RE` schärfen. Nebenwirkung bei 51: Beim Verwerfen landete TikTok im Editor (Sound „Vivaldi“ angehängt), beim Zurück speicherte TikTok automatisch einen **Entwurf von 51 auf anduri** (nicht veröffentlicht, Artur löscht ihn).

**17.11.2026 19:45 – TikTok schließen als Rettung bei Hängern (Artur: „lerne TikTok auf dem Handy zu schließen“, Steuer-Chat am iPhone geübt):** `tiktok_schliessen()`: Home, 1 s, Doppel-Home → App-Umschalter (ein Wisch vom unteren Rand öffnet ihn übers Kabel NICHT); bis 4× `ziehe(90,400,300,400)`, bis „TikTok“ über einer Karte steht; Karte mit `ziehe(x,450,x,40,0.25)` nach oben wegwischen, prüfen (kein „TikTok“-Titel mehr), Home. Danach TikTok über die Suche öffnen, 4 s warten → Feed. Ersetzt in `zur_hauptseite` das bloße „TikTok neu nach vorn“, wenn ein Bildschirm 3× bleibt (z. B. hängender Editor/„umbenennen“ bei 148-51). Live getestet 19:42 (Feed → geschlossen → Feed). Punkte 334 × 735, nicht Bildpixel.

**17.11.2026 21:15 (Artur): Entwürfe zählen NICHT zum 25er-Tageslimit**, nur veröffentlichte Posts. Der Zähler in `posts-<tag>.json -> zaehler` zählt schon nur Veröffentlichte (`eintragen`: nur wenn nicht Entwurf), also keine Code-Änderung nötig. Die Vermutung von 19:35 („Entwürfe zählen mit“) ist damit falsch; der Hänger bei 148-51 auf anduri (23 Posts) war also kein Entwurf-Effekt. Ursache offen, die Limit-Hinweis-Erkennung bleibt aktiv.

**17.11.2026 21:13 – Genauer Wortlaut des Limit-Hinweises (148-32, ella_robinson2, auf „Produkt umbenennen“):** Dialog „Du hast dein heutiges Posting-Limit für Shopping-Videos erreicht.“ / „Du hast das tägliche Posting-Limit erreicht. Richtlinie anzeigen“ mit Knopf „Alles klar“. Laut unserem Zähler hatte ella erst 24 veröffentlichte Posts, TikToks Zählung weicht also ab (z. B. Entwürfe mit Produktlink oder Posts aus anderen Quellen). `limit_hinweis` erkennt den Text (Wort „Limit“) → LIMIT, Account für heute fertig. Der Hänger bei 148-51 (anduri, 23 laut Zähler) war sehr wahrscheinlich derselbe Dialog.

**17.11.2026 21:16 – Banner nach App-Neustart:** Nach dem Schließen mitten in einem Beitrag zeigt TikTok oben „Diesen Beitrag weiter bearbeiten? Entwurf speichern | Bearbeiten“. Der Banner blockierte „Konto wechseln“ (148-17 2× gescheitert). `zur_hauptseite` wischt ihn jetzt nach oben weg (kein Entwurf, nicht bearbeiten).

**17.11.2026 21:25 – Volle Accounts: andere auffüllen (Artur: „Wenn ein Account voll ist, nutz die Möglichkeit und fülle die anderen Accounts auf – nicht einfach liegen lassen“):** Bei `LIMIT <account>` hängt post_mensch das Video und alle restlichen Videos dieses Accounts automatisch auf einen Account mit Platz um (`umverteilen`: Reihenfolge anduri → ella → artur → andreas.testet, nie andreasfastlane; Platz = veröffentlichte Posts heute + schon dorthin umgehängte < 25, andreas.testet < 3; kein Produkt doppelt auf einem Account am selben Tag). Ausgabe `↪ <datei>: <alt> voll → <neu>`, die Videos kommen ans Ende des Laufs. Erst wenn alle voll sind → `✗ … alle Accounts voll, für morgen` → REST-POSTEN. Accounts mit Limit-Hinweis merkt sich `uebergabe/ausgang/limit-<tag>.json` (gilt über Neustarts; TikToks Zählung weicht von unserem Zähler ab, deshalb zählt der Hinweis).

**17.11.2026 21:30 (Artur, Ergänzung Umverteilung):** Die Produkt-Regel gilt nur als Vorrang. Passt ein Video am Ende nur noch auf einen Account, der dasselbe Produkt (anderes Video) heute schon hat, wird es trotzdem dort gepostet. Dieselbe Datei nie doppelt, auf keinem Account (hart: `umverteilen` prüft die posts-Datei, dazu `gepostet.sh pruefen`).

**17.11.2026 21:55 – Showcase-Ausweichweg, „Mehr erkunden“ → App neu, Methoden-Speicher (Artur):** (1) „Wenn es im Showcase drin ist, ist es auch eingespeichert und du kannst es vom Showcase entnehmen“: Reihenfolge jetzt **Einkaufswagen → Showcase → „Jetzt erstellen“**. Neukunden-/Willkommensangebot (Einkaufswagen geht nicht) → beim Verlinken Reiter Showcase, oberstes passendes Produkt (Namensprüfung wie immer, nie suchen); passt es nicht → „Jetzt erstellen“. Ersetzt für diesen Fall „nie im Showcase“. (2) Im „pro Verkauf“-Blatt den ersten Knopf nehmen („Zum Showcase hinzufügen“ bzw. „Jetzt erstellen“). Steht nur „Mehr erkunden“: TikTok komplett schließen (`tiktok_schliessen`), Produkt neu über Social1 → View on TikTok Shop → „pro Verkauf“ → dann sollte „Jetzt erstellen“ kommen (ersetzt die 3× „Blatt zu, pro Verkauf neu“-Schleife; ein Neuladen pro Versuch). (3) Methoden-Speicher `uebergabe/ausgang/methoden.json`, Schlüssel `account|produkt-id` → `{gescheitert: [...], geklappt: ...}`: Einkaufswagen gescheitert → nächstes Mal direkt Showcase; geklappt → direkt diese Methode. Gilt über Neustarts und Tage. Tests isoliert (echter Speicher/Limitliste nie in Tests). Test „Liste per Produkt (Tatort → bof)“ ist rot, weil Tatort nach dem Posten aus der echten bof-Liste raus ist (Testdaten, kein Code-Fehler).

**17.11.2026 22:00 – andreasfastlane als letzter Ausweg (Artur: „Wenn alle anderen nicht gehen, machst du die restlichen Videos bei andreasfastlane“; „alle Videos erst auf den anderen Accounts versuchen … so ist sicher, dass der Account auch voll ist“):** `umverteilen` nimmt andreasfastlane erst, wenn anduri, ella, artur und andreas.testet per Limit-Hinweis voll sind bzw. kein Platz haben (`LETZTER_AUSWEG`). Gleiche Regeln wie immer (Einkaufswagen → Showcase → Jetzt erstellen, Namensprüfung, nie dieselbe Datei doppelt). Ist ein Produkt auf einem Account nicht verlinkbar (nur Käufer-Ansicht), wird es erst auf den anderen Accounts geprüft, dann andreasfastlane.

**17.11.2026 22:05 (Artur: „Nur unsere Exporte“):** Vor jeder Nachholrunde in Fotos aufräumen. „Alles löschen“ heißt dabei: alle Videos, die wir per AirDrop geschickt haben (unsere Exporte, z. B. Video 147/148), NIE die ganze Mediathek. Rohclips und private Videos bleiben. Danach die offenen Videos der Nachholrunde frisch per AirDrop schicken (Eintrag in `airdrop-<stapel>.txt` für diese Videos zurücksetzen, ein zweites AirDrop ist hier ausdrücklich erlaubt).
