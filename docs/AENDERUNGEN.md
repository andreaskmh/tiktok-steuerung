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
