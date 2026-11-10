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
