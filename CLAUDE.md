# TikTok-Steuerung – Anweisungen für Claude

Dieses Projekt holt **Stock-Bilder aus TikTok-Shop-Produkten** (für Bottom-of-Funnel-Videos) und soll
später **Videos automatisch posten** (Showcase-Produkt verlinken, Beschreibung, Hashtags).
Nutzer ist **Artur** (TikTok-Shop-Creator, 4 Accounts). Kein Programmierer: sprich Deutsch, per Du,
kurz und verständlich, Fachbegriffe nur wenn nötig.

## Abgrenzung

- Eigenes Projekt, **getrennt vom Editing-System** (`~/Documents/Coding/Editing System 1.1`, stammt von
  Nicolas Damerius, kuendigedeineneditor.de). Kopplung mit Nicolas abgeklärt (Artur, 09.11.2026).
- Das Editing System ruft nur unsere Befehle auf (Brücke dort: `eigene/TIKTOK-STEUERUNG.md`): `social1.py` (Social1-Liste → Produkt-IDs, Zuordnung
  macht Claude selbst), `stock.py` (Stock in dessen `Belege/`), `einreichen.py` (Video + JSON nach `uebergabe/eingang/`), `eingang.py freigeben|posten`.
  Format in `docs/UEBERGABE.md`. Im Editing System nur Arturs eigene Bereiche (`eigene/`) anfassen, nie Nicolas' Paket.
- Sync aufs 2. MacBook: `zsh werkzeuge/sync.sh holen` bei Chat-Start, `sichern` nach jedem Stapel
  (Repo `andreaskmh/tiktok-steuerung`, Gedächtnis liegt in `gedaechtnis/`).

## Was wo liegt

- `docs/KABEL.md` – iPhone per Kabel steuern (zuerst lesen). `docs/ABLAUF.md` – Abläufe am iPhone (alte Steuerung).
- `docs/UEBERGABE.md` – JSON-Format für `uebergabe/eingang` (Posten) und `uebergabe/ausgang` (Stock).
- `werkzeuge/` – Fenster-Aufnahme, Zeiger setzen, Prüfer; `test/` = Versuche, die nicht gewirkt haben.
  Bauen: `zsh werkzeuge/build.sh`.
- `vmaus/` – virtuelle Maus (Karabiner-Treiber), damit wird gewischt; gleiche Befehle wie das Mini-Gerät; `ANLEITUNG.md`.
- `geraet/` – Mini-Gerät (Arduino Pro Micro als echte USB-Maus), Sketch, `geraet.py`, `FLASHEN.md`.

## Arbeitsweise

- **Seit 12.11.2026: Bedienung per Kabel** (`docs/KABEL.md`): `open-iphone-use serve`, dann laufen alle Werkzeuge
  automatisch übers Kabel (`werkzeuge/kabel.py`: Foto, Tippen, Ziehen, Text, AirDrop fürs Video). Fotos: `python3 werkzeuge/kabel.py foto`.
- Alte Steuerung (iPhone-Synchronisierung + virtuelle Maus `vmaus/`, docs/ABLAUF.md) nur noch als Reserve (`TS_MODUS=sync`).
  Im Test nie tippen, wenn unklar ist, was dort liegt.
- Fortschritt in einer Zeile, Probleme selbst lösen, Artur nur fragen, wenn nur er es kann.

## Tempo (Artur, 08./09.11.2026 – gilt vor allem anderen)

- **Posten = `python3 werkzeuge/eingang.py posten <stapel>`** (= `post_mensch.py --stapel`, Arturs Ablauf, `docs/POSTEN-MENSCH.md`):
  ein Befehl pro Stapel im Hintergrund, findet jeden Schritt per Text-Label, Gefahren-Sperre bei jedem Tipp. Claude schaut nur bei
  `STOPP` per Foto nach. Test ohne Veröffentlichen: `--entwurf`. Keine Zwischenfotos.
- Kein Schritt fällt weg (Doppel-Schutz, Link, Button-Text, Beschreibung, Brand, Like, Speichern, Eintragen).
- **Nicht** mehr kontrollieren: orangener Shop-Button, Like, Speichern. Profil nicht neu laden.
- **Kein Abstand** zwischen Posts. Nach „+“: „Kamera nicht verfügbar“ → OK.
- Produkt nicht oben im Showcase → nicht scrollen/suchen, Einkaufswagen-Weg (Memory upload-speed-regeln).
- **Showcase voll** → STOPP, Artur fragen und auf seine Antwort warten (er löscht selbst), danach weitermachen.
- **Einkaufswagen voll** → irgendein Produkt aus dem Einkaufswagen entfernen (egal welches), weitermachen.
- **Produkt ausverkauft** → Video mit Text + Brand als **Entwurf** speichern, ohne Produktlink (posten.py macht das).
- **Tippen:** langsam (menschlich) nur in TikTok. Links/Adressleiste/Suche am iPhone schnell auf einmal (`posten.schnell`).
- **Kontext sparen (Artur 12.11.: nie über 500k, Stapel bis 50+ Videos):**
  - Lange Läufe (`stock.py --stapel`, `eingang.py posten`) im **Hintergrund**, danach nur die letzten Zeilen lesen
    (eine Zeile pro Produkt/Video). Kein Mitlesen, keine Zwischenfotos; Foto nur bei `STOPP` (`kabel.py foto`, möglichst Ausschnitt).
  - Keine großen Dateien/Logs ganz lesen (`tail`, `grep`). Abläufe sind fortsetzbar: Stock überspringt Fertiges,
    Posten arbeitet nach Status (`eingang.py liste`) → nach Abbruch oder in neuer Session einfach denselben Befehl starten.
  - **Übergabe:** nach jedem Stapel, alle ~20 Videos oder wenn der Chat lang wird (~300k): `docs/STAND.md` (wo stehen wir,
    nächster Befehl) aktualisieren, `sync.sh sichern`, dann **neue Session (fresh)** mit „Lies docs/STAND.md und mach weiter“
    (start_session bzw. hand_off_to_session) – nicht im vollen Chat weitermachen.

## Regeln (nicht verhandelbar)

- **Captchas, Logins, Passwörter, Codes macht Artur.** Bot-Schutz nie umgehen.
- **Nie blind tippen** in der Nähe von „Kasse“, „Einkaufswagen“, „Jetzt kaufen“ – vorher Bildschirmfoto.
- **Posten nur nach Arturs OK pro Stapel** (im Chat). **Seit 11.11.2026: Die Abnahme der Videos („passt“, `/fertig`, auch per Sprache) IST die Freigabe zum Posten** – danach ohne weitere Rückfrage (kein extra Posting-Plan) direkt posten. Ohne ein solches Signal von Artur/Andreas im Chat wird nie gepostet. **Kein Abstand** zwischen Posts (Artur 08.11. und 09.11.2026).
- Keine Käufe, keine Nachrichten, Kommentare oder Follows.
- Keine macOS-Sicherheitsabfragen klicken (z. B. „Zubehör erlauben“) – das macht Artur.
- Jede Änderung am System kurz in `docs/AENDERUNGEN.md` eintragen (Datum, was, warum).
