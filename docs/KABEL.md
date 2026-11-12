# iPhone per Kabel steuern (seit 12.11.2026)

Ersetzt die iPhone-Synchronisierung + virtuelle Maus. Grundlage: [open-iphone-use](https://github.com/semsturgut/open-iphone-use)
(Klon: `~/Documents/Coding/extern/open-iphone-use`), nutzt Xcodes CoreDevice: Live-Bild vom iPhone, Tipps landen genau,
kein Zeiger, kein „Aufwecken“, keine doppelten Tipps.

## Automatisch (Wächter, seit 12.11.2026)

`werkzeuge/kabel/waechter.py` prüft alle 20 s: Server aus → starten; Kabel steckt, Server auf WLAN → neu starten (USB);
iPhone nicht eingebunden → einbinden. Als Autostart beim Anmelden (einmalig, macht Artur selbst):
```bash
zsh werkzeuge/kabel/autostart.sh an       # aus: … aus   |   Stand: … status   |   Protokoll: ~/Library/Logs/ts-iphone-waechter.log
```
Nach Änderungen an waechter.py erneut `an` ausführen (kopiert die Fassung nach ~/.local/share/ts-iphone-waechter/).

## Von Hand starten (ohne Wächter)

```bash
open-iphone-use stop; open-iphone-use serve     # ~20 s, nimmt USB, wenn das Kabel steckt (sonst WLAN)
python3 werkzeuge/kabel.py status               # → „USB  verbunden=True  bild=True“
```
Live zuschauen: http://127.0.0.1:27893 . Der Server wechselt **nicht** von selbst von WLAN auf USB → nach dem Einstecken neu starten.

Alle Werkzeuge (`seh.py`, `tap.py`, `posten.py`, `post_wagen.py`, `stock.py`, `eingang.py`) nehmen automatisch das Kabel,
sobald der Server ein Live-Bild liefert. Alte Steuerung erzwingen: `TS_MODUS=sync`.

## Was wie geht

| Aufgabe | Kabel |
|---|---|
| Foto | `kabel.foto()` – verlustfreies PNG 832×1808 (≈ volle iPhone-11-Auflösung) |
| Tippen | `kabel.tipp(x, y)` – Punkte 334×735 wie das alte Fenster, alle festen Werte gelten weiter |
| Wischen/Ziehen | `kabel.ziehe(x1, y1, x2, y2, dauer)` – echtes Ziehen (Karte hochziehen, Galerie wischen) |
| Tasten | `kabel.taste("home")`, `"return"`, `"cmd+v"` … |
| Text | `kabel.text(t, menschlich=True)` – deutsches Layout (Umlaute, ß, #, @), keine Emojis |
| Einfügen | `kabel.einfuegen(t)` – gemeinsame Zwischenablage Mac → iPhone + ⌘V (~2 s, auch Emojis) |
| Video aufs iPhone | `python3 werkzeuge/airdrop.py <video> …` – AirDrop an „iPhone von Artur (2)“, ~11 s, landet in Fotos |

## Einmalig eingerichtet

- Xcode 27.2, iPhone 11 auf iOS 27.2.1, Entwicklermodus an (Artur, 12.11.2026).
- AirDrop am iPhone: Einstellungen → Allgemein → AirDrop → **Nur für Kontakte** (vorher „Empfangen aus“, Artur OK 12.11.).
  Gleiche Apple-ID → keine Abfrage, das Video öffnet sich direkt in Fotos.
- Server-Erweiterung: `python3 werkzeuge/kabel/patch_oiu.py` (Live-Bild-Fix, Ziehen, rohe Tasten, PNG).
  **Nach jeder Neuinstallation/Aktualisierung von open-iphone-use erneut ausführen**, dann Server neu starten.

## Stolpersteine

- iPhone muss **entsperrt** sein (Auto-Sperre lang stellen). Entsperren/Code macht Artur.
- Kamera ist per Kabel verfügbar → der Hinweis „Kamera nicht verfügbar“ kommt nicht mehr (Code kann beides).
- „Neu in Fotos“-Hinweis beim ersten Öffnen der Galerie → „Fortfahren“ (airdrop.py tippt es selbst).
- Gelöschte Videos stehen in TikToks Galerie noch kurz als schwarze 00:00-Kacheln.
- Ganzer Post per Kabel getestet (12.11., als Entwurf): `python3 werkzeuge/test/kabel_posttest.py <eingang-json>` (OHNE_AIRDROP=1,
  wenn das Video schon am iPhone ist). Echte Veröffentlichung per Kabel steht noch aus → 1. Post im Stapel mitschauen.
- iPhone-**Tastatursteuerung** (Bedienungshilfen) muss AUS sein, sonst drückt die Leertaste fokussierte Knöpfe (z. B. Zurück).
- TikTok-Kopfbereich liegt per Kabel ~35 Pkt höher als im alten Fenster (`posten.oben()`), unten passt alles.
