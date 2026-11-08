# Ablauf (erprobt am 08.11.2026)

## Warum über das iPhone?

TikTok Shop ist am Mac leer (auch für Affiliates). Deshalb läuft alles über die
**iPhone-Synchronisierung** (macOS-App, Bundle `com.apple.ScreenContinuity`, iPhone 11 gespiegelt).
Claude bedient sie per Computer-Use (`app_*`-Werkzeuge). Freigaben für Bildschirmaufnahme und
Bedienungshilfen sind erteilt.

## Stock-Bilder eines Produkts holen

1. iPhone-Synchronisierung öffnen. Zum Home-Bildschirm: Menü **Darstellung → Home-Bildschirm**.
2. **Safari** auf dem iPhone öffnen → Social1-Liste (z. B. `social1.ai/saved-videos/…`).
   - Scrollen in Safari: **Pfeiltasten** (Wischen geht noch nicht, siehe unten).
3. Beim Video aufs **Produktbadge** tippen → **„View on TikTok Shop“**.
   - Tippen klappt oft erst beim **zweiten Klick**.
4. Das Produkt öffnet sich in der **TikTok-App** → aufs Produktbild tippen.
5. Vollbild-Galerie mit Zähler (z. B. `8/12`).
6. Fenster aufnehmen:
   ```bash
   zsh werkzeuge/aufnahme.sh uebergabe/ausgang/<produkt>/bild-01.png
   ```
   Ergebnis: nur das iPhone-Fenster, 668–694 px breit, ohne Schatten.
7. Alle Bilder automatisch holen:
   ```bash
   zsh werkzeuge/galerie.sh <ordnername> "<Produktname>" "<social1_link>" "<tts_link>"
   ```
   Geht zurück auf Bild 1, nimmt jedes Bild auf, wischt weiter (`SHIFTSCROLL ±7 10` = genau ein Bild) und prüft
   jedes Mal den Zähler (`werkzeuge/bin/zaehler`). Ergebnis in `uebergabe/ausgang/<ordnername>/`.

### Die virtuelle Maus „aufwecken“ (wichtig!)

Die iPhone-Synchronisierung nimmt die virtuelle Maus erst an, nachdem einmal eine **echte** Berührung kam
(Finger kurz aufs Trackpad legen, ohne zu bewegen). Danach wirkt sie dauerhaft, auch ohne Finger
(getestet über mehrere Minuten). Nach Sperren/Entsperren der iPhone-Synchronisierung wohl wieder nötig.
Anzeichen: Befehle sagen „OK“, aber das Bild bewegt sich nicht → Artur bitten, einmal kurz das Trackpad zu berühren.

Weitere Regeln:
- Das iPhone-Fenster muss **vorne** sein (`open -b com.apple.ScreenContinuity`), sonst landet das Scrollen im Fenster darüber.
- Zeiger direkt vor jedem Befehl neu setzen (`zeiger rel 0.5 0.45`).
- Senkrecht scrollen: `SCROLL 0 ±10 n 15`. Zur Galerie: Seite nach oben, dann `CLICK` in die Bildmitte (≈ 40 % Höhe,
  „Kasse“ liegt bei ≈ 90 %) – vorher immer Foto prüfen.
- Kleine Rad-Mengen (unter ~6 schnellen Rasten) bewirken in der Galerie nichts.

## Was NICHT geht (alles am 08.11. probiert)

- Künstliches Scrollen/Wischen per Software: CGEvent-Scroll mit Trackpad-Phasen, Shift + Mausrad,
  aufgezeichnete echte Gesten 1:1 abgespielt (`werkzeuge/test/`) → wird von der iPhone-Synchronisierung
  ignoriert. Ebenso „bereinigte“ Ereignisse (keine Synthetik-Flags, Hardware-Zeitstempel, direkt an die App
  geschickt, `werkzeuge/test/echt.swift`). Echte Ereignisse tragen intern eine Geräte-Kennung, die sich per
  Software nicht setzen lässt. Nur **echte Geräte** wirken (Trackpad mit 2 Fingern, Maus mit Shift + Scroll).
- AssistiveTouch-Menü wird nicht gespiegelt.
- Tastatursteuerung am iPhone (Bedienungshilfen) blockierte die Eingaben → wieder aus.

- Vorsicht beim Testen: Jede Berührung von Arturs Trackpad/Maus (auch ein Wassertropfen!) verfälscht das Ergebnis → immer mit
  `werkzeuge/bin/rec` mitschneiden und prüfen, dass nur die eigenen Ereignisse drin sind.

**Lösung (funktioniert seit 08.11.2026):** virtuelle Maus über den Karabiner-Treiber (`vmaus/`) – oder als Reserve das Mini-Gerät = Arduino Pro Micro als echte USB-Maus (`geraet/`). Beide über `geraet/geraet.py`.

## Reserve: Mini-Gerät (falls die virtuelle Maus einmal nicht geht)

1. Gerät flashen (`geraet/FLASHEN.md`), anstecken, `python3 geraet/geraet.py ping` → `OK PONG`.
2. iPhone: ein Produkt in der Vollbild-Galerie öffnen (Zähler sichtbar, z. B. `1/12`).
3. `zsh geraet/wischtest.sh` → probiert `SHIFTSCROLL`, horizontales `SCROLL` und `DRAG` und macht nach
   jedem Versuch ein Fensterfoto in `uebergabe/ausgang/wischtest-…/`.
4. Am Zähler sehen, welche Art wirkt. Die nehmen wir dann fest in den Ablauf (Schritt 7 oben).

## Später: automatisch posten

Ablauf noch nicht gebaut. Geplant:
- Fertiges Video + JSON liegen in `uebergabe/eingang/` (Format: `docs/UEBERGABE.md`).
- Claude zeigt Artur den ganzen **Stapel** (Video, Account, Produkt, Titel, Hashtags).
- **Erst nach Arturs OK** pro Stapel: Video hochladen, Showcase-Produkt verlinken, Beschreibung +
  Hashtags, posten. **5 Minuten Abstand** zwischen zwei Posts.

## Regeln (immer)

- Captchas, Logins, Passwörter, Zwei-Faktor-Codes macht **Artur**. Bot-Schutz nie umgehen.
- Nie in der Nähe von **„Kasse“, „Einkaufswagen“, „Jetzt kaufen“** blind tippen – vorher Bildschirmfoto ansehen.
- Posten nur nach Arturs OK **pro Stapel**.
- Keine Nachrichten, Kommentare oder Follows.
