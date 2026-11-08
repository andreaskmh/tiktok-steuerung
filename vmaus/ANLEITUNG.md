# Virtuelle Maus (eingerichtet 08.11.2026, funktioniert)

Der Treiber **Karabiner-DriverKit-VirtualHIDDevice** (von pqrs.org, Apple-notarisiert, gemeinfrei)
meldet im System eine virtuelle USB-Maus + Tastatur an, die macOS wie echte Hardware behandelt.
`vmaus` steuert sie und versteht dieselben Befehle wie das Mini-Gerät (`geraet/geraet.py`).

Der Treiber nimmt Befehle nur von Programmen mit Admin-Rechten an. Deshalb läuft `vmaus` einmal
eingerichtet als Hintergrunddienst und lauscht auf `/var/run/tiktok-maus.sock` – das darf nur
Arturs Benutzer öffnen. **Danach gibt es keine Abfragen mehr**, auch nicht nach einem Neustart.

## Einmalig einrichten (Artur, ca. 3 Minuten)

1. **Treiber installieren:** Doppelklick auf `vmaus/Karabiner-DriverKit-VirtualHIDDevice-8.8.0.pkg`
   → Installieren → Mac-Passwort.
2. **Treiber aktivieren:** Claude führt aus:
   `/Applications/.Karabiner-VirtualHIDDevice-Manager.app/Contents/MacOS/Karabiner-VirtualHIDDevice-Manager activate`
   → macOS meldet „Systemerweiterung blockiert“ → **Systemeinstellungen → Allgemein → Anmeldeobjekte &
   Erweiterungen → Treibererweiterungen** → „Karabiner-DriverKit-VirtualHIDDevice“ einschalten (Passwort).
   Verlangt macOS einen Neustart: neu starten, danach „weiter“ schreiben.
3. **Dienste einrichten:** im Terminal (einmal Passwort):
   ```bash
   sudo zsh ~/Documents/Coding/TikTok-Steuerung/vmaus/einrichten.sh
   ```
   Geht das Passwort im Terminal der Claude-App nicht: Claude kopiert `einrichten.sh` + `bin/vmaus` nach
   `/Users/Shared/tiktok-vmaus-setup/` (Admin-Skripte dürfen nicht in ~/Documents lesen) und startet es per
   `osascript … with administrator privileges` → normales macOS-Passwortfenster. Danach Kopie löschen.
   Am Ende steht `OK pointing=1 keyboard=1` → fertig.
4. Erscheint der **Tastatur-Assistent** („Tastatur identifizieren“): einfach schließen.

## Benutzen

```bash
python3 geraet/geraet.py STATUS            # OK pointing=1 keyboard=1
werkzeuge/bin/zeiger rel 0.5 0.45
python3 geraet/geraet.py "SCROLL -1 0 6"   # echtes horizontales Mausrad
zsh geraet/wischtest.sh                    # alle Wisch-Arten mit Fotos
```

Steckt später das Mini-Gerät, nimmt `geraet.py` automatisch das Gerät (oder `--port` angeben).

## Neu bauen / Updates

`zsh vmaus/build.sh` (ohne sudo), danach `sudo zsh vmaus/einrichten.sh` erneut – das kopiert das neue
Programm an seinen geschützten Ort. Treiber und Client müssen dieselbe Protokoll-Version haben
(8.8.0 = Protokoll 7); bei einem Treiber-Update auch `vmaus/quelle/` auf dieselbe Version bringen.

## Entfernen

`sudo zsh vmaus/entfernen.sh` (Dienste weg), Treiber-Deinstallation steht am Ende der Ausgabe.

## Sicherheit

- `/usr/local/libexec/tiktok-vmaus` gehört root – kein anderes Programm kann es austauschen.
- Das Socket gehört nur Arturs Benutzer (Rechte 0600).
- Die virtuelle Maus kann alles, was eine echte Maus kann. Es gelten die Regeln aus `CLAUDE.md`
  (nie blind bei Kasse/Einkaufswagen, Posten nur nach OK).

## Aufwecken

Nach dem Entsperren der iPhone-Synchronisierung reagiert sie erst auf die virtuelle Maus, wenn einmal eine echte
Trackpad-Berührung kam (Finger kurz drauflegen). Danach dauerhaft. Details: `docs/ABLAUF.md`.
