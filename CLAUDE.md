# TikTok-Steuerung – Anweisungen für Claude

Dieses Projekt holt **Stock-Bilder aus TikTok-Shop-Produkten** (für Bottom-of-Funnel-Videos) und soll
später **Videos automatisch posten** (Showcase-Produkt verlinken, Beschreibung, Hashtags).
Nutzer ist **Artur** (TikTok-Shop-Creator, 4 Accounts). Kein Programmierer: sprich Deutsch, per Du,
kurz und verständlich, Fachbegriffe nur wenn nötig.

## Abgrenzung

- Eigenes Projekt, **getrennt vom Editing-System** (`~/Documents/Coding/Editing System 1.1`, stammt von
  Nicolas Damerius, kuendigedeineneditor.de). Dort **nichts ändern**. Eine Kombination beider Projekte
  erst nach Absprache mit Nicolas.
- Einzige Schnittstelle: `uebergabe/` (Format in `docs/UEBERGABE.md`).

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

## Regeln (nicht verhandelbar)

- **Captchas, Logins, Passwörter, Codes macht Artur.** Bot-Schutz nie umgehen.
- **Nie blind tippen** in der Nähe von „Kasse“, „Einkaufswagen“, „Jetzt kaufen“ – vorher Bildschirmfoto.
- **Posten nur nach Arturs OK pro Stapel** (im Chat). **Kein Abstand** zwischen Posts (Artur 08.11. und 09.11.2026).
- Keine Käufe, keine Nachrichten, Kommentare oder Follows.
- Keine macOS-Sicherheitsabfragen klicken (z. B. „Zubehör erlauben“) – das macht Artur.
- Jede Änderung am System kurz in `docs/AENDERUNGEN.md` eintragen (Datum, was, warum).
