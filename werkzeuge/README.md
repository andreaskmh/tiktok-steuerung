# werkzeuge/

Alles läuft nach `zsh werkzeuge/build.sh` aus `werkzeuge/bin/`.

| Werkzeug | Zweck |
|---|---|
| `aufnahme.sh <ziel.png>` | Fenster der iPhone-Synchronisierung sauber aufnehmen (`screencapture -x -o -l <id>`) |
| `fenster [bundle]` | Fenster-ID + Lage der iPhone-Synchronisierung (`com.apple.ScreenContinuity`) |
| `galerie.sh <ordner> [produkt] [social1] [tts]` | alle Galerie-Bilder eines Produkts holen + `produkt.json` |
| `zaehler <bild.png>` | liest den Galerie-Zähler (z. B. `3 12`) per Texterkennung |
| `zeiger <x> <y>` / `zeiger rel <fx> <fy>` | Mauszeiger setzen, damit das Mini-Gerät an der richtigen Stelle wischt |

## test/ – Versuche vom 08.11.2026 (alle ohne Wirkung aufs iPhone)

| Datei | Was | Ergebnis |
|---|---|---|
| `swipe.swift` | künstliches Scrollen: `pad` (Trackpad-Phasen), `shift` (Mausrad + Shift), `h` (horizontal) | wird ignoriert |
| `rec.swift` | echte Gesten roh aufzeichnen (Event-Tap) | Aufnahme klappt |
| `play.swift` | aufgezeichnete Gesten 1:1 abspielen | wird ignoriert |
| `ana.swift` | Aufnahme auswerten (Phasen, Deltas) | Analyse |
| `info.swift` | Bildschirm, Fenster, Mausposition ausgeben | Hilfe |
| `ax.swift` | prüfen, ob Bedienungshilfen freigegeben sind | Hilfe |
| `felder.swift` | alle Felder eines aufgezeichneten Ereignisses ausgeben (echt vs. künstlich vergleichen) | Analyse |
| `echt.swift` | „echter“ wirkende Eingaben: Flags 0, Hardware-Zeitstempel (Feld 169), HID-Quelle, direkt an die App (`postToPid`), echte Aufnahme an die App | wird ignoriert (08.11., Galerie 11/12 blieb) |

Fazit: Nur echte Geräte wirken → Mini-Gerät (`../geraet/`).

## Weitere

| Werkzeug | Zweck |
|---|---|
| `pruefe_uebergabe.py [ordner]` | prüft JSONs in `uebergabe/` gegen `docs/UEBERGABE.md` |
| `build.sh` | übersetzt alle `.swift` nach `bin/` |
