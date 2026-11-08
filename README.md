# TikTok-Steuerung

Stock-Bilder aus TikTok-Shop-Produkten holen – und später Videos automatisch posten.
Läuft über die iPhone-Synchronisierung am Mac, gesteuert von Claude.

| Ordner | Inhalt |
|---|---|
| `docs/` | `ABLAUF.md` (wie es geht), `UEBERGABE.md` (Dateiformat), `AENDERUNGEN.md` |
| `werkzeuge/` | Fenster aufnehmen, Zeiger setzen, Übergabe prüfen; `test/` = alte Versuche |
| `geraet/` | Mini-Gerät (Arduino Pro Micro als echte Maus): Sketch, Mac-Skript, Flash-Anleitung, Wisch-Test |
| `vmaus/` | virtuelle Maus über den Karabiner-Treiber (`ANLEITUNG.md`) |
| `uebergabe/` | `eingang/` (Videos zum Posten), `ausgang/` (Stock-Bilder), `beispiel/` |

## Stand 08.11.2026

- ✓ Produkt im TikTok Shop öffnen und Galerie-Bild aufnehmen
- ✓ Zum nächsten Bild wischen – mit der virtuellen Maus (`vmaus/`), nach einmaligem „Aufwecken“ per Trackpad
- ✓ Alle Bilder eines Produkts automatisch holen (`werkzeuge/galerie.sh`)
- ☐ Mehrere Produkte nacheinander (Social1-Liste abarbeiten)
- ○ Mini-Gerät nur noch als Reserve
- ☐ Automatisch posten (mit Freigabe pro Stapel)

Erste Schritte:

```bash
zsh werkzeuge/build.sh
zsh werkzeuge/aufnahme.sh ~/Desktop/test.png
```
