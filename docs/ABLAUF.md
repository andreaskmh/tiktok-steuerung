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

Nach ein paar Minuten Pause (oder nach einem Fensterwechsel) ignoriert die iPhone-Synchronisierung Scroll-Befehle,
bis sich der Zeiger **im iPhone-Fenster bewegt**. Eine kleine Bewegung der virtuellen Maus reicht:
`MOVE 4 0` + `MOVE -4 0` direkt vor jedem Wisch (macht `galerie.sh` automatisch). Getestet 08.11.: 7/7 Schritte
ohne Arturs Zutun. Eine echte Trackpad-Berührung ist **nicht** nötig.

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
  Hashtags, posten. **Kein Abstand** zwischen Posts (Artur 09.11.2026).

## Regeln (immer)

- Captchas, Logins, Passwörter, Zwei-Faktor-Codes macht **Artur**. Bot-Schutz nie umgehen.
- Nie in der Nähe von **„Kasse“, „Einkaufswagen“, „Jetzt kaufen“** blind tippen – vorher Bildschirmfoto ansehen.
- Posten nur nach Arturs OK **pro Stapel**.
- Keine Nachrichten, Kommentare oder Follows.

## ⚠️ Gefahrenstelle beim Upload (Vorfall 08.11.2026, 21:16)

Im TikTok-Editor liegt **„Weiter“ unten rechts genau dort, wo auf der nächsten Seite „Veröffentlichen“ liegt**.
Tipps über die iPhone-Synchronisierung kommen manchmal **doppelt bzw. verzögert** an → der zweite Tipp hat das Video
ohne Beschreibung/Link sofort veröffentlicht (artur.official, Schokoellsen).

Regeln ab jetzt:
- Nach jedem Tipp unten rechts (Weiter) **sofort den Zeiger aus der unteren Leiste wegbewegen** (z. B. in die obere Bildhälfte)
  und 2 s warten, bevor irgendetwas anderes passiert.
- Auf der Beitragsseite **nie** in den Bereich der unteren Knöpfe (Entwürfe / Veröffentlichen) tippen, außer für das
  freigegebene Veröffentlichen ganz am Schluss.
- „Weiter“ im Editor nur **einmal** tippen, dann per Foto prüfen – nie ein zweites Mal „zur Sicherheit“.
- Unten links im Editor ist „Deine Story“ → sofort veröffentlicht, nie antippen.

## Erprobter Upload-Ablauf (08.11.2026, Schokoellsen auf artur.official)

**Zeiger-Regel (wichtigste Regel):** Der erste Tipp landet dort, wo der iPhone-Zeiger zuletzt war. Deshalb vor
**jedem** Tipp den Zeiger per `app_scroll` (dy 0) an die Zielstelle holen, per Foto prüfen, dann `app_click`.
Nach einem Tipp unten rechts (Weiter/Hinzufügen) sofort `app_scroll` an eine sichere Stelle oben (z. B. 200,60).
Über Dialogen geht `app_scroll` nicht → nur tippen, wenn der Zeiger vorher an einer sicheren Stelle stand.
Klappt ein Textfeld gar nicht, bitte Artur einmal kurz mit dem Trackpad ins Feld zu tippen.

0. **Doppel-Schutz:** `zsh werkzeuge/gepostet.sh pruefen "<video>"` → nur bei „NEU“ weitermachen.
1. Video aufs iPhone: Fotos-App am iPhone öffnen, Datei im Finder **am Dateinamen** greifen (nicht Symbolmitte =
   Play-Knopf) und mit `werkzeuge/ziehen.py` ins iPhone-Fenster ziehen. Finder und iPhone-Fenster vorher nach vorne.
2. Account wechseln: Profil → Name oben antippen → Account wählen.
3. Produkt ins Showcase: Safari → `social1.ai/products/<id>` → „View on TikTok Shop“ → Provisions-Badge
   („Verdiene … pro Verkauf“) → „Zum Showcase hinzufügen“ (danach heißt der Knopf „Mehr erkunden“).
   Nie „Kasse“; „Einkaufswagen“ nur, wenn Showcase nicht geht. **Pro Account neu.**
4. Upload: + → Galerie unten links → Video → Weiter → Weiter (Editor; unten links „Deine Story“ nie!).
   Zwischendurch geht „Entwürfe“ (Profil → Video-Reiter → Kachel „Entwürfe“).
5. Beitragsseite: Beschreibung tippen; Brand über **„@ Erwähnung“** suchen und den Shop-Account wählen.
6. Link hinzufügen → Produkt → (Hinweis Provisionsschutz: „OK, verstanden“) → im Showcase „Hinzufügen“ →
   „Hinzufügen“ bestätigen → Feld „Produktname“ leeren (Rücktaste) → Button-Text (siehe docs/ACCOUNTS.md) → Hinzufügen.
6b. **Nur einmalig pro iPhone** (bleibt gespeichert): unter **Weitere Optionen** höchste Qualität / hochwertige
    Uploads **an** und „Auf Gerät speichern“ (automatisch in die Galerie) **aus**. Bei jedem weiteren Upload nicht mehr prüfen.
    Erledigt auf: iPhone 11 (Artur) – siehe docs/AENDERUNGEN.md.
7. Dialog „gesponsert offenlegen“ → „Posten zustimmen“ (schließt nur den Dialog) → **Veröffentlichen**.
   Artur will **keine Rückfrage vor dem Veröffentlichen**, wenn alles stimmt (08.11.2026).
7b. Nach dem Veröffentlichen: eigenes Video **liken** (Herz) und **speichern** (Lesezeichen → „Gespeichert“).
7d. Sofort eintragen: `zsh werkzeuge/gepostet.sh eintragen "<video>" <account>` (Liste: `uebergabe/ausgang/gepostet.txt`).
7c. **Profilseite neu laden** (oben runterziehen) und im Video prüfen, ob der **orangene Produkt-Button** da ist.

**Feld „Produktname“ lässt sich nicht per Bedienung aktivieren** (eingebettete Web-Eingabe). Arturs Trackpad-Tipp
kommt beim Mac als Klick mit Untertyp „Touch“ an (CGEvent-Feld 7 = 3, Druck 255, Feld 108 = 1); unsere Klicks
haben das nicht. Nächster Versuch: eigener Klick mit diesen Feldern (werkzeuge/test/). Bis dahin: Artur tippt einmal ins Feld.
8. Vorsicht im Video-Feed: roter Balken „… Aufrufe für … €“ (Promote) direkt unter der Navigationsleiste – nie antippen.

**Feld „Produktname“ (Erkenntnis 08.11.2026, Artur):** Direkt nach „Hinzufügen“ im Showcase ist das Feld bereits **aktiv**.
Sofort löschen (Rücktaste) und tippen – **kein** Klick, Scroll oder Zeiger-Setzen dazwischen, sonst verliert es den Fokus.
Klappt es nicht: zurück, Produkt nochmal „Hinzufügen“. Erprobtes Rezept: „Hinzufügen“ per app_click → Seite „Produkt umbenennen“ → `werkzeuge/bin/tipp rel 0.838 0.512` (rechts ins Feld) → sofort Rücktaste ×30 und tippen.
