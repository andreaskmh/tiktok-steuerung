# Mini-Gerät flashen (Arduino Pro Micro, ATmega32U4)

Das Gerät ist eine echte USB-Maus + Tastatur. Der Mac (und damit die iPhone-Synchronisierung)
hält es für ein normales Gerät – deshalb wirkt Wischen damit, künstliche Eingaben nicht.

## Einmalig: arduino-cli installieren

```bash
brew install arduino-cli
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install Mouse Keyboard
```

## Gerät anstecken und erkennen

```bash
arduino-cli board list
```

Es erscheint ein Port wie `/dev/cu.usbmodem1101`. Fragt macOS „Zubehör erlauben?“ → **Artur klickt
„Erlauben“** (Claude klickt keine macOS-Sicherheitsabfragen). Ein Tastatur-Assistent („Tastatur
identifizieren“) darf geschlossen werden.

## Übersetzen und aufspielen

Die meisten Pro-Micro-Klone melden sich als **Arduino Leonardo** – deshalb dieses Board:

```bash
cd ~/Documents/Coding/TikTok-Steuerung/geraet
arduino-cli compile --fqbn arduino:avr:leonardo hid_maus
arduino-cli upload  --fqbn arduino:avr:leonardo -p /dev/cu.usbmodemXXXX hid_maus
```

Klappt der Upload nicht („Couldn't find a Board“): Beim Pro Micro gibt es keinen Reset-Knopf.
Kurz **RST mit GND** verbinden (zweimal schnell), dann innerhalb von 8 Sekunden den Upload-Befehl
starten. Der Port heißt danach evtl. anders – mit `arduino-cli board list` nachsehen.

Falls es ein SparkFun-Board ist und Leonardo nicht passt: SparkFun-Boardpaket hinzufügen und
`SparkFun:avr:promicro:cpu=16MHzatmega32U4` nehmen (5-V-Version) bzw. `8MHzatmega32U4` (3,3 V).
**Falsche Taktfrequenz = Board meldet sich nicht mehr** → dann mit dem RST-Trick und der richtigen
Variante neu flashen.

## Testen

```bash
python3 geraet/geraet.py ping            # -> PING -> OK PONG
werkzeuge/bin/zeiger rel 0.5 0.45        # Zeiger in die Mitte vom iPhone-Fenster
python3 geraet/geraet.py "SHIFTSCROLL -3"
```

Dann den ganzen Wisch-Test: `zsh geraet/wischtest.sh` (siehe `docs/ABLAUF.md`).

## Befehle

Stehen oben im Sketch `hid_maus/hid_maus.ino`: `PING`, `SCROLL dx dy n [ms]`, `SHIFTSCROLL n [ms]`,
`MOVE dx dy`, `DRAG dx dy steps [ms]`, `CLICK [L|R|M]`, `PRESS`/`RELEASE`, `KEY name`, `TYPE text`, `STOP`.

**Hinweis TYPE:** Das Gerät tippt mit US-Tastaturbelegung. Auf einem deutschen Mac werden z. B.
`y`/`z` vertauscht und Umlaute fehlen. Für Texte deshalb weiter die Text-Eingabe über Computer-Use nehmen.

**Notfall:** Spinnt das Gerät, einfach abziehen. `python3 geraet/geraet.py STOP` lässt alle Tasten los.
