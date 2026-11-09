# TikTok-Steuerung – Anweisungen für Claude

Dieses Projekt holt **Stock-Bilder aus TikTok-Shop-Produkten** (für Bottom-of-Funnel-Videos) und soll
später **Videos automatisch posten** (Showcase-Produkt verlinken, Beschreibung, Hashtags).
Nutzer ist **Artur** (TikTok-Shop-Creator, 4 Accounts). Kein Programmierer: sprich Deutsch, per Du,
kurz und verständlich, Fachbegriffe nur wenn nötig.

## Abgrenzung

- Eigenes Projekt, **getrennt vom Editing-System** (`~/Documents/Coding/Editing System 1.1`, stammt von
  Nicolas Damerius, kuendigedeineneditor.de). Kopplung mit Nicolas abgeklärt (Artur, 09.11.2026).
- Das Editing System ruft nur unsere Befehle auf (Brücke dort: `eigene/TIKTOK-STEUERUNG.md`): `stock.py` (Stock in
  dessen `Belege/`), `einreichen.py` (Video + JSON nach `uebergabe/eingang/`), `eingang.py freigeben|posten`.
  Format in `docs/UEBERGABE.md`. Im Editing System nur Arturs eigene Bereiche (`eigene/`) anfassen, nie Nicolas' Paket.
- Sync aufs 2. MacBook: `zsh werkzeuge/sync.sh holen` bei Chat-Start, `sichern` nach jedem Stapel
  (Repo `andreaskmh/tiktok-steuerung`, Gedächtnis liegt in `gedaechtnis/`).

## Was wo liegt

- `docs/ABLAUF.md` – der erprobte Ablauf am iPhone (zuerst lesen).
- `docs/UEBERGABE.md` – JSON-Format für `uebergabe/eingang` (Posten) und `uebergabe/ausgang` (Stock).
- `werkzeuge/` – Fenster-Aufnahme, Zeiger setzen, Prüfer; `test/` = Versuche, die nicht gewirkt haben.
  Bauen: `zsh werkzeuge/build.sh`.
- `vmaus/` – virtuelle Maus (Karabiner-Treiber), damit wird gewischt; gleiche Befehle wie das Mini-Gerät; `ANLEITUNG.md`.
- `geraet/` – Mini-Gerät (Arduino Pro Micro als echte USB-Maus), Sketch, `geraet.py`, `FLASHEN.md`.

## Arbeitsweise

- Bedienung über die **iPhone-Synchronisierung** per Computer-Use (`app_*`-Werkzeuge).
  Fotos immer mit `werkzeuge/aufnahme.sh` (nur das Fenster).
- Wischen geht mit der **virtuellen Maus** (`vmaus/`) über `geraet/geraet.py` – vor jedem Wisch kurz `MOVE` im iPhone-Fenster
  (weckt es auf, docs/ABLAUF.md). Bilder holen: `werkzeuge/galerie.sh`. Im Test nie klicken, wenn unklar ist, was unter dem Zeiger liegt; Software-Wischen ist ausprobiert und wirkt nicht.
- Fortschritt in einer Zeile, Probleme selbst lösen, Artur nur fragen, wenn nur er es kann.

## Tempo (Artur, 08./09.11.2026 – gilt vor allem anderen)

- **Posten = `python3 werkzeuge/posten.py <stapel.json>`**: ein Befehl pro Stapel, prüft jeden Schritt selbst per
  Texterkennung (`werkzeuge/seh.py`). Claude schaut nur bei `STOPP` per Foto nach. Keine Zwischenfotos.
- Kein Schritt fällt weg (Doppel-Schutz, Link, Button-Text, Beschreibung, Brand, Like, Speichern, Eintragen).
- **Nicht** mehr kontrollieren: orangener Shop-Button, Like, Speichern. Profil nicht neu laden.
- **Kein Abstand** zwischen Posts. Nach „+“: „Kamera nicht verfügbar“ → OK.
- Produkt nicht oben im Showcase → nicht scrollen/suchen, Einkaufswagen-Weg (Memory upload-speed-regeln).
- **Showcase voll** → STOPP, Artur fragen und auf seine Antwort warten (er löscht selbst), danach weitermachen.
- **Einkaufswagen voll** → irgendein Produkt aus dem Einkaufswagen entfernen (egal welches), weitermachen.
- **Produkt ausverkauft** → Video mit Text + Brand als **Entwurf** speichern, ohne Produktlink (posten.py macht das).
- **Tippen:** langsam (menschlich) nur in TikTok. Links/Adressleiste/Suche am iPhone schnell auf einmal (`posten.schnell`).
- **Kontext:** Nach jedem Stapel, spätestens bei ~500k Token: `docs/STAND.md` aktualisieren, committen und eine
  **neue Session (fresh)** starten mit „Lies docs/STAND.md und mach weiter“ – nicht im vollen Chat weitermachen.

## Regeln (nicht verhandelbar)

- **Captchas, Logins, Passwörter, Codes macht Artur.** Bot-Schutz nie umgehen.
- **Nie blind tippen** in der Nähe von „Kasse“, „Einkaufswagen“, „Jetzt kaufen“ – vorher Bildschirmfoto.
- **Posten nur nach Arturs OK pro Stapel** (im Chat). **Kein Abstand** zwischen Posts (Artur 08.11. und 09.11.2026).
- Keine Käufe, keine Nachrichten, Kommentare oder Follows.
- Keine macOS-Sicherheitsabfragen klicken (z. B. „Zubehör erlauben“) – das macht Artur.
- Jede Änderung am System kurz in `docs/AENDERUNGEN.md` eintragen (Datum, was, warum).
