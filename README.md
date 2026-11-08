# TikTok-Steuerung

Stock-Bilder aus TikTok-Shop-Produkten holen – und später Videos automatisch posten.
Läuft über die iPhone-Synchronisierung am Mac, gesteuert von Claude.

| Ordner | Inhalt |
|---|---|
| `docs/` | `ABLAUF.md` (wie es geht), `UEBERGABE.md` (Dateiformat), `AENDERUNGEN.md` |
| `werkzeuge/` | Fenster aufnehmen, Zeiger setzen, Übergabe prüfen; `test/` = alte Versuche |
| `geraet/` | Mini-Gerät (Arduino Pro Micro als echte Maus): Sketch, Mac-Skript, Flash-Anleitung, Wisch-Test |
| `vmaus/` | Plan B: virtuelle Maus über den Karabiner-Treiber (`ANLEITUNG.md`) |
| `uebergabe/` | `eingang/` (Videos zum Posten), `ausgang/` (Stock-Bilder), `beispiel/` |

## Stand 08.11.2026

- ✓ Produkt im TikTok Shop öffnen und Galerie-Bild aufnehmen
- ✗ Zum nächsten Bild wischen (Software wird ignoriert) → Mini-Gerät ist bestellt
- ☐ Virtuelle Maus einrichten (`vmaus/ANLEITUNG.md`) → Wisch-Test
- ☐ Wisch-Test mit dem Mini-Gerät (`geraet/FLASHEN.md`, dann `zsh geraet/wischtest.sh`)
- ☐ Alle Bilder eines Produkts automatisch holen
- ☐ Automatisch posten (mit Freigabe pro Stapel)

Erste Schritte:

```bash
zsh werkzeuge/build.sh
zsh werkzeuge/aufnahme.sh ~/Desktop/test.png
```
