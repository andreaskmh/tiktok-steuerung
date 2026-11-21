# Änderungen

- **08.11.2026** – Projekt angelegt: Test-Werkzeuge vom Wisch-Versuch übernommen (`werkzeuge/test/`),
  Fenster-Aufnahme + Zeiger-Werkzeug, Mini-Gerät-Sketch (noch nicht geflasht), Übergabe-Format.
- **08.11.2026** – `geraet/attrappe.py` (Gerät simulieren ohne Arduino), `GERAET_PORT` in `geraet.py`,
  `zeiger` findet `fenster` jetzt auch ohne Pfadaufruf. Getestet: zeiger rel, Protokoll, Wisch-Test komplett mit Attrappe.
- **08.11.2026** – Weg „echtere Software-Eingaben“ getestet (`werkzeuge/test/echt.swift`, `felder.swift`): wirkungslos.
- **08.11.2026** – `vmaus/`: virtuelle Maus über Karabiner-DriverKit-VirtualHIDDevice 8.8.0 (root-Dienst + Socket nur für Artur,
  einmalige Einrichtung per `einrichten.sh`), `geraet.py` spricht auch mit ihr. Der halbe Wisch am Anfang war Arturs Trackpad.
- **08.11.2026** – vmaus eingerichtet (Treiber aktiv, Dienste laufen). Sauberer Test: Ereignisse kommen an, iPhone-Synchronisierung
  ignoriert sie. Scheinbarer Erfolg vorher kam von Arturs Maus. Neu: `werkzeuge/zaehler.swift` (Galerie-Zähler lesen).
  Wichtig: Klicks im Test vermeiden – ein Klick schloss die Galerie (Produktseite mit „Kasse“).
- **08.11.2026** – Korrektur: vmaus FUNKTIONIERT – nach einmaliger echter Trackpad-Berührung („Aufwecken“). Der vermeintliche
  Fehlschlag kam daher, dass ohne Berührung getestet wurde; die Störung war ein Wassertropfen auf dem Trackpad.
  Kalibriert: `SHIFTSCROLL ±7 10` = genau ein Galerie-Bild (9/9 Schritte richtig). Neu: `werkzeuge/galerie.sh`
  (erstes Produkt: Monopoly FC Bayern, 4/4 Bilder). `aufnahme.sh` nimmt erst temporär auf (screencapture darf nicht nach ~/Documents).
- **08.11.2026** – Aufwecken ohne Finger: kurze virtuelle Mausbewegung im iPhone-Fenster vor jedem Wisch (7/7 ohne Artur).
  In `galerie.sh` eingebaut.
- **08.11.2026** – Erste zwei Posts über das System (Schokoellsen → artur.official, Powerbank → anduri.official), beide mit
  orangenem Button geprüft. iPhone 11: hohe Qualität an, „Auf Gerät speichern“ aus (einmalig erledigt).
- **08.11.2026** – Doppel-Schutz `werkzeuge/gepostet.sh` (pruefen/eintragen, erkennt Videos per Prüfsumme auch unter anderem
  Namen; Liste `uebergabe/ausgang/gepostet.txt`). Schokoellsen + Powerbank nachgetragen. Grund: Artur will keine doppelten Uploads.
- **08.11.2026** – `werkzeuge/tipp.swift`: Klick mit Touch-Kennung (Feld 7 = 3, Druck, Feld 108 = 1) direkt an die
  iPhone-Synchronisierung, damit Artur nicht mehr ins Feld „Produktname“ tippen muss. Noch ungetestet (Test beim nächsten Upload),
  Reserve: `CLICK` der virtuellen Maus. ACCOUNTS.md: artur.official möglichst wenig.
- **08.11.2026** – `werkzeuge/tap.py` (Tipps mit der virtuellen Maus: Zeiger setzen + kleine echte Bewegung + CLICK → sitzt beim
  ersten Mal, anders als app_click) und `werkzeuge/upload.py` (feste Upload-Abschnitte start/link/publish/like am Stück). Grund: Speed.
- **09.11.2026** – Letzte 2 Videos vom Stapel 08.11. auf artur.official gepostet (Tunnelblick, Rock Shorts). 5-Minuten-Regel aus
  CLAUDE.md, ABLAUF, UEBERGABE und ACCOUNTS entfernt: Artur will keinen Abstand (stand nur in der Memory, CLAUDE.md widersprach).
- **09.11.2026** – Tempo: `werkzeuge/text.swift` (Texterkennung, 0,3 s), `werkzeuge/seh.py` (Fenster lesen/Text finden) und
  `werkzeuge/posten.py` (ganzer Stapel in einem Befehl, prüft jeden Schritt selbst, bricht bei Unklarem mit STOPP ab).
  Grund: jedes Zwischenfoto kostete eine Rückfrage an Claude. Herz/Lesezeichen werden über „Teilen“ gefunden (Lage
  verschiebt sich mit/ohne Shop-Button). Tippen etwas schneller (45–140 ms). Shop-Button/Like/Speichern werden nicht
  mehr kontrolliert. Kontext-Regel ab ~500k in CLAUDE.md. Noch nicht live getestet (iPhone war gesperrt).
- **09.11.2026** – posten.py: ausverkauft → Entwurf ohne Link; `schnell()` für Links/Suche (langsam nur in TikTok).
  Neu `werkzeuge/stock.py` (unfertig, siehe STAND). Regeln Showcase voll (Artur fragen) / Einkaufswagen voll (egal was
  entfernen) in CLAUDE.md.
- **09.11.2026** – Sync aufs 2. MacBook (`werkzeuge/sync.sh`, Repo andreaskmh/tiktok-steuerung, Gedächtnis in `gedaechtnis/`,
  Doppel-Schutz-Liste + Logs werden mitsynchronisiert). Kopplung mit dem Editing System (mit Nicolas abgeklärt):
  `stock.py` fertig (Vorschaukarte hochziehen), `einreichen.py`, `eingang.py liste|freigeben|posten`, Brücke im Editing System
  `eigene/TIKTOK-STEUERUNG.md`. posten.py: Brand-Nutzername optional, wenn eindeutig.
- **09.11.2026** – `werkzeuge/social1.py`: liest eine Social1-Liste am Mac (Safari, nur lesen) komplett aus (Produktname,
  Produkt-ID aus dem Produktbild, Video-ID, Creator, Vorschaubilder). Grund: Artur schickt nur die Liste, Claude ordnet
  jedes Video selbst zu (Brücke im Editing System §0). Test: „bof 2.0“ 110/110 mit ID.
- **09.11.2026** – `social1.py --listen` (alle Social1-Listen, neueste zuerst) für die Start-Umfrage im Editing System
  (/bof usw. fragen Videoordner + Social1-Liste als Auswahl ab; Ordner-Helfer dort `eigene/ordner-auswahl.sh`).
- **09.11.2026** – 2. MacBook (Artur K) eingerichtet: Repo geklont, `sync.sh einrichten` (Gedächtnis, Werkzeuge, vmaus gebaut),
  Karabiner-Treiber aktiv, Dienste laufen (`OK pointing=1 keyboard=1`), Freigaben erteilt (Bedienungshilfen für „claude“ klein nötig).
  Getestet: `seh.py` liest das iPhone, `tap.py safe` ok, Tipps kommen an. **Damals offen (siehe nächster Eintrag gelöst):** `stock.py` stoppte, weil
  Ziehen/Scrollen der virtuellen Maus hier nicht wirkt (Details und erfolglose Versuche: `vmaus/ANLEITUNG.md` Schritt 6).
  Editing System auf diesem Mac von ~/Downloads nach ~/Documents/Coding verschoben (gh-Pfad in ~/.gitconfig angepasst).
- **09.11.2026** – 2. MacBook: Stock-Test läuft (Hosenrock 2/2). `stock.py` schiebt die Produktkarte notfalls per Mausrad hoch
  (`SCROLL 0 ±10 15`, Richtung nach „Natürliches Scrollen“), falls Ziehen nicht wirkt. Grund: auf dem 2. MacBook wirkte
  Ziehen zeitweise nicht; kleine Rad-Mengen (3 Rasten) täuschten einen Defekt vor. ANLEITUNG Schritt 6 aktualisiert.

## 10.11.2026 (Claude, Video 139)
- `werkzeuge/post_wagen.py` neu: Stapel posten mit Arturs Regel „erst Showcase über Social1, Einkaufswagen NUR wenn schon im Showcase“; beim Verlinken „Weitere Produkte hinzufügen → Einkaufswagen“, oberster Eintrag + Stichwort. Galerie von unten nach oben durchsuchen (OCR-tolerant: 14€→14C, Ä→A, Emoji weg). Account-Wechsel über „Konto wechseln“.
- Tastenanschläge kamen am iPhone oft nicht an, ⌘V schon → Texte per Einfügen (Adressleiste, Button-Text, Beschreibung).
- iPhone-Fenster wieder auf x=700 (dort lief der Drag in Fotos); Fotos muss in der Mediathek stehen, nicht in der Suche.
- Kachel = Text ohne Emoji; Produkt-Feld = Stichwort, das im (abgeschnittenen) Showcase-/Wagen-Titel steht.
- posten.py/eingang.py unverändert (Claude-Versuche als *.claude-1110 gesichert).

## 11.11.2026 – Umstellung auf Kabel (open-iphone-use)
- open-iphone-use (github.com/semsturgut/open-iphone-use, Stand 719bd55) nach `~/Documents/Coding/extern/open-iphone-use` geklont und
  per `sh setup.sh` installiert (`~/.local/bin/open-iphone-use`, MCP + Skill bei Claude Code angemeldet). Warum: iPhone per USB über
  Xcodes CoreDevice steuern (genaue Tipps, Live-Bild) statt iPhone-Synchronisierung + virtueller Maus. Braucht Xcode 27 + iOS 27, Entwicklermodus.
- Platz für Xcode: 2.097 Video-/Tondateien (118,8 GB) aus Editing System `Videos/Archiv` und `Videos/Fertige Videos` gelöscht (Artur OK,
  alles hochgeladen). Texte/Protokolle/Vorlagen blieben. Liste: Editing System `eigene/geloescht-2026-11-11.txt`.
- 12.11.: iPhone 11 („iPhone von Artur (2)“) auf iOS 27.2.1, Entwicklermodus an, in open-iphone-use als Gerät
  `cd6297a30ec147bb88a5f37763d805ae` eingebunden. Verbunden über **WLAN** (USB wird vom Mac noch nicht erkannt → Kabel prüfen).
- Fehler behoben: `oiu/coredevice.py` `_broadcast_frame(self, bgra)` → `(*args)`, weil pymobiledevice3 11.52 jetzt
  (bild, breite, höhe, drehung) übergibt; sonst kein Live-Bild. Gepatcht in installierter Kopie + Klon (bei Neuinstallation wieder nötig).
- Getestet: Foto (`GET /api/devices/<id>/frame`, 832×1808), Tippen (Uhr-App), Home-Taste, Wischen links – alles ok.
- 12.11.: Kabel wird jetzt erkannt (USB). Nach Server-Neustart (`open-iphone-use stop` + `serve`) läuft das iPhone über USB
  (6 Mbit/s statt 2 über WLAN). Wechselt nicht von selbst von WLAN auf USB → nach dem Einstecken Server neu starten.
  Stream-Bild 832×1808 ≈ volle iPhone-11-Auflösung (828×1792).
- 12.11.: **Kabel-Schicht gebaut.** `werkzeuge/kabel.py` (Tippen, Ziehen, Tasten, Text mit deutschem Layout inkl. Umlaute/#/@,
  Einfügen per gemeinsamer Zwischenablage, verlustfreie Fotos). `seh.py`, `tap.py`, `posten.py`, `post_wagen.py`, `stock.py`
  nehmen automatisch das Kabel, sobald `open-iphone-use serve` läuft (sonst wie bisher iPhone-Synchronisierung; erzwingen: `TS_MODUS=sync`).
  Punkte bleiben Breite 334 (Kabel-Höhe ≈ 726 statt 735 → feste y-Werte unten ggf. ein paar Punkte daneben, beim 1. Post prüfen).
  Server-Erweiterung `werkzeuge/kabel/patch_oiu.py` (drag, hid, PNG) – nach jeder Neuinstallation von open-iphone-use erneut ausführen.
- 12.11.: Stock per Kabel getestet: Hosenrock 2/2 in 41 s, verlustfrei 832×1808 PNG (`uebergabe/ausgang/test-kabel-hosenrock`).
- 12.11.: Video aufs iPhone (bisher Ziehen in die iPhone-Synchronisierung) noch offen. AirDrop-Versuch (`werkzeuge/airdrop.swift`):
  Empfänger heißt nur „Artur“ – Testclip (blau.mp4) kam NICHT in den Fotos dieses iPhones an → anderes Gerät?
- 12.11.: AirDrop am iPhone 11 auf „Nur für Kontakte“ (Artur OK) → Mac sieht „iPhone von Artur (2)“, Video kommt ohne Abfrage
  in Fotos (11 s). `werkzeuge/airdrop.py` + `airdrop.swift`, in `eingang.py aufs_iphone` eingebaut. Testclip wieder gelöscht.
- 12.11.: Kabel-Punkte auf 334×735 (wie altes Fenster) → feste Koordinaten in posten.py treffen (Profil, „+“, Galerie geprüft).
  Doku: neu `docs/KABEL.md`, CLAUDE.md/ABLAUF.md/STAND.md angepasst.
- 12.11.: Probelauf 1 gestoppt: ⌘V fügte am iPhone noch die ALTE Zwischenablage ein (Sync Mac→iPhone > 1,5 s) → Safari suchte
  bei Google statt Social1. Kabel tippt jetzt alles (Links schnell, TikTok-Texte menschlich); Zwischenablage nur noch für Emojis (`kabel.schreibe`).
- 12.11.: Probelauf 2 gestoppt: fester Tipp (241,686) in Safari traf das Mikrofon → Diktierfunktion (geschlossen, nicht aktiviert).
  Kabel: Adressleiste jetzt per ⌘L (post_wagen.in_wagen, stock.zur_galerie).
- 12.11.: Probeläufe 3–5: Werbeaktions-Blatt schließen jetzt relativ zum Titel; TikTok-Kopfbereich per Kabel ~35 Pkt höher
  (`posten.oben()`: X/Zurück, Beschreibungsfeld, Sound-Hinweis, Galerie-X in stock.py); Kamera-Hinweis nur noch, wenn OK-Knopf da
  (per Kabel läuft die Kamera wirklich, „KAMERA“ unten löste den falschen STOPP aus).
- 12.11.: Ursache „markiert alles / geht beim Tippen zurück“ (Artur): iPhone-**Tastatursteuerung** (Bedienungshilfen) war noch an
  (von der iPhone-Synchronisierung) → Leertaste drückte den fokussierten Zurück-Knopf. Auf Arturs Wunsch ausgeschaltet; alle
  Bedienungshilfen geprüft (alles „Aus“, AssistiveTouch aus).
- 12.11.: **Probelauf ganzer Post per Kabel erfolgreich** (Video 139/01 BotaBay auf anduri.official, als ENTWURF gespeichert,
  nicht veröffentlicht): AirDrop → Einkaufswagen → Hochladen → Link „Wenige auf Lager“ → Beschreibung → Entwurf.
  Behoben unterwegs: Galerie-X/Zurück y=61, Kamera-Seite schließen (x=24), tolerante Link-Prüfung (`seh.aehnlich`, OCR „aut“/„auf“).
  Brand „BotaBay Perfume“ ohne handle nicht eindeutig → ohne Brand (wie vorgesehen); fürs echte Posten handle in der JSON nachtragen.
- 12.11.: Menschliches Tippen schneller (Artur): Häppchen von 2–5 Zeichen, 25–70 ms Abstand, selten kurze Pausen.
- 12.11.: Profil immer auf den linken Reiter **Beiträge** (neueste Videos) statt Shop/Showcase (Artur: übersichtlicher).
  `posten.beitraege()` – tippt nur, wenn ein anderer Reiter offen ist (2. Tipp öffnet sonst das Sortiermenü); in posten.profil und post_wagen.profil.
- 12.11.: `eingang.py posten` = ein Befehl für alles: AirDrop aller Videos, dann pro Video `post_wagen.ein_post` (getesteter Weg,
  Showcase zuerst/sonst Wagen); nur „ausverkauft“ läuft weiter über posten.py (Entwurf ohne Link). Vorher nutzte es nur den alten Showcase-Weg.
  Brücke im Editing System (`eigene/TIKTOK-STEUERUNG.md`) auf Kabel/AirDrop angepasst (dort nicht committet).
- 12.11.: **Tempo:** Tipp 0,95 s → 0,24 s (Server: ruhendes Bild alle 0,15 s statt 0,5 s, patch_oiu.py Nr. 5); feste Wartezeiten
  per Kabel × 0,6 (`TS_WARTE`, tap.py; =1 setzt zurück, falls etwas zu schnell ist – Prüfungen per Texterkennung bleiben).
  `stock.py --stapel liste.json`: viele Produkte, eine Zeile je Produkt, Fertige übersprungen (Test: BotaBay 11 Bilder in 51 s).
  Kontext-Regeln in CLAUDE.md + Brücke (Hintergrund, nur Endzeilen, Übergabe an frische Session alle ~20 Videos).
- 12.11.: Probe-Post mit Wartezeiten × 0,6: 124 s komplett, kein Stopp.
- 12.11.: Wächter `werkzeuge/kabel/waechter.py` + `kabel/autostart.sh an|aus|status` (LaunchAgent): Server automatisch starten, bei Kabel von WLAN auf USB wechseln. Getestet: Server gestoppt → nach 20 s wieder da. Autostart einrichten muss Artur selbst (Freigabe).
- 12.11.: Werkzeuge starten den iPhone-Server selbst, wenn er fehlt (kabel.aktiv, getestet 4 s); Brücke im Editing System prüft bei Chat-Start (`waechter.py einmal`). Autostart damit optional.
- 12.11. abends: **`werkzeuge/post_mensch.py`** – Posten nach Arturs Bildschirmaufnahmen (docs/POSTEN-MENSCH.md): Social1-Produktseite →
  View on TikTok Shop → Showcase („pro Verkauf“) sonst Wagen → + → Galerie → Beschreibung (1 Produkt-Hashtag + 3 Pflicht) → Link →
  Brand nur mit Konto → Veröffentlichen (erst kräftig rot) → Social1-Lesezeichen am Mac abhaken. Jeder Schritt per Text-Label,
  Gefahren-Sperre bei jedem Tipp (Kasse/LIVE/Konto hinzufügen/Delete, CAPTCHA → STOPP), kein Tipp oben links im Feed (LIVE-Symbol –
  Ursache der LIVE-Event-Seite heute). `bin/pixel` (pixel.swift): „+“-Erkennung und rote Knöpfe. `eingang.py posten` ruft es auf
  (alt: `TS_ALT=1`). Test als Entwurf: Showcase-Weg ~91 s, Wagen-Weg 116 s am Stück. Fotos-Löschen noch aus (ungetestet).
- 12.11. 22:40: Fotos-Löschen in post_mensch fertig (Kachel per Text in der Mediathek, Mülleimer bis 4×), gesammelt am Stapel-Ende; `--fotos <stapel>`.
- 16.11.2026 17:05 – **Drei Produkt-Szenarien nach Arturs Bildschirmaufnahmen** (szenario1–3.mp4; Backups `*.bak-20261116-szenarien`):
  (1) Neukunden-Erkennung nur noch beim echten Hinweis („1 Option pro Artikel … Schaltfläche Kaufen“) – vorher lösten
  „Funde für Neukund*innen“ (Shop-Reiter) und Ähnliches fälschlich den „Jetzt erstellen“-Weg aus. (2) Einkaufswagen: nach dem
  grauen Knopf erst das Ergebnis abwarten (Toast „hinzugefügt“ / Neukunden-Hinweis / Varianten-Blatt); vorher wurde der graue
  Knopf bei Produkten ohne Varianten ein 2. Mal gedrückt. (3) Showcase-/Wagen-Liste erst nach „Wird geladen“ und mit zwei
  gleichen Bildern entscheiden (Szenario 1 zeigte kurz die alte Reihenfolge). (4) Blatt „Hinzufügen von“: nur „Einkaufswagen“
  (darunter verdeckt „Gekaufte Produkte“). (5) Werbe-Blatt schließen, bis Kasse + Einkaufswagen frei stehen. (6) „+“: Produktseite
  über die Zustandsmaschine schließen (kein Wisch auf Höhe 400 mehr). (7) Szenario 3: X am Blatt „Wie möchtest du …“ relativ
  zum Titel, kurze Toasts nicht sofort als Fehler, Produktname nicht änderbar (2. Durchlauf) → nach ~5 s Standard-Namen
  behalten, nach dem Speichern sofort zurück zur Hauptseite. Tests 166/166 (neu `test_szenarien`), Tests sperren jetzt das
  echte iPhone (Kabel-Aufrufe brechen ab). Noch nicht am iPhone gelaufen → erster Lauf als `--entwurf`.
- 16.11.2026 17:22 (Artur: „warum schreibst du so langsam“): menschliches Tippen etwa doppelt so schnell – weiter jedes Zeichen
  einzeln, Pause 60–150 ms (Leerzeichen +40–150 ms, 4 % Denkpause 0,3–0,7 s) statt 120–300 ms. Backup `kabel.py.bak-20261116-tippen`.
- 16.11.2026 17:28 (Artur: „übernimm meine Tippgeschwindigkeit aus den Aufnahmen, menschlich mit kleinen zufälligen Pausen“):
  ersetzt 17:22. Seine Aufnahmen: ~9–10 Zeichen/s. Bremse war ~0,3 s Rückmeldung je Befehl bei jedem einzelnen Buchstaben
  (45 Zeichen ≈ 40 s). Jetzt Wortstücke von 2–6 Zeichen in einem Befehl, Tastenabstand zufällig 30–90 ms (Server-Argument
  `pause`), zwischen Stücken 40–160 ms (+ bei Leerzeichen, 5 % Denkpause 0,25–0,6 s) → ~5–7 Zeichen/s. Tests angepasst.
- 16.11.2026 17:30 (Artur: „schon falsch gehandelt, du hast den Produktnamen nicht geändert – jetzt kannst du es nicht mehr“):
  Abkürzung „Name nach ~5 s unverändert → nicht änderbar, Standard-Namen behalten“ (17:05) wieder entfernt – das Feld WAR
  änderbar, die Eingabe kam nur verzögert an. Übersprungen wird nur noch, wenn kein Namensfeld/Zähler erscheint (wie 15.11.).
- 16.11.2026 17:35 (Artur: „das Umbenennen hat nicht geklappt“, Fanttik, Szenario 3 simuliert): Prüfung meldete „umbenannt“,
  weil der Zähler 16/30 zur Länge von „Wenige verfügbar“ passte – der alte Name „E1 Max Schrauber“ hat auch 16 Zeichen.
  Jetzt zählt der Zähler nur, wenn sich der Feldtext gegenüber vorher geändert hat (`name_ok(…, alt)`). Test ergänzt.
  Außerdem: Test-Schalter `"weg": "erstellen"` in der Eingang-JSON erzwingt den „Jetzt erstellen“-Weg (Szenario 3 üben).
- 16.11.2026 19:30 (Artur: „einfach aufs transparente X unter ‚Jetzt anfordern‘ klicken, falls sowas wieder kommt“):
  Popup „Jetzt anfordern“ (verdeckte das „pro Verkauf“-Badge → Produkt wurde 3× neu über Social1 geöffnet) = neuer Dialog
  `DLG_ANFORDERN` → Tipp aufs X darunter (gelesenes ×, sonst 60 Pkt unter dem Knopf), nie auf „anfordern“; Foto
  `anfordern-*.png` als Beleg. Wird auch beim Warten aufs Badge weggedrückt. Tests 172/172.
- 16.11.2026 19:35 (Artur: „du klickst das Textfeld am Anfang weg, deswegen kannst du nicht reinschreiben“): Umbenennen –
  ist die Tastatur schon offen (Feld aktiv), wird NICHT ins Feld getippt, direkt ⌘A → Löschen → Name. Vor dem Feld-Tipp
  Bildschirm frisch lesen (Hinweisband „Überprüfe die Qualität …“ verschiebt das Feld nach dem Laden). Name im Feld war der
  KI-Vorschlag „E1 Max Schrauber“.
- 16.11.2026 19:55 – **Tempo, ohne Prüfungen anzutasten** (Backups `*.bak-20261116-speed`, `kabel/patch_oiu.py.bak-20261116-tippen`):
  (1) Zeitbuch `TS_ZEITBUCH=1`: je Log-Zeile Warten / Bild lesen / Eingaben. (2) Server-Patch 6 (`patch_oiu.py`): hid-Argument
  `halt` = Taste nur kurz gedrückt (vorher fest ~0,1 s je Taste). Tippen in TikTok: Wortstücke 4–10 Zeichen, Taste 25–35 ms,
  Abstand 15–50 ms, kurze zufällige Pausen → Beschreibung 13–16 s statt 23 s (vorher 40 s). Löschen 60× ≈ 2 s statt 6 s.
  Adressleiste/Suche: halt 0,035 + 15 ms Abstand (mit 0,02 ohne Abstand verlor die iOS-Suche Zeichen). Server nach Patch neu
  starten. (3) Fehler unterwegs behoben: Blatt „Hinzufügen von“ – OCR liest „: Einkaufswagen“ (genaue Suche fand nichts →
  60 s Hänger); Home-Bildschirm mit TikTok-Widget „What Live do you want to watch?“ galt als LIVE-Seite → jetzt Home (Widget
  bleibt gesperrt); Showcase-Seite „Entdecken | Verwalten“ galt als Feed → eigene Seite, Zurück-Pfeil; „Mehr erkunden“ wird nie
  angetippt. Unverändert: Doppel-Schutz, Kachel-/Cover-/Beschreibungs-/Produkt-/Schluss-Prüfung, Gefahren-Sperre. Tests 177/177.
- 16.11.2026 20:00 – **Bild lesen schneller:** neuer `werkzeuge/textdienst.swift` (bleibt laufen, Erkennung bleibt geladen;
  gleiche Einstellungen wie `text`: accurate, de+en, ohne Sprachkorrektur – Ausgabe am Testbild identisch). `seh.lesen` nutzt
  ihn automatisch, fällt bei Problemen auf `bin/text` zurück (`TS_OCR=alt` erzwingt den alten Weg). Gemessen im Lauf:
  ~0,22 s statt ~0,4–1,0 s pro Bild. Roxlin (Einkaufswagen, Entwurf) 91 s statt 120 s (Mittag 139 s). `bin/` ist nicht im
  Git → auf dem 2. MacBook nach `sync.sh holen` einmal `zsh werkzeuge/build.sh`. Backup `seh.py.bak-20261116-ocr`.
  Hinweis: Bei hoher Mac-Last (Load 18–20 durch macOS-KI-Dienste) wird jedes Lesen langsamer.
- 16.11.2026 20:10 – **Tempo 3 (Artur: Social1 → Produktseite + Umbenennen, „wenn damit kein Fehler passiert“)** (Backup
  `post_mensch.py.bak-20261116-speed2`): feste Pausen nach „View on TikTok Shop“ (2,0 → 0,8 s) und „Öffnen“ (2,5 → 1,0 s),
  Link-Navigation (Link hinzufügen / Produkt / Weitere Produkte / Einkaufswagen 1,0–1,4 → 0,6–0,7 s), „Jetzt erstellen“-Hinzufügen
  (3,0 → 1,5 s), Umbenennen (Pausen 0,8/0,9/0,6 → 0,3/0,6/0,4). Neu: Doppel-Tipp-Schutz `kuerzlich()/merke()` – dasselbe Label
  wird innerhalb von 2,5–4 s nie ein zweites Mal angetippt (auch „Hinzufügen“ nach dem Umbenennen). Namens-Prüfung schaut alle
  0,5 s statt 1,0 s nach, gleiche Gesamtzeit. Unverändert: Auswahl von Video und Listen-Produkt, alle Prüfungen.
  Probelauf (Entwürfe, mit 2 Kontowechseln): Fanttik „Jetzt erstellen“ 87 s (vorher 106), Roxlin Einkaufswagen 99 s inkl.
  Kontowechsel (vorher 120 ohne). `zlog()`: Zwischenzeiten in zum_produkt nur mit TS_ZEITBUCH=1.
- 16.11.2026 20:20 (Artur: „ab sofort auch ein einfacher kurzer simpler Beschreibungstext, nicht komplex, nicht unbedingt
  Emojis, alles kleingeschrieben, nicht nur die Hashtags“; ersetzt „nur Hashtags“ vom 15.11.): Beschreibung = kurzer Text +
  Hashtags. Text aus Eingang-JSON `text` (neu: `einreichen.py --text "…"`), sonst neutraler Standardsatz (`KURZTEXTE`).
  Immer klein, ohne Emojis/#, ≤ 8 Wörter; Preis/Versprechen (VERBOTEN) → Standardsatz. Beschreibungs-Prüfung am Bildschirm
  unverändert (alle Wörter + Hashtags müssen dastehen). Backups `*.bak-20261116-text`. Nicht am iPhone getestet (Artur: kein Test).

- 16.11.2026 21:52 – Badge fehlt: kein Scrollen mehr (badge_scrollen nicht mehr aufgerufen), stattdessen bis 10× neu über Social1 öffnen, bis „pro Verkauf“ erscheint (Artur: „einfach von Social1 aus nochmal öffnen bis es angezeigt wird, kein Scrollen“). Backup post_mensch.py.bak-20261116-badge.
- 16.11.2026 22:00 – Variante nicht vorrätig: Gruppen-Titel jetzt auch „Fall:“/„Sorte:“ usw. (jede „Name:“-Zeile), Varianten ohne Text als Bildkacheln nebeneinander antippen (Artur: „nimm doch einfach die andere Variante“, Tatort). Backup post_mensch.py.bak-20261116-variante.
- 16.11.2026 22:05 – Varianten-Blatt mit „Fall:“ + „nicht vorrätig“ wurde nicht erkannt („unbekannt“) → nie weggewischt, Lauf hing. bildschirm.VARIANTEN erkennt jetzt auch „nicht vorrätig“ und jede „Name:“-Gruppe. Backup bildschirm.py.bak-20261116-variante.
- 16.11.2026 22:05 – Kein „pro Verkauf“-Badge (nach ~8 s Warten) → nicht mehr neu über Social1 öffnen, sondern direkt Einkaufswagen-Weg (F["nur_wagen"]), Artur: „damit wir keine Zeit verlieren … packs einfach in den Einkaufswagen“. Backup post_mensch.py.bak-20261116-ohnebadge.
- 16.11.2026 22:12 – Galerie-Hook OCR-tolerant (_passt: Ähnlichkeit ≥ 85 %, ab 10 Zeichen): „ANHÄNGER“ als „ANMANGER“ gelesen → HOTU-Kachel nie gefunden, Lauf hing 8 min. Backup post_mensch.py.bak-20261116-ocrhook.
- 16.11.2026 22:16 – beschreibung_stimmt: zwei benachbarte OCR-Stücke zusammen vergleichen („#digita kamera“ = #digitalkamera am Zeilenumbruch), HOTU war fälschlich gesperrt. Fremde Hashtags weiter streng. Backup post_mensch.py.bak-20261116-beschr.
- 16.11.2026 22:22 – „Dieses Produkt ist nicht provisionsberechtigt“ auf der Produktseite → sofort Entwurf ohne Link (Regel 12.11.), vorher: kein Badge → Wagen → Neukunde → „Jetzt erstellen“ ohne Badge → Hänger (House of Thêom).
- 16.11.2026 22:25 – Galerie: Video nach 15 s (erst 40, Artur: zu lang) nicht da → einmal nochmal per AirDrop (Artur: „wenn der AirDrop nicht zuverlässig ist bzw. lange dauert, airdrop nochmal“). Backup post_mensch.py.bak-20261116-airdrop2.
- 16.11.2026 22:36 – Hinweis: SOCIAL1_LISTE ist fest auf bof 2.0; beim Stapel 2026-11-16-bof (Liste „bof“) griff das Abhaken nicht („keine-liste“) → nachträglich mit TS_SOCIAL1_LISTE=6afb1c70204ef09999b79488. Zweiter Abhaken-Klick aufs gleiche Produkt braucht vorher Neuladen.
- 16.11.2026 22:45 – Social1-Abhaken in der Liste, die beim Schneiden gewählt war (Artur: „nicht nur bof 2.0“): einreichen.py --liste <name|link|id> → `social1_liste` in der JSON; fehlt sie, sucht post_mensch.liste_fuer() die neueste ausgang/social1-*.json mit dem Produkt; Liste nicht offen → wird im Mac-Safari geöffnet; nach jedem Abhaken neu laden (2. Klick aufs gleiche Produkt). Backups *.bak-20261116-liste.
- 16.11.2026 22:55 – Neue Social1-Liste „nicht verfügbar“ (ID 6afb797b0db9dac6d93b5ccf, von Claude angelegt). Entwurf ohne Link (ausverkauft/nicht provisionsberechtigt) → `social1_verschieben()`: Vorbild aus der Arbeitsliste raus, Haken bei „nicht verfügbar“ (fehlt die Liste: wird angelegt). House of Thêom (Video 145-03) von Hand verschoben. Backup post_mensch.py.bak-20261116-nv.
- 16.11.2026 23:05 – **stock.py prüft die Postbarkeit schon beim Stock-Holen** (Anlass: Video 03 House of Thêom fertig
  geschnitten, dann nur Entwurf, weil „nicht provisionsberechtigt“). Backup `stock.py.bak-20261116-check`. Auf der Produktseite
  wird nur GELESEN (vor und nach dem Hochziehen der Karte, kein zusätzlicher Tipp): `produkt.json` bekommt
  `"status": {"provision", "vorraetig", "neukunden", "hinweis"}` (true/false/null). „Verdiene … pro Verkauf“ → provision true,
  „nicht provisionsberechtigt“ → false; „nicht vorrätig“/„ausverkauft“ → vorraetig false; Seite „Artikel/Produkt nicht
  verfügbar“ → keine Galerie, `produkt.json` nur mit Status (bilder leer); „Angebot für Neukund*innen“/„Neukunden-Angebot“ →
  neukunden true (Neukunden-Preis auf der Seite, KEIN Hindernis; den Einkaufswagen-Hinweis sieht man erst beim Tipp).
  `--stapel`-Zeile: `✓ kurz: 5 Bilder, 31 s ⚠ nicht provisionsberechtigt (Neukunden-Angebot)`. Social1-Namensprüfung robuster
  (`name_passt`: Akzente egal, Titel mit „…“ als Namensanfang, sonst die ersten zwei Namenswörter in einer Zeile; einzelnes
  Wort nur bei einwortigen Namen). Feste Pausen um das Hochziehen 1,5+1,5 → Badge-Warteschleife (0,4 s) + 1,0 s.
  Test: Thêom provision false, PS5-Akku + Pukka provision true; je ~31–39 s (alt 36–41 s).
- 16.11.2026 23:30 – **Tempo ohne Hänger (Bericht Video 145, Ziel ~1,5–2 min je Video), keine Prüfung entfernt** (Backups
  `post_mensch.py.bak-20261116-tempo2`, `airdrop.py.bak-20261116-tempo`, `bildschirm.py.bak-20261116-tempo`,
  `test/test_posten.py.bak-20261116-tempo2`; nur offline getestet, iPhone nicht benutzt):
  (1) **AirDrop:** Ankunft gilt nur noch als „gesehen“, wenn Fotos am iPhone aufgeht (`airdrop.angekommen` → „fotos“/„mac“;
  „kaum Text nach 9 s“ nur, wenn sich der Bildschirm seit dem Senden geändert hat); Wartezeit 40 s statt 90 s; kommt es nicht
  an → **sofort** nochmal (noch vor TikTok, `airdrop_einmal`), statt erst in der Galerie nach 15 s. Neue Merkliste
  `ausgang/airdrop-<stapel>-da.txt` (Ankunft gesehen): nur die verhindert ein zweites AirDrop – „angeklickt“ allein
  (`airdrop-<stapel>.txt`/`letztes-airdrop.txt`) meldete bei 145-04 fälschlich „schon am iPhone“. Höchstens 2 AirDrops je
  Video und Lauf. Galerie-Fallback: nach dem 2. AirDrop zurück in TikTok (`_zurueck_in_tiktok`, „◂ TikTok“; Fotos-Bildschirme
  im Galerie-Weg → zurück statt Hänger „unbekannt“ wie bei 145-08), nach 10 s ohne Kachel Galerie einmal neu öffnen;
  Warten in der Galerie 2 s statt 5 s je Runde (nur Lesen). `_ist_app("TikTok")` erkennt Kamera/Galerie/Vorschau/Editor.
  (2) **Varianten nicht vorrätig:** neue reine Funktion `varianten_optionen()` – Gruppe nie „Menge:“, Optionen nur über
  „Menge“/Hinweis/rotem Knopf, nie „+“/„-“/Menge/Preis (vorher hätte „+“ die Menge erhöht); Bildkacheln nur, wenn die Gruppe
  gar keine Text-Optionen hat. `bildschirm.VARIANTEN` zusätzlich: „Menge:“ + Gruppe/„nicht vorrätig“ ohne Kasse unten (falls
  der rote Knopf anders heißt) – an allen 646 + 768 gespeicherten Bildschirmen keine Abweichung zu vorher.
  (3) **Hook-OCR:** kurze Hooks (6–9 Zeichen) dürfen genau 1 Buchstaben abweichen (vorher gar keine Toleranz); Cover-Prüfung
  liest den Hook auch über 2–3 Zeilen zusammen. Länge ±1 s, fremde Hooks und Beschreibungs-Prüfung unverändert streng.
  (4) **Social1:** kein Neuladen mehr nach jedem Abhaken; abgehakte Karten werden markiert (`data-ts-ab`) und übersprungen
  (2. Video desselben Produkts); ist der Haken schon raus (Seite veraltet) oder die Karte fehlt → einmal neu laden, nochmal.
  „abgehakt“ nur, wenn ein gesetzter Haken wirklich entfernt wurde. Dialog/Haken werden abgewartet statt fester 1,2/0,8 s.
  Abhaken läuft im Hintergrund parallel zum nächsten Video (Mac-Safari, immer nur eins gleichzeitig, am Ende abgewartet).
  `--entwurf` verschiebt nichts mehr in Social1 („nicht verfügbar“ nur bei echten Läufen).
  (5) **Feste Pausen → Warten auf den nächsten Bildschirm** (`warte_bildschirm`, höchstens so lange wie die alte Pause):
  „+“, Galerie öffnen, Kachel → Vorschau, Weiter → Editor/Beitrag, Editor → Beitrag, „Jetzt erstellen“, „Videos“.
  Kachel wird erst angetippt, wenn sie in zwei Bildern gleich liegt (Galerie fährt ein). „pro Verkauf“ 1,6 → 0,6 s (Schleife
  wartet), Listen-„Hinzufügen“ 1,4 → 0,6 s, Dialog „Hinzufügen“ 1,4 → 0,7 s mit Doppel-Tipp-Schutz, rotes „Hinzufügen“
  1,2 → 0,6 s (Schutz 3 s bleibt), Veröffentlichen: Pause davor 0,3–0,6 s statt 1,0–1,8 s (wartet weiter auf kräftig rot,
  bis 5 statt 3 Runden), danach warten bis der Knopf weg ist (bis 4 s) statt fest 2,5 s – nochmal getippt wird erst nach 4 s.
  Entwürfe ebenso. Unverändert: „Zum Showcase hinzufügen“ (Showcase-voll-Prüfung), Account, Rückwege (zur_hauptseite).
  Tests 201/201 (neu `test_tempo_16_11`). Erst beim nächsten echten Lauf prüfbar: AirDrop-Erkennung/Nochmal, Social1 im
  Hintergrund + Markierung, Galerie-Neu-Öffnen, die kürzeren Übergänge.

## 16.11.2026 23:45 – Jedes MacBook hat sein eigenes iPhone (Artur)
- `kabel.py`, `kabel/waechter.py`, `airdrop.py` lesen das iPhone jetzt aus `~/.config/tiktok-steuerung/geraet.json`
  (`udid`, `airdrop_ziel`) – liegt nur auf dem jeweiligen Mac, nicht im Git. Ohne Datei gilt wie bisher das iPhone 11
  `…C3402E` / „iPhone von Artur (2)“. Umgebungsvariablen `TS_IPHONE_UDID` / `TS_AIRDROP_ZIEL` gehen weiterhin vor.
- MacBook Pro von Artur: open-iphone-use neu installiert (719bd55), Xcode 27.2, patch_oiu, iPhone 11 `…D3802E` per USB eingebunden.

## 17.11.2026 14:45 – Galerie, CAPTCHA, Fotos (Lauf Video 147, Rest)
- **Galerie-Länge „100:29“** (Symbol vor 00:29 mitgelesen) → `bildschirm.dauer_text` macht „00:29“ daraus (147-13 nie erkannt).
- **Hook ganz oben in der Kachel** (~98 über der Länge) → `galerie_kachel` Fenster 95 → 108 (147-25 UNO; Kachel ~112 hoch).
- **Länge auf hellem Hintergrund unlesbar** → `galerie_kachel_nachlesen`: Ausschnitt um die Label-Position 4× vergrößert lesen
  (ffmpeg, Schwelle/roh); nur bei sicherem Hook, Pflicht Länge ±1 s bleibt. Foto `ausgang/galerie-*.png` + Texte ins Log,
  wenn nach 20 s keine Kachel passt.
- **„Mehrere auswählen“** in der TikTok-Galerie (seit Arturs Umstellung an) → einmal pro Video aus (`mehrfach_an`, Punkte um
  den roten Kreis). Auswahl-Ansicht `auswahl_weiter`: Mini-Kachel ohne lesbaren Hook → Länge reicht (fremder Hook nein).
- **CAPTCHA-Fehlalarm** „Bestseller-Nr. 3 · Spiele & Puzzles“ (UNO) → Kategorie-/Bestseller-Zeilen raus, in `bildschirm.captcha_wort`
  (post_mensch._captcha nutzt jetzt dieselbe Funktion).
- **⚠ Fotos „Alle“:** iOS zeigt im Album-Auswahlmodus oben links „Alle“ – genau dort tippte `fotos_loeschen` blind „Zurück“
  (30,57) → alle 254 Objekte in „Zuletzt gesichert“ ausgewählt (nichts gelöscht, Auswahl aufgehoben). Jetzt: `tipp()` sperrt
  jeden Tipp neben „Alle“ (außer was=„Alle…“); `_ausgewaehlt` kennt „Auswahl (N) anzeigen“/„Objekte auswählen“ (=0);
  Sammel-Löschen hebt vorhandene Auswahl auf, startet nur bei 0 und löscht nie mehr als selbst angetippt; Dialog-Zahl muss
  dem Zähler am iPhone entsprechen. Einzel-Löschen (`fotos_loeschen`, Mediathek) ist mit dem neuen iOS noch nicht angepasst.
- Tests 206/206. Backups `*.bak-20261117-*` (post_mensch, bildschirm, test_posten).

## 17.11.2026 13:35 – Zwischenbild nach Kachel-Tipp + neue Auswahl-Ansicht (Lauf Video 147)
- Mit der Regel „Hänger = Beitrag neu“ führte jedes kurz „unbekannte“ Zwischenbild nach dem Kachel-Tipp (Vorschau fährt ein)
  sofort zum Verwerfen (147-12, 147-15). `zum_beitrag`: „unbekannt“ bis 5 s nur lesen (kein Tipp), erst dann Stopp; Foto
  `ausgang/unbekannt-HHMMSS.png` + Texte ins Log.
- Neue TikTok-Ansicht nach der Kachel (seit Arturs Umstellung 17.11.): oben „Ausgewählt 1“, unten Mini-Kachel (Hook + Länge),
  rechts „Weiter (1)“, links „AutoCut“. `auswahl_weiter()` (rein, getestet): „Weiter (1)“ nur, wenn Mini-Kachel Hook UND Länge
  (±1 s) passen; „Weiter (2+)“ = Sperre; AutoCut nie. Backups `post_mensch.py.bak-20261117-unbekannt` / `-auswahl`. Tests 203/203.

## 17.11.2026 13:20 – Hänger/Verbindungswechsel = Beitrag verwerfen + neu (Artur, Lauf Video 147)
- Anlass 147-03: Kabel-Steuerung riss ab (→ WLAN → USB), danach Schleife 6 min auf „Produkt umbenennen“ (Tastatur offen,
  Eingaben kamen nicht an, roter Knopf verdeckt; Wiederaufnahme „umbenennen → weiter“ endlos). Von Hand fertig gepostet.
- Artur: „bei einem hänger verwirfst du den post und machst ihn neu“, „Hänger passiert nur wenn das Kabel entfernt wird oder
  sich löst“, „wenn von Kabel auf WLAN umgeschaltet wird oder andersrum“. KEINE Umbenennen-Retry-Logik („bau das nicht ein“) –
  ein erster Entwurf davon wurde verworfen (`post_mensch.py.verworfen-20261117-umbenennen`).
- `kabel.WECHSEL` (+1 bei `_steuerung_neu` und bei USB-Umschaltung in `auf_usb`); `post_mensch.verbindung_merken/pruefen`:
  in jedem `lesen()` während eines Versuchs, Zähler geändert oder `steuerung_art` USB↔WLAN gewechselt → `Verbindungswechsel`.
- `ein_video`: jede Stopp/Kabel/Verbindungs-Ausnahme → `zur_hauptseite(abbrechen=True)` (Beitrag verwerfen), F zurück
  (Produkt, Beitrag, Cover, Text, Link), Video einmal neu (kein 2. AirDrop – liegt außerhalb `ein_video`); 2. Mal → Stopp
  „auch im 2. Versuch gescheitert“ → Video „fehler“, nächstes. `fortsetzen_planen` wird von `ein_video` nicht mehr benutzt.
- `produktname_feld_tippen`: immer direkt auf den vorhandenen Namen tippen (auch bei offener Tastatur), dann ⌘A/Löschen/Tippen.
- `einreichen.py BUTTONS`: „Bald vergriffen“ raus (verboten seit 15.11., 147-01 ging damit raus); offene 147-JSONs umgestellt.
- Tests 202/202 (angepasst: Hänger → komplett neu; Dauer-Hänger → nach 2. Versuch Fehler; neu: Verbindungswechsel).
  Backups `*.bak-20261117-wechsel` (post_mensch, kabel, test_posten).
- 17.11.2026 (Artur): „Provision unklar“ = Badge „Verdiene … pro Verkauf“ wurde kurz nicht angezeigt (TikTok-Bug) – KEIN Ausschlusskriterium. Badge erscheint oft erst nach mehrmaligem Öffnen des Links. stock.py wartet jetzt bis ~8 s. Nur ausdrückliches „nicht provisionsberechtigt“ = Entwurf.

## 18.11.2026 – „What Live do you want to watch?“ (Artur: „wie kommst du immer auf dieses Live-Widget … sorg dafür, dass es nicht nochmal passiert“)
- **Ursache (am iPhone belegt 16:09):** In der Spotlight-Suche steht unter „Toptreffer“ direkt rechts neben dem TikTok-Symbol der TikTok-Kurzbefehl **„WatchLive“**. `app("TikTok")` tippte 20 Pkt über das gefundene Wort „TikTok“; traf das (Layout springt beim Laden, OCR-Mitte verschoben) den Kurzbefehl, öffnet iOS das System-Blatt „What Live do you want to watch?“ (following/trending/recommend Live + Kanäle). Das Blatt liegt über JEDER App und bleibt nach der Home-Taste stehen. Bisher wurde es als „LIVE“ erkannt (Rückweg Wisch → wirkt nicht → 3× → TikTok neu über Spotlight → wieder Gefahr) bzw. über Home fälschlich als „Home mit TikTok-Widget“ (16.11.). Vorkommen: 13.11. 16:46, 15.11. 14:55/19:46, 18.11. 16:03.
- **Fix:** `app()` öffnet Apps aus Spotlight nur noch per **Return** (Feld zeigt „TikTok — Öffnen“, erster Toptreffer = App links: `spotlight_app_oben`), kein Tipp in die Treffer. Nur ohne „Öffnen“ noch Tipp aufs Symbol, und dann nie, wenn ein „…Live…“-Text näher als 70/60 Pkt liegt. Kein langer Druck irgendwo.
- **Neuer Bildschirm `B.LIVE_WAHL`** (`bildschirm.live_wahl`, Vorrang vor allen Dialogen): Rückweg `live_wahl_weg()` = Tipp oben über dem Blatt in die Statusleiste (240,22 / 300,22), nie eine Zeile; Wisch nach unten schließt es NICHT (getestet). `app()` macht das Blatt auch nach Home und nach dem Öffnen weg; `tipp()`-Gefahren-Sperre greift auch auf diesem Blatt.
- Tests 216/217 (neu `test_live_wahl`: Erkennung über TikTok/Home, Spotlight-Return mit echtem Bildschirm, Rückweg nur y < 40, app() ohne Tipp in Treffer; 3 Fälle in `faelle.json` + 2 Alt-Tests „Home-Widget“ auf `live_wahl` umgestellt). Rot bleibt nur „Liste per Produkt (Tatort → bof)“: Tatort steht inzwischen auch in Liste „bof 2“ (Testdaten, kein Fehler).
  Backups `*.bak-20261118-livewahl` (bildschirm, post_mensch, test_posten, faelle.json).

## 18.11.2026 17:30 – Produkt nicht verfügbar/entfernt = sofort Entwurf (Artur)
- „wenn ein Produkt nicht verfügbar ist oder entfernt wurde, bitte nicht nochmal versuchen, sondern als Entwurf speichern.“ `nicht_vorraetig()` erkennt jetzt auch „wurde entfernt“, „Produkt/Artikel entfernt“, „nicht (mehr) erhältlich“, „existiert nicht mehr“, „derzeit/ist nicht verfügbar“ (+ OCR ohne Umlaut). Befund → `Entwurf` (kein zweiter Versuch, kein Neustart des Videos, nicht wieder einreihen). Galt schon für „nicht vorrätig“/„OK, verstanden“ (Video 148: 27 Saugroboter, 12 Zerup).
- Tests ergänzt (`test_live_wahl`: 4 Fälle), laufen erst nach dem Lauf (nie während das iPhone benutzt wird). Backup `*.bak-20261118-entfernt`.
- 18.11. 17:55 (148-23/24 artur.official): Gefahren-Sperre „oben links im Feed liegt LIVE – Kamera zu nicht getippt“ griff im Zwischenbild, während die Kamera über den Feed fährt (Feed-Reiter + „Sound hinzufügen“ gleichzeitig). `tipp()` liest jetzt bis 3× nach 0,8 s neu; nur wenn sicher die Kamera steht (kein Feed oben), wird das X getippt, sonst bleibt die Sperre. Backup `*.bak-20261118-kamerazu`.
- 18.11. 17:58 – eigentliche Ursache 148-23/24: Shop-Reiter mit Produkt „SnapBliss Mini-Kamera“ + „LIVE-Auktion“ wurde als KAMERA erkannt (Teilwort-Treffer) → Rückweg wollte „Kamera zu“ (X oben links = LIVE) tippen, Sperre griff richtig. KAMERA jetzt nur bei „Sound hinzufügen“ oder exakt „KAMERA“ + „LIVE“/„VORLAGEN“ in der Modus-Leiste unten. Tests 222/223. Backup `bildschirm.py.bak-20261118-minikamera`.
- 18.11. 18:10 – Shop-Bedingungen-Blatt („Nur noch ein Schritt zum Bewerben der Produkte von Maybelline“, Knopf „Hinzufügen“): wurde als DLG_VERSTANDEN erkannt („einverstanden“) → Neustart-Schleife. Jetzt `B.DLG_BEDINGUNGEN` (`shop_bedingungen`, Vorrang vor „verstanden“); `lesen()` → `bedingungen_abwarten()`: Foto `bedingungen-*.png`, Mac-Mitteilung, warten bis 20 min, bis Artur selbst „Hinzufügen“ tippt (Zustimmung zu AGB wird nie automatisch gegeben), dann weiter am Bildschirm; danach Hart-Stopp. Tests ergänzt. Backups `*.bak-20261118-bedingungen`.

## 17.11.2026 – Foto-Slideshows posten
- Neu: `werkzeuge/post_slideshow.py` (nutzt post_mensch.ein_video, ersetzt nur Galerie/Editor/Link-Vorstufe), `werkzeuge/jpg_datum.py` (EXIF-Aufnahmedatum für feste Reihenfolge).
- Regeln (Artur): Galerie-Tab „Alle“, Mehrere auswählen an; im Editor alle Bilder auf 9:16 (sonst kein „Produkt“ beim Link); Titel leer; Produkt über „Hinzufügen von → Einkaufswagen“; Sound wählt TikTok; Produkt schon im Einkaufswagen → nicht nochmal hinzufügen (`uebergabe/ausgang/wagen.json`).
- Erster echter Post: Chupa Chups Adventskalender → andreasfastlane, 102 s.

## 18.11.2026 – mehr Hashtags
- `beschreibung_text`: statt 1 eigenem Hashtag so viele Themen-Hashtags wie erlaubt (max. 5 je Beitrag: bis 30.11. 3 Pflicht + 2 eigene, danach 5). Artur: „lass dir ruhig noch mehr Hashtags zum passenden Thema einfallen, auch bei Videos“.

## 18.11.2026 19:00 – Social1-Abhaken („keine-checkbox“ bei allen 148-Videos)
- Ursache: Artur hat die Liste „bof 2“ in „BOF“ umbenannt (gleiche ID 6afc676e…). Der offene Safari-Tab war veraltet; der „Save to list“-Dialog zeigte dort GAR KEINE Listen → `keine-checkbox`. Nach Neuladen sind alle Listen da.
- `social1_abhaken`: bei `keine-checkbox` Dialog zu, Liste neu laden, einmal wiederholen.
- `social1_verschieben`: wartet bis 6 s, bis der Dialog Checkboxen hat; leerer Dialog → neu laden + einmal wiederholen, NIE „Create new list“ auf leerem Dialog (so entstanden heute zwei leere Listen „nicht verfügbar“ – eine ist leer, Artur kann sie löschen). Nach dem Verschieben wird der Haken der Arbeitsliste gezielt per `social1_abhaken` entfernt (blieb sonst stehen).
- `social1-bof-2.json` → Listenname „BOF“, Kopie `social1-BOF.json`. Test „Tatort → BOF“ angepasst. Tests 225/225.
- Nachgeholt: 35 gepostete Videos aus BOF abgehakt, 09/12/27 nach „nicht verfügbar“ (3) und aus BOF raus. In BOF bleibt nur SONAX (Social1-Nr 10, nicht gedreht). Backups `*.bak-20261118-social1`.
- 18.11. 18:30 – Fotos-Sammel-Löschen: bei genau 1 ausgewähltem Video heißt der Knopf „Video löschen“ (ohne Zahl) → wurde nicht erkannt („Lösch-Dialog nicht gesehen“, Auswahl blieb). Jetzt = 1, nur wenn auch genau 1 ausgewählt. Backup `*.bak-20261118-einzelvideo`.
- **19.11.2026** – Neu: Research-System (`werkzeuge/research.py`, Regeln in `werkzeuge/research_regeln.json`, Sammelbild-Werkzeug
  `werkzeuge/blatt.swift`, Doku `docs/RESEARCH.md`). Liest Social1-Videos (Today/Trending) Seite für Seite über `?page=N`,
  Land über `localStorage.selectedRegion` (de/us), Vorfilter (Alter, Promis, Beauty, Supplements), Sammelbilder zum Sortieren,
  Speichern in Social1-Listen (Dialog-Methode wie `social1_verschieben`), Rangliste mit Punkten. Warum: Artur will tägliche
  automatische Research (DE: BOF + Slides, USA: Slides + Quality).
- **19.11.2026** – research.py: Klicks in Safari immer per `setTimeout(()=>…click(),0)` – ein direkter Klick auf „Save to list“
  ließ den Tab einfrieren (AppleEvent-Zeitüberschreitung, nur Tab schließen half). Liste anlegen braucht längere Pausen
  (Feld 1,5 s, Create bis 8 s auf Haken warten). Speichern sucht ein Video auch auf Nachbarseiten (Ränge verschieben sich).
- **19.11.2026** – rtk 1.2.0 (github.com/rtk-ai/rtk) nach `~/.local/bin` installiert und als Bash-Hook in
  `~/.claude/settings.json` eingetragen (`rtk init -g`, Sicherung: gibt es nicht, Datei war neu). Kürzt Ausgaben von git/ls/grep/tail,
  damit Claude weniger Kontext verbraucht. Unsere Python-/zsh-Werkzeuge bleiben unberührt; `tail` auf Logs zeigt STOPP-Zeilen weiter vollständig.
  Abschalten: Hook-Eintrag aus `~/.claude/settings.json` löschen. Gilt nur auf diesem MacBook (2. MacBook separat installieren).
- **19.11.2026** – research.py: hängender Safari-Tab wird erkannt (25-s-Zeitlimit) → Social1-Tab schließen, neu öffnen, Ablauf
  fortsetzen (`mit_neustart`, nur wenn vorne wirklich Social1 ist). Fehler beim Anlegen neuer Listen behoben (fehlende Zuweisung).
  Erster Lauf DE: 600 gelesen, 408 Kandidaten, `BOF DE 19.11.2026` 121 Videos, `SLIDES DE 19.11.2026` 31 Videos
  (5 inzwischen aus der Rangliste gerutscht). Research-Bilder per .gitignore nicht im Repo.
- **19.11.2026 (Artur)** – Research: Parfüm erlaubt; Sketche/Vergleiche und reine Vorführungen ohne Gesicht gehören in BOF DE
  (`BOF DE 19.11.2026` jetzt 332 Videos). research.py: eigenes Safari-Fenster statt „front document“ (stört post_mensch nicht),
  Land danach zurück auf DE, stabile Kandidaten-Nummern bei mehreren Läufen/Tag (`lesen --frisch`, `blaetter --neu`),
  Sperre `uebergabe/research/.laeuft`, leerer Listen-Dialog = Tab neu (Social1 wird nach vielen Saves langsam).
  Neu: `de-suche` (TikTok Shop DE über Social1-Produkte, Bestseller zuerst), `amazon`/`wagen` (Amazon.es, nur Einkaufswagen),
  `skript` (Transcribe), `messen`/`messung` (stündlich per launchd `de.tiktoksteuerung.research-messen`, Plist in werkzeuge/).
  Geplante Aufgabe „tiktok-research-taeglich“ 7/13/19 Uhr (Claude-App, Auto-Modus) → Tageslauf in docs/RESEARCH.md.
- **19.11.2026 13:20** – Stündliche Messung lief nicht („Operation not permitted“: launchd darf ~/Documents nicht lesen). Messung läuft
  jetzt aus einer Kopie in `~/.tiktok-research/` (`werkzeuge/research-messen-installieren.sh`), Sperre + Messdaten liegen auch dort.
- **19.11.2026 (Artur)** – Kein Video zweimal: `filtern` wirft Videos raus, die an einem früheren Tag schon in einer Research-Liste
  waren (auch wenn sie nach dem Posten aus der Liste entfernt wurden). Gleiches Produkt mit neuem Video/neuer Hook bleibt erlaubt.
  Rangliste markiert Produkte, die schon gepostet wurden (posts-*.json).
- **19.11.2026 13:50 (geplanter Lauf)** – `blaetter --neu` stürzte ab, wenn es noch keine `<land>-sortiert.json` gab (erster USA-Lauf) →
  fehlende Datei zählt jetzt als leer. Hinweis: bei Mac-Überlast (Load ~50) bricht `lesen` zu früh mit „keine Videos mehr“ ab →
  einfach nochmal `lesen` ohne `--frisch` starten, setzt fort.
- **19.11.2026 (Artur)** – Skripte nur für fremdsprachige Videos (auch Englisch): `research.py skripte <land>` holt Transkripte der
  Top 30 je Liste, erkennt Deutsch (Wortliste) und sammelt die übrigen in `uebergabe/research/<datum>/SKRIPTE <datum>.md`;
  Claude schreibt die deutschen Skripte hinein und hängt die Datei nach jeder Research im Chat an.
- **19.11.2026 (Artur)** – Kein Social1-„Transcribe“ (kostet Credits): `skripte` ausgesetzt, bis lokale Spracherkennung läuft.
- **19.11.2026 (Artur)** – Lokale Transkripte statt Social1-Transcribe: `werkzeuge/transkript.py` (yt-dlp + mlx-whisper large-v3-turbo
  + imageio-ffmpeg in `~/.tiktok-research/venv`, Artur hat die Installation erlaubt). Kleinstes MP4 laden (Nur-Ton gab 403),
  3 Versuche; Sprache kommt von Whisper. `research.py skripte` nutzt das, Ablage `<land>-transkripte/<nr>.json`. Test DE Top 3: 4× Deutsch erkannt.
- **19.11.2026 (Artur)** – Research liest bis Seite 100 statt 50.
- **19.11.2026 (Artur)** – Social1-Server-Aktionen fürs Speichern/Entfernen/Listen mitgeschnitten (docs/RESEARCH.md „Direkter Weg“), noch nicht eingebaut.
- **19.11.2026 (Artur: „schneller“)** – research.py spricht direkt mit Social1 (Server-Aktionen im Safari-Fenster, IDs werden zur
  Laufzeit aus den Social1-Programmdateien gelesen): `lesen` = getTopVideos gebündelt (100 Seiten DE 1200 Videos in 1:43 Min.),
  `speichern` = addVideoToList gebündelt + Abgleich mit der echten Liste + Liste anlegen per createVideoList, `de-suche` =
  searchProducts (neu `--datei` für viele Wörter, ~1,4 s/Wort), `messen` ebenfalls direkt. Neue Felder slideshow/ki/time_posted,
  Sammelbilder zeigen SLIDE/KI. BOF DE: 22 beim Klick-Speichern verlorene Videos nachgetragen. Sicherung `research.py.bak-20261119-direkt`.
- **19.11.2026 (Artur)** – Amazon erstmal deaktiviert (`amazon_aktiv: false` in research_regeln.json; `amazon`/`wagen` melden nur
  „deaktiviert“, auch für den laufenden 13-Uhr-Lauf). Amazon trotzdem auf den direkten Weg umgebaut: Suche + Einkaufswagen als
  Anfragen im Amazon-Fenster (keine Seitenwechsel/Klicks), nur Formular „In den Einkaufswagen“, Captcha → STOPP. Getestet: Suche
  2 Wörter 6 s, Formularprüfung 2 s (`--pruefen`); echtes Einlegen noch nicht getestet (deaktiviert).
- **19.11.2026 (Artur)** – Bildersuche nur bei TikTok Shop + Amazon.es (kein Google Lens – Testfenster wieder geschlossen):
  neu `research.py bildvergleich <land> <wuensche.json>` → Sammelbilder US-Produktbild neben TikTok-Shop-DE- (Social1) und
  Amazon.es-Treffern (wenn aktiv), Claude entscheidet am Bild. Test 4 Produkte 15 s. Treffer haben jetzt Bild-Links.
- **19.11.2026 (Artur)** – bildvergleich sucht automatisch mit dem kopierten Social1-Produktnamen (Amazon voller Name, Social1 auch gekürzt) plus Zusatzwörtern; Auswahl am Produktbild. Test: Name allein fand bei Social1 nur 1 von 4, mit kurzen deutschen Wörtern 3 von 4.
  Außerdem: `speichern` (neu direkt per Social1-API, Päckchen zu 50) lief bei 249 Videos in „429 Too many requests“ → Rest in Päckchen
  zu 15 mit 20 s Pause nachgespeichert, alles drin. Vorschlag: Päckchen kleiner/mit Pause. 1× Social1-„Transcribe“ (Nr 68 US) aus
  Versehen genutzt, bevor die Regel „nie Transcribe“ in RESEARCH.md stand.
- **19.11.2026 (Artur)** – Nach jeder Research werden die Ranglisten (de/us) und die SKRIPTE-Datei immer im Chat angehängt (Tageslauf + geplante Aufgabe).
- **19.11.2026 (Artur, Abgleich DE)** – Regeln aus Arturs eigener Research in docs/RESEARCH.md „Gelernt“ (Formate BOF/SLIDES, Beauty nur
  mit Reden/Preis, keine Vergleiche/Sketche, Handy-Preis-Videos = BOF, max. 6 Tage). Filter: Beauty + Supplements nur noch in USA
  pauschal raus, neu `verstoss_risiko` (Heilversprechen, Schmerzen, Haare, Anti-Aging … – alle Länder). Befund: alte Klick-Lesung
  hatte Foto-Slideshows verschluckt (67 Slides fehlten). Neu `research.py sortieren` (Social1-Liste = Ranglisten-Reihenfolge):
  erster Versuch verlor wegen Social1-Bremse 180 Videos kurz – komplett wiederhergestellt, jetzt einzeln + 429-Wiederholung.
- **19.11.2026 abends (Artur)** – Social1-Ansicht sortiert nach Hinzufüge-Reihenfolge, zuerst Hinzugefügtes OBEN → `sortieren`
  umgedreht. Neu `uebergabe/research/gemacht.json` (131 von Artur erledigte = aus seinen Listen entfernte Videos; filtern wirft sie
  raus), aus BOF DE 88 / SLIDES DE 11 entfernt. Promis → Kandidaten für „Reactions DE <datum>“ (`<land>-promis.txt`) statt raus.
- **19.11.2026 (spät)** – Research nach Arturs Abgleich überarbeitet: DE-Kandidaten (629 neu) einsortiert (Slideshow/KI → SLIDES,
  KI mit Reden zusätzlich BOF, Promis → neue Liste `Reactions DE 19.11.2026`, Rest per Sammelbild), 17 alte Sketch-/Vergleichs-BOF
  und alle Videos ab 7 Tagen aus den DE-Listen, alle DE-Listen nach Rangliste sortiert (Platz 1 zuerst eingelegt = oben).
  Neu: `research.py gemacht-abgleich` (Arturs eigene Listen gegen Momentaufnahme `~/.tiktok-research/artur-listen.json` →
  Entferntes = erledigt, gemacht.json + aus unseren Listen). `filtern us` lässt Slideshows trotz Beauty/Supplement drin (SLIDES USA
  = Format-Ideen). USA-Regeln aus Arturs Listen in docs/RESEARCH.md „Gelernt“, Quality USA ausgedünnt. Tageslauf + Prompt der
  geplanten Aufgabe angepasst (Schritt 0 Abgleich, Reactions-Liste, Sortier-Richtung, US-Regeln).

- **19.11.2026** – Neu `docs/ANALYSE.md`: Weg zu Einnahmen/Partnerbestellungen und Excel-Export erkundet (andrucha, iPhone 15 Pro Max), Export-Summen = Täglicher Umsatz geprüft. Grundlage für die Morgen-/Abend-Analyse (Artur).

## 19.11.2026 (abends) – Research nur bis Seite 50 (Artur)
- research.py `lesen`: Standard 50 Seiten statt 100 (Artur: 100 ist zu viel). RESEARCH.md + Auftrag der täglichen Aufgabe angepasst.
- Heutige Listen (BOF DE, SLIDES DE, Reactions DE, SLIDES USA, Quality USA 19.11.2026): Videos, die nur auf Seite 51–100 standen, entfernt
  (Sicherungen in uebergabe/research/2026-11-19/sicherung-*), Ranglisten + SKRIPTE neu.
- Listennamen festgehalten: unsere = „BOF DE …“/„SLIDES DE …“, Arturs = „eigene BOF …“/„eigene slides … DE“.
- Tägliche Aufgabe „tiktok-research-taeglich“ ist an (7/13/19 Uhr).
- Nachtrag (Artur): gelesen wird wieder bis Seite 100; `SEITEN_MAX` in research.py: BOF DE + SLIDES DE nur bis Seite 50 (speichern lässt
  Weiteres weg), Reactions DE + USA bis 100 → heute 44 Videos in Reactions DE/SLIDES USA zurückgelegt. `gemacht-abgleich`: nur Arturs
  `eigene BOF …` zählt (Inhalt + Rausgenommenes = gemacht), seine anderen Listen nicht (er arbeitet nur die BOF-Liste ab).

**20.11.2026 00:20 – CAPTCHA-Fehlalarm „Holzpuzzle“ (Video 151-24, Posting-Session):** Social1-Seite „TONECHEER 3D Holzpuzzle …“ wurde als Puzzle-CAPTCHA erkannt → Lauf wartete. `bildschirm.captcha_wort` entfernt jetzt Wörter mit „puzzle“ am Wortende (Holzpuzzle, 3D-Puzzle als Kompositum) vor der Prüfung; „Puzzleteil“/„das Puzzle“ bleiben CAPTCHA. Backup `bildschirm.py.bak-20261120-holzpuzzle`. Tests 224/225 (rot nur datenabhängig „Liste per Produkt Tatort“).
  Nachtrag 00:21: auch Hashtags (#puzzle aus der eigenen Beschreibung) werden vor der CAPTCHA-Prüfung ausgeblendet.

**20.11.2026 – Liken + Speichern in `post_mensch.py` (Artur: „liken und markieren integrieren“, Regel seit 13.11.):** nach jedem echten Veröffentlichen `liken_nach_post()` → Feed (neues Video „Vor 1 Sek.“) oder Profil-Kachel (Hook) → Herz + Lesezeichen nur tippen, wenn weiß, danach Pixel-Prüfung (rot/gelb). Fehler nur geloggt, Post bleibt gepostet; 3 Fehlschläge in Folge → für den Lauf aus; `TS_OHNE_LIKEN=1` schaltet ab. Neu `--liken <stapel> [account]` (Nachlauf). Erkennung in `bildschirm.py` (`eigenes_video`, `seitenleiste`, `herz_an`, `merken_an`; `erkenne()` unverändert). Tests `test_liken` (33 neu, an 4 echten Fotos gemessen). Backups `*.bak-20261120-liken`.

**20.11.2026 00:45 – Fehlalarm „Bild eingefroren“ (151-55):** Nach dem AirDrop zeigt das Fotos-Vollbild (Video spielt) oben die Platzhalter-Uhr „9:41“ → `_bild_aktuell` meldete Einfrieren → harter STOPP. Jetzt: Uhr „9:41“ auf Fotos-/unbekanntem Bildschirm zählt nicht als eingefroren. Backup `post_mensch.py.bak-20261120-uhr941`. Tests 258/259.
  Nachtrag 00:50: Das iPhone zeigt seit dem Server-Neustart ÜBERALL „9:41“ (Demo-Statusleiste, auch Home) → Uhr „9:41“ wird generell nicht mehr verglichen (Einfrier-Schutz per Uhr ruht, solange die Demo-Uhr steht).

- 20.11.2026 01:50 – Liken/Speichern: Profil stand oft auf dem Shop-Reiter (Tasche) → Kachel nie gefunden, Liken im Lauf ab 00:53 aus.
  Jetzt: `profil_raster()` zählt Shop-Reiter/Ladefehler nicht mehr, `_zum_profil()` tippt den Video-Reiter (`video_reiter()`,
  36 pt unter der Showcase-Zeile, Höhe je Konto verschieden). Am iPhone getestet (ella_robinson2, Halara): Herz + Lesezeichen an.

## 20.11.2026 – Slideshow-Test nach klickguru (Artur: „alle 5 Punkte“)
- Analyse @klickguru vs. @andreasfastlane: `docs/SLIDESHOW-ANALYSE.md`.
- `research.py vorbilder`: liest Slideshow-Accounts (research_regeln.json „vorbilder“, zurzeit klickguru) im eigenen Safari-Fenster
  (TikTok-Profil, nicht eingeloggt; Haken auf /api/post/item_list, „Aktualisieren“ bei Fehlerseite) → Hits ≥ 30K/≤ 7 Tage als
  `uebergabe/ausgang/social1-vorbilder.json` (social1-Format + gewinner_sounds). Produkt-ID als Text (zu groß für JS-Zahlen).
  Logik im Claude-Browser geprüft, echter Safari-Lauf noch offen (lief gerade ein Posten-Stapel).
- `post_slideshow.py --stil klickguru`: Beschreibung leer, keine Hashtags (Schluss-Prüfung bleibt).
- Editing System (eigene/): `slideshow-auto/auto_posten.py` + `konten.json` „regeln“: andreasfastlane = Testkonto, max. 8/Tag,
  ≥ 45 Min. Abstand, --stil klickguru, Gesamtlimit aufgehoben; andere Konten wie bisher (Vergleich). Sicherungen *.bak-vor-klickguru.
  `REZEPT-SLIDESHOW-AUTO.md`: Abschnitt „Test klickguru-Regeln“ (Bild 1 = Story/Meme, immer neue Bilder, Quelle „vorbilder“).
- Offen: KI-Kennzeichnung am iPhone (Schritt nicht gebaut), Sound-Wiederverwendung (TikTok wählt Musik selbst, Artur 17.11.).

**20.11.2026** – Neu iPhone-App „Provision“ (`app/Provision`, SwiftUI, kostenloses Personal Team → 7 Tage gültig) zeigt die eigenen Provisionszahlen; Daten aus iCloud Drive `Provision/provision.json`, erzeugt von `werkzeuge/analyse/app_daten.py` (aus `bestellungen.json`/`praemien.json`). Installiert auf iPhone 15 Pro Max (Artur).

**20.11.2026** – App heißt jetzt **kmhview** (`app/kmhview`, iPhone + Mac, neues Icon, modernes Design mit Profilbildern,
voraussichtliche Provision heute/gestern/7/30 Tage, „Alle Accounts“ zusammengerechnet) + Browser-Version (`app/web`, Artifact).
Neu `werkzeuge/analyse/export_holen.py` (Export aller Accounts am iPhone 11 per AirDrop), `baue.py` (alle Konten),
`web.py`. Alte App `app/Provision` ersetzt (Artur).

**20.11.2026** – App heißt **statsKMH** (Artur). Neu: Zeiträume 3 Tage + eigener Zeitraum mit klarer Datumsangabe, Video-Performance
(Sales/GMV), Kacheln „Bereits ausgezahlt“ / „Zur Auszahlung bereit“ (Guthaben per `export_holen.py --guthaben`), interaktive
Diagramme. Stand + nächste Schritte: `docs/STAND-ANALYSE.md`.

**20.11.2026 (früh)** – Offizielle TikTok-Zahlen statt Export-Rechnung (Artur: Export wich ab, z. B. anduri 113,09 statt 114,76 €).
Neu `werkzeuge/analyse/daten_holen.py`: liest pro Account die Seite „Daten“ (Creator-Bereich → Pfeil neben „Heute | Letzte 7 Tage“)
je Tag ab (Heute, Gestern = Reiter; ältere Tage über Benutzerdefiniert → Tag, TikTok lässt dort nur bis vorgestern zu) –
Vorauss. Provisionen, GMV, Artikel, Sichtkontakte, Klicks, Ansichten – plus je Tag die Top 25 Videos nach Aufrufen
(→ `exporte/<konto>.tage.json`, `exporte/<konto>.videotage.json`, fortgeschrieben). Geprüft: Summe 16.–18.11. = TikToks Bereichswert auf den Cent.
`app_daten.py`: Tageswerte = TikTok-Zahl, wo abgelesen, sonst Export (Anteil wird angezeigt). App heißt jetzt **viewKMH** (Artur),
Video-Performance mit eigener Zeitraumwahl (3 Tage nur dort, nicht in der Geldstatistik – Artur), Seiten à 10, Ansicht
„Nach Verkäufen“/„Nach Aufrufen“, Sortierung; Profilbilder ohne weißen Rand; Bestellmonat „davon … offen“.
Likes/Kommentare zeigt TikTok auf „Daten“ nicht (→ später Display API).
- **20.11.2026** – Eigenes iPhone-Spiegel-Fenster statt „Mirror My Phone“ (Abo gespart): `werkzeuge/kabel/spiegel.html`,
  + `spiegel.js`, über `patch_oiu.py` (Schritt 7) in den Kabel-Server eingehängt (Server erlaubt nur Skripte als eigene Datei) → http://127.0.0.1:27893/spiegel. Klick = Tippen, halten = langer Druck,
  ziehen = Wischen, Mausrad = Scrollen, Mac-Tastatur tippt am iPhone, Knöpfe Home/Sperre/Lauter/Leiser.

**20.11.2026 (06:15) – VORFALL + Sperren.** Beim Ablesen (export_holen.py) wurde auf artur.official versehentlich eine Story gepostet:
„Zurück“ oben links traf auf dem eigenen Profil den Stift (Story), dann tippte die Werbe-Popup-Regel („Poste…“) auf „Posten“.
Artur hat die Story gelöscht. Neu: `gesperrt()` – nach JEDEM Tipp wird geprüft, ob ein Post-/Story-Bildschirm offen ist
(„Veröffentlichen“, „Posten“, „Story“, „sichtbar“, „Was läuft“ …) → sofort STOPP, nichts mehr tippen. Werbe-Popup nur noch bei
Text „Poste …“ (nie Knopf „Posten“/„Posteingang“). Eigenes Profil = „Gefolgt“ ohne „Nachricht“, dort nie oben links tippen.
Kontoname nur links antippen (rechts sitzt „Was läuft?“). Ebenso früher am Tag: „Posteingang“ wurde als Popup getippt
(öffnete Aktivitätsstatus) → behoben.

**20.11.2026 (06:30)** – `export_holen.py --praemien`: Guthaben + Prämien (Auszahlungsverlauf → Belohnungen, Kopfzeile „N Prämien €X verdient“)
→ praemien.json je Konto. App/Web: Account-Auswahlfeld mit Suche (für 10–20 Accounts), Zeitraum-Kalender (Start/Ende mit 2 Tipps),
Profilbild-Cache (kein Ruckeln), iPhone-Dunkelmodus schwarz, Balken grün, Seiten bei Top-Listen/offenen Bestellungen.
- **20.11.2026** – Eigene Mac-App **iPhone-Spiegel** (`app/spiegel/`, bauen: `zsh app/spiegel/bauen.sh` → /Applications) statt
  „Mirror My Phone“: nur Zuschauen. Kabel wie QuickTime (CoreMediaIO gibt das iPhone als Kamera frei), ohne Kabel das WLAN-Live-Bild
  des Kabel-Servers (open-iphone-use muss laufen). Fenster ohne Rand, Ampel-Knöpfe erscheinen beim Drüberfahren (Schließen = App zu,
  Minimieren, Dock-Klick holt zurück), ⌘W/⌘M/⌘Q; Rechtsklick: Vordergrund / normal / Schreibtisch, iPhone-Wahl.
  Signiert mit dem Apple-Development-Zertifikat, damit „Kamera erlauben“ nur einmal kommt (ad-hoc fragt nach jedem Neubau).
- **20.11.2026** – Web-Spiegel (`/spiegel`, spiegel.html/.js, patch_oiu.py Schritt 7) wieder entfernt: Andreas will nur zuschauen,
  als eigenes Fenster statt Website → App iPhone-Spiegel.
- **20.11.2026** – iPhone-Spiegel: eigenes App-Symbol (`app/spiegel/icon.swift`, beim Bauen erzeugt) und mehrere iPhones gleichzeitig –
  ein Fenster pro iPhone (⌘N / Rechtsklick „Neues Fenster“ nimmt das nächste freie iPhone, im Rechtsklick fest wählbar).
  Fenster samt Position und iPhone-Wahl kommen beim nächsten Start wieder.

**20.11.2026 (07:00)** – andrucha.official am iPhone 15 Pro Max abgelesen. `creator_oeffnen()` (Profilknopf, sonst TikTok Studio →
Monetarisierung → TikTok Shop für Creator*innen); Rückweg: auf bekannten Shop-/Studio-Seiten X oben links, sonst Zurück-Wischgeste
vom linken Rand (kein Tipp); Profil-Reiter mit Beschriftung „Profil“; längere Ladezeiten (30 s); Dunkelmodus-OCR („Taд“).

## 20.11.2026 nachmittags – Vorbilder-Research im echten Safari getestet
- `research.py vorbilder` läuft im Safari: 126 klickguru-Posts, 5 Hits → `uebergabe/ausgang/social1-vorbilder.json`.
- Gewinner-Sounds: alles „original sound“ (z. B. „mike🕸️“, auch mit Produktlink). Wiederverwenden noch nicht eingebaut:
  Suche nach Namen am iPhone unsicher; erst am iPhone testen, ob TikTok den Produktlink damit erlaubt.

## 20.11.2026 16:40 – Research: Bildvergleich-Download mit Zeitlimit
- `research.py bildvergleich`: Bilder laden jetzt mit 20 s Zeitlimit (`urlopen(timeout=20)` statt `urlretrieve`).
  Warum: der Lauf hing seit 07:47 über 8 h an einem einzigen Bild-Download. Alter Prozess (PID 50047) konnte ich nicht beenden – bitte bei Gelegenheit selbst beenden.
- US-Lauf: `us-sortiert.json` muss vor `rangliste us` angelegt sein (SLIDES/QUALITY) – fehlte, nachgeholt.
- **KI-Kennzeichnung bei Slideshows (Artur 20.11.):** `post_slideshow.py` → `ki_label()` vor der Schluss-Prüfung:
  Beitragsseite runter → „Weitere Optionen“ → „KI-generierter Inhalt“ an (Farbe türkis = an, nur tippen wenn aus,
  Hinweis „Einschalten“ bestätigen) → Blatt zu → hoch. Am iPhone getestet (an→bleibt, aus→an), Test-Beitrag verworfen.
  Warum: KI-Bilder ohne Label; das C2PA-Kennzeichen von ChatGPT geht beim Text-Rendern (Playwright-JPG) verloren –
  nicht absichtlich entfernt (alte Regel REZEPT-SLIDESHOW.md: „C2PA nicht gezielt entfernen“).

## 20.11.2026 17 Uhr – Research DE: Übernahme statt „nie zweimal“, Artur arbeitet unsere BOF-Liste ab
- Artur: „eigene BOF 19.11.“ war einmalig; ab heute arbeitet er `BOF DE <datum>` ab. Nicht Erledigtes von gestern soll
  heute wieder rein (vorher flog alles raus, was an einem früheren Tag in einer Liste war – 579 Videos).
- `research.py`: `frueher_gespeichert()` gibt die Art (BOF/SLIDES/REACTIONS) zurück; `filtern de` schließt früher
  Gespeichertes nicht mehr aus und trägt die Art in `de-sortiert.json` ein (USA unverändert: nie zweimal).
  `gemacht_abgleich()`: erledigt = was seit der letzten Momentaufnahme aus unseren `BOF DE …`-Listen fehlt.
- docs/RESEARCH.md und die geplante Aufgabe angepasst. Sicherung: scratchpad research.py.vor-uebernahme.
- **20.11.2026** – iPhone-Spiegel neu gestaltet: randloses Fenster mit gezeichnetem iPhone (schmaler Rahmen, Metallkante, iPhone-Ecken),
  Knöpfe als Milchglas-Pille über der Dynamic Island (erscheint beim Drüberfahren), Grün = Vollbild (iPhone mittig auf Schwarz, Esc beendet).
  Flüssiger ohne Kabel: patch_oiu.py Schritt 7 – Live-Bild 60 statt 30 Bilder/s, WLAN 6 statt 2 Mbit/s (iPhone wird etwas wärmer).
- **20.11.2026** – iPhone-Spiegel: Ziehen irgendwo auf dem iPhone verschiebt immer das Fenster (performDrag, auch im Hintergrund);
  das WLAN-Livebild nimmt keine Klicks mehr an (vorher startete macOS manchmal „Bild herausziehen“).
- **20.11.2026** – iPhone-Spiegel bedient sich jetzt wie Mirror My Phone über die Menüleiste: „Gerät“ (iPhone fürs vorderste Fenster,
  ⌘1/⌘2 …, „iPhone-Rahmen zeigen“ an/aus) und „Optionen“ (Immer im Vordergrund ⌘T, Auf dem Schreibtisch). Rechtsklick und Knopf-Pille bleiben.
- **Rangliste als Seite (Artur 20.11.: „nicht visualisiert“):** `rangliste` schreibt zusätzlich `<land>-rangliste.html`
  (Kacheln mit Social1-Vorschaubild, Platz, Liste, Alter, +Views, Produkt; Klick → TikTok). Rangliste zeigt nur noch Videos
  bis zur Seitengrenze der Liste (wie `speichern`), vorher auch Seite > 50.
- `speichern`: Nummern, die beim neuen Lesen nicht mehr unter den Kandidaten sind, werden übersprungen (vorher KeyError
  beim USA-Abendlauf 20.11.).
- Vorbilder-Research (klickguru) läuft jetzt in jeder Research-Runde (7/13/19 Uhr) nach USA mit (Artur 20.11.).
- **20.11.2026** – iPhone-Spiegel wie Mirror My Phone umgebaut: Menüs Ablage (Neues Gerät, Alle schließen), Optionen (Im Vordergrund
  fixieren ⌘T, Schreibtisch), Gerät (Rahmen: Geräterahmen/Geräteform/Fenster, 12 Rahmenfarben, Größe: Gerätegröße/Punkt für Punkt/
  Pixel für Pixel/An Bildschirm anpassen, iPhone-Wahl ⌘1 …), Fenster (Minimieren, Füllen, Zentrieren, Vollbild, Schließen).
  „Warte auf iPhone …“-Bildschirm, echte Bildgröße auch über WLAN (PNG-Kopf). Fehler behoben: App kam beim Klick nicht nach vorn
  (Menüleiste blieb bei der vorigen App). Weggelassen: Aufnahme, Bildschirmfoto, Musik/Video-Modus, Ton, Gerätemodell.
- **20.11.2026** – iPhone-Spiegel: Klick aufs iPhone holt die App selbst nach vorn und verschiebt das Fenster von überall
  (vorher verschob macOS das Fenster ohne die App zu aktivieren → Menüleiste blieb bei der vorigen App).

**20.11.2026 (abends)** – Aktualisieren auf Knopfdruck (Artur: nur manuell): viewKMH hat Knöpfe „Schnell“ (Heute/Gestern/Guthaben,
~2 Min./Account) und „Voll“ (30 Tage, Videos, Export, Prämien, ~7 Min./Account) mit geschätzter Dauer, Fortschritt, „läuft seit“
und Restzeit. Ablauf: Knopf → iCloud statsKMH/auftrag.json → Mac-App viewKMH startet `werkzeuge/analyse/aktualisieren.py <art>`
(launchd-Dienst ging nicht: kein Zugriff auf ~/Documents) → status.json → App zeigt Fortschritt, lädt danach neu. Zeiten lernen
mit (dauer.json). Web-Version aktualisiert nur Claude. App-Icon zuerst Graphit-Balken, dann (Artur-Wahl) B „Graphit + Mint-Linie“. App heißt viewKMH.

**20.11.2026 (19:30)** – viewKMH: Handy-Auswahl beim Aktualisieren (alle Handys mit Entwicklermodus im WLAN/am Kabel; Mac schreibt
alle 30 s `statsKMH/geraete.json` über `aktualisieren.py --geraete` ← Steuer-Server /api/candidates; neue Handys werden beim Start
automatisch angemeldet; Accounts, die auf dem Handy fehlen, werden übersprungen). iPhone-Spiegel (app/spiegel) hat jetzt den Link
`iphonespiegel://geraet/<UDID>` → Fenster für genau dieses iPhone; aktualisieren.py öffnet ihn beim Start, Mac-App hat Knopf „Spiegel“.

**20.11.2026 (20:00)** – App wieder **statsKMH** (Artur). Rückfrage vor jedem Aktualisieren; verständliche Fehler (z. B. Handy per
WLAN nicht erreichbar); „✓ Offizielle Zahl aus TikTok › Daten“ + Ablesezeit („Heute … · Stand 07:05 Uhr“, app_daten: `gelesen`);
Handy-Liste mit iPhone-Namen inkl. bekannter, nicht erreichbarer Handys (devicectl); Ruckeln behoben (iCloud-Lesen im Hintergrund,
nur bei Änderung neu zeichnen, Diagramm per Tippen statt Ziehen); Accounts-Liste immer sichtbar mit Hervorhebung;
„Account hinzufügen“ (konten.json in iCloud → aktualisieren.py), Einloggen auf dem Handy macht Artur.

**20.11.2026 (19:50, Research-Lauf 19 Uhr)** – `research.py lesen`: liefert Social1 schon Seite 1 leer → STOPP, alter Stand
bleibt (vorher: 0 Videos, `filtern` leerte de-kandidaten.json; aus Git wiederhergestellt). `sortieren`: Fehler beim Wieder-Einlegen
(„Load failed“) bricht nicht mehr ab, sondern versucht es nochmal + Nachkontrolle (1 BOF-Video war kurz raus, aus Sicherung zurück).

**20.11.2026 (20:10)** – iPhone: Seite war breiter als der Bildschirm (lange Handy-Auswahl mit fixedSize) → gekürzt; Schrift auf
„groß“ begrenzt, kompaktere Abstände. Icon B (Graphit + Mint-Linie) eingebaut. Alte Fehlermeldungen aus status.json entfernt.

- 20.11.2026 (abends): (zurückgenommen, Artur: alte Rangliste war gut) research.py `punkte`: Alter entscheidet zuerst (jeder Tag 100 Punkte Abstand, Rest max. 75), innerhalb eines Tages wie bisher Views/GMV/Interaktion. Warum: Artur – Listen „nach Rangliste, vorwiegend Alter“; vorher konnte ein starkes älteres Video vor einem jüngeren landen.
- 20.11.2026 (abends): research.py `rangliste`/`sortieren`: sortieren nimmt bei Punktgleichstand exakt dieselbe Reihenfolge wie die Rangliste (Rangliste selbst unverändert). Warum: Artur – Social1-Listen exakt wie die Rangliste.
- 20.11.2026 (abends): research.py `rangliste` schreibt zusätzlich je Liste eine eigene Rangliste (`-bof`, `-reactions`, `-slides`, `-quality`, .md + .html, Platz-Nr. je Datei neu). Warum: Artur – SLIDES und Reactions immer extra.
- 20.11.2026 (spät, wirkt ab Research 21.11. 7 Uhr): research.py `punkte`: Creator-GMV (30 Tage) und 🔥-Bonus raus, dafür Video-Umsatz (Social1-Feld `gmv` pro Video, neu als `video_gmv` in kandidaten). Warum: Artur – Creator-GMV sagt nichts übers Video; Stückzahl (units_sold) ist bei Social1 fast immer 0. Heutige Ranglisten nicht neu erzeugt.
- 20.11.2026 (spät): research.py `sortieren` übernimmt die Reihenfolge 1:1 aus `<land>-rangliste.md` (statt Punkte neu zu rechnen); removeVideosFromList bei „Load failed“ einmal wiederholt. Warum: Artur – Social1-Liste genau wie die Rangliste; BOF-Sortierung brach bei Platz ~100 ab.
- 20.11.2026 (spät): research.py `rangliste` teilt BOF/Reactions/Quality auf Artur und Andreas auf (`<land>-rangliste-artur.md`/`-andreas.md`, gleiches Produkt nur bei einer Person) und kopiert alle .md-Ranglisten nach `~/Documents/Ranglisten/<JJJJ-MM-TT>/` (erst Schreibtisch, dann auf Arturs Wunsch Dokumente); `sortieren` 1 s Pause pro Video. Warum: Artur arbeitet mit Andreas, will die Listen auf dem Schreibtisch; Social1 verlangte ohne Pause ein Captcha.
- 20.11.2026 (spät): research.py Übernahme: nur Abgehaktes fällt weg – `gemacht-abgleich` beobachtet ALLE unsere Listen (nicht nur BOF DE), USA übernimmt nicht Abgehaktes wie DE (vorher „nie zweimal“), Quality-Listen als QUALITY erkannt. Warum: Artur – oft wird nur DE erledigt, USA gar nicht; nach dem Upload wird in Social1 abgehakt.
- 20.11.2026 (spät): Ranglisten für Artur/Andreas/SLIDES als einfache Liste statt Tabelle (Name fett, darunter Art · Alter · +Views · Creator, Link in eigener Zeile). Warum: Artur – über WhatsApp/AirDrop auf dem iPhone waren die .md-Tabellen unlesbar.
- 20.11.2026 (spät): Artur/Andreas/SLIDES-Ranglisten zusätzlich als HTML-Tabelle (`<land>-rangliste-<wer>.html`, iPhone-Breite, Produkt = TikTok-Link, Dunkelmodus) in uebergabe/research/<datum>/ und ~/Documents/Ranglisten/<datum>/. Warum: Artur – Tabelle soll auf dem iPhone (WhatsApp/AirDrop) gut aussehen.
- 20.11.2026 (spät): HTML-Ranglisten immer dunkel im Graphit-Look von Arturs Dock (iPhone-Vorschau ignoriert Dunkelmodus), Chips für Art/Alter, Hinweis heißt jetzt „Produkt schon verlinkt“ statt „schon gepostet“. Warum: Artur – weiß auf dem iPhone; „schon gepostet“ klang, als sei das Video erledigt.
- 20.11.2026 (spät): Hinweis „Produkt schon verlinkt“ aus allen Ranglisten entfernt. Warum: Artur – bringt nichts, das Video ist trotzdem zu machen.
- 20.11.2026 (spät): HTML-Ranglisten: Graphit-Tabelle + leichte Farben der statsKMH-App (Grün Today, Türkis Yesterday, Blau Art); fremdsprachige Videos mit Badge „🌐 EN · Skript“, Antippen klappt das deutsche Skript aus SKRIPTE <datum>.md auf; in der .md steht das Skript als Zitat unter dem Video.
- 20.11.2026 (spät): Ranglisten: BOF-Videos ohne Sprache (Transkript < 30 Zeichen oder SKRIPTE „nur Musik“) bekommen Badge „🎵 Standard-Skript“ mit Arturs 2 Standard-Skripten (Black-Friday-Skript nur bis 01.12.2026, Produktname gekürzt, Preis falls bekannt). Warum: Artur – bei Musik-Videos braucht man trotzdem einen Text.
- 20.11.2026 (spät): Ablage ~/Documents/Ranglisten/<datum>/ mit Dateinamen „<JJJJ-MM-TT> <DE|USA> <Artur|Andreas|SLIDES>.<md|html>“. Warum: Artur – Datum im Namen, klarer sortiert.
- 20.11.2026 (spät): Steht im deutschen Skript „nur Musik“, kommen Arturs 2 Standard-Skripte (Black Friday + Preisfehler) mit Produktname dazu – in .md und HTML, alle Listen. Warum: Artur.
- 20.11.2026 (spät): Standard-Skripte mit Platzhaltern „(Produkt)“ und „(Preis)“ statt automatisch eingesetzt. Warum: Artur schaut Produkt und Preis selbst nach.
- 20.11.2026 (spät): Standard-Skripte beschriftet „Black-Friday-Skript“ / „Normales Standard-Skript“ statt 1./2.
- 20.11.2026 (spät): Ranglisten-HTML ohne Seitwärts-Scrollen (feste Spaltenbreiten, Umbruch), Skripte ohne JavaScript aufklappbar; zusätzlich PDF in iPhone-Breite (Google Chrome headless, Skripte aufgeklappt), weil Links in der WhatsApp/AirDrop-Vorschau nur im PDF funktionieren.
- 20.11.2026 (spät): HTML-Ranglisten: Nummer antippen = eigener Haken (nur für Artur/Andreas, pro Gerät im Browser gespeichert, kein Bezug zu Social1/gemacht). Zeile wird blass + durchgestrichen.
- 20.11.2026 (spät): Ablage Dokumente/Ranglisten: vor dem Schreiben werden die Dateien des Landes im Tagesordner gelöscht – nur die aktuelle Version liegt drin.
- 20.11.2026 (spät): .md-Ranglisten nicht mehr in Dokumente/Ranglisten (nur HTML + PDF). Warum: Artur – nur die endgültige Version im Ordner.
- 20.11.2026 (spät): Dokumente/Ranglisten nur noch HTML (6 Dateien), keine PDF mehr (pdf_machen bleibt als Reserve im Code). Warum: Artur – nur eine Datei pro Rangliste.
- 20.11.2026 (spät): Ablage überschreibt Dateien statt sie vorher zu löschen (iCloud hatte „… 2.html“-Kopien angelegt) und räumt danach alles Übrige des Landes weg.
- 20.11.2026 (spät): Online-Seite für die Ranglisten (claude.ai, fester Link, privat): DE/USA × Artur/Andreas/SLIDES, gemeinsame Haken (Artifact-Datenbank), Skripte aufklappbar, Links funktionieren am Handy. research.py schreibt daten-<land>.json, die Research veröffentlicht sie jede Runde an dieselbe URL. Warum: lokale HTML-Dateien öffnen am iPhone nur in der Vorschau (keine Haken, keine Links).
- 20.11.2026 (spät): Ranglisten-Seite im WLAN: werkzeuge/ranglisten_server.py (launchd, Port 8080) liefert die Seite + gemeinsame Haken für alle Handys ohne Anmeldung; research.py `rangliste` kopiert daten-<land>.json nach ~/.tiktok-research/seite. Warum: Artur – mehrere Handys ohne Claude-Login.
- 20.11.2026 (spät): Ranglisten-Server liefert die Seite mit Handy-Breite (viewport fehlte → iPhone zeigte Desktop-Breite, rechts abgeschnitten); Produktnamen auf 2 Zeilen gekürzt.

## 20.11.2026 – statsKMH: alle Accounts auf jedem Handy
- `werkzeuge/analyse/aktualisieren.py`: iPhone 11 und iPhone 15 Pro Max haben jetzt beide alle 6 Accounts (vorher iPhone 15 nur andrucha.official).
  Ohne Handy-Wahl wird jeder Account nur einmal gelesen. Grund: Artur – Stand jetzt sind auf jedem Handy alle Accounts; soll später wieder getrennt werden.
- statsKMH (`Uebersicht.swift`): Account unten in der Liste antippen → Bild springt nicht mehr mit (Liste bleibt an derselben Stelle stehen, ohne Animation). Grund: Artur – „Wisch-Hocheffekt“ beim Wechseln.
- statsKMH Design an Arturs Vorlage (Broker-App-Screenshots) angepasst: echtes Schwarz/Weiß, Abschnitte ohne Rahmen mit großen fetten Überschriften,
  Hauptzahl groß, Verlauf als reine weiße Linie bis an den Rand mit gepunkteter Durchschnittslinie (ohne Achsen), Zeitraum als schlichte Textreihe,
  flache graue Kacheln (ohne Symbole), Ansicht-Reiter als Text, Aktualisieren-Knöpfe als helle Pillen. Gilt für iPhone und Mac. Alte Fassung: Git-Verlauf.
- statsKMH Design noch am selben Abend auf Arturs zweite Vorlage (Revolut-Video) umgestellt: Blau-Grau-Verlauf als Hintergrund, halbdurchsichtige Glas-Karten
  mit kleiner grauer Überschrift „›“, oben runder Account-Kreis + Such-Kapsel zum Wechseln, Zahl mit ▲/▼ ggü. gleich langem Zeitraum davor (nicht bei „Heute“),
  türkise Linie mit Fläche + Tagesachse, Umschalter als graue Kapsel, „Schnell“ als weiße Kapsel, Aktualisieren-Karte nach unten.
  Neu: Startbild „statsKMH“ auf Schwarz (0,9 s, App.swift).
- statsKMH: bunte runde Symbole (Kacheln + Karten-Überschriften, Revolut-Art); Diagramm als eigene Ansicht mit vorberechneten Punkten
  (Antippen zeichnet nur das Diagramm neu → kein Ruckeln); Account-Auswahl/„Account hinzufügen“ mit gleichem Hintergrund + Glas-Zeilen;
  Fehler unter Schnell/Voll nur vom letzten Lauf (< 6 Std.), doppelte einmal; alte andrucha-Fehler aus status.json gelöscht.
- statsKMH Logo/App-Symbol „A Puls“ (Türkis→Blau, weiße Kurslinie, leuchtender Endpunkt; Quelle app/icon-vorschlaege/icon_puls.swift).
  Startbild neu: Systemstart in derselben Farbe (Asset StartFarbe, app/kmhview/Info-iOS.plist) → kein Flackern; Logo federt rein,
  Schriftzug „stats“ dünn + „KMH“ fett gleitet nach, dann Zoom/Überblendung in die App. Grund: Artur – Start unflüssig, Logo nicht modern.
- 21.11.2026 statsKMH: Aktualisieren übers Handy lief sofort auf „nicht erreichbar“ → `aktualisieren.py` setzt jetzt TS_WLAN=1
  (sonst will kabel.py bei WLAN-Steuerung auf Kabel umschalten = Server-Neustart); Rohmeldung wird mitgeloggt.
  Kalender: Tage 1–5 fehlten am Monatsanfang (leere Felder hatten dieselben IDs) → behoben. Aktualisieren-Karte wieder oben,
  Accountliste direkt unter den Kacheln, Wechsel ohne Animation, alter Scroll-Ausgleich entfernt (machte den Schieb-Effekt).
- 21.11.2026 Eigentliche Ursache „Handy nicht erreichbar“: Steuer-Server lieferte Bilder, aber jede Eingabe übers WLAN → „No route to host“
  (beide iPhones). Server-Neustart behebt es. `aktualisieren.py` prüft jetzt vor jedem Handy eine Probe-Eingabe (Home-Taste) und startet
  den Server bei Bedarf selbst neu.
- 21.11.2026 Kamera am iPhone 15 war schwarz, solange der Steuer-Server dessen Bildschirm mitschnitt → iPhone 15 beim Server abgemeldet.
  `aktualisieren.py` meldet nach jedem Lauf alle Handys außer dem Daten-iPhone 11 wieder ab.

## 21.11.2026 – Ranglisten-Seite im statsKMH-Design
- `uebergabe/ranglisten-seite/index.html`: Farben 1:1 aus statsKMH (Verlauf oben, Glas-Karten, Minzgrün, bunte runde Icons je Videoart: BOF orange, Reactions pink, Slideshows blau, Quality lila). Warum: Artur wollte das statsKMH-Design (Bildschirmaufnahme 21.11.).
- 21.11.2026 statsKMH: Knopf „Ranglisten“ (Listen-Symbol oben) öffnet die Research-Ranglisten-Seite vom Mac in einer Webansicht
  (app/kmhview/kmhview/Ranglisten.swift; iPhone: MacBook-Pro-von-Andreas.local:8080, sonst 192.168.8.214:8080; Mac: localhost:8080).
  Seite und Server unverändert. Info-iOS.plist: NSAllowsLocalNetworking + NSLocalNetworkUsageDescription; neu Info-mac.plist (ATS lokal).
  TikTok-Links öffnen außerhalb (TikTok/Browser). Auftrag aus dem Research-Chat (Artur 21.11.).
