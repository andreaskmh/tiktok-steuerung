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
