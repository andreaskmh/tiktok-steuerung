# Slideshow-Analyse: @klickguru vs. @andreasfastlane (20.11.2026)

Daten: öffentliche Profile (TikTok-Web, nicht eingeloggt), 144 klickguru-Posts + 198 eigene, Stand 20.11. morgens.

## Zahlen

| | klickguru | andreasfastlane |
|---|---|---|
| Follower / Likes | 27,8K / 1,6M | 3,2K / 108K |
| Posts pro Tag | 5–8, **über den Tag verteilt** (20–90 Min. Abstand) | **~30 in 40 Min.** (alle 2–3 Min.), dann Pause |
| Beschreibung | **komplett leer** – kein Text, keine Hashtags | 4–5 Hashtags, fast immer gleich: `#tiktokshopblackfriday #livedeals #superdeals …` |
| KI-Kennzeichnung (aigcLabel) | **bei jedem Post an** | eure Hits (1,4M / 1,2M, Okt.) **an**, die neuen Posts **aus** – obwohl KI-Bilder |
| Bilder pro Slideshow | 2–4 (Hits bis 7) | 1–6 |
| Produktlink | jeder Post | jeder Post |
| Sound | wenige Sounds immer wieder (v. a. „mike🕸️“: 5 Posts mit 112K–876K) | fast jeder Post ein anderer |
| Trefferquote | ~1 von 4 über 30K, viele 1M+ | seit 17.11. fast alles unter 1K |

**Wichtig:** Auch klickguru ist seit 19.11. eingebrochen (letzte 6 Posts: 373–921 Aufrufe). Ein Teil ist also
Black-Friday-Flut / Plattform, nicht nur ihr.

## Was klickguru inhaltlich macht

- **Bild 1 = Story/Meme, nicht Produkt:** „3 signs your jacket is trash“, Comic-Szene (3 Freunde im Herbst, „Aren't you cold?“),
  Weggabelung-Meme („Hoodie on SALE 80€“ vs. „4 for the same price“), „How to unf**k your boring room“.
- Danach 1–3 Bilder: Problem → Lösung → Produkt (echtes Produktfoto oft erst am Ende, mit „3 for the price of 1“).
- Viel **Englisch** bei Mode, Deutsch bei Deals (Adventskalender-Meme „Ihr den Purelei-Adventskalender schenken / mit ihr Schluss machen“).
- KI-Bilder offen gekennzeichnet (Label an).

## Eure Hits vs. eure Flops

- **Hits (Okt.):** Bild 1 = echtes Pärchen-/Selfie-Foto mit Gefühls-Hook („ps: wenn du sie nicht zum Weinen bringen willst …“,
  „also ihr habt doch NICHT bei dieser japanischen Zahnpasta gelogen“), Vorher/Nachher, KI-Label an.
- **Flops (Nov.):** Bild 1 = Produkt oder KI-Szene (Skelett, Chat mit „Mama“), Verkaufs-Hashtags, 30 Stück auf einmal, KI-Label aus.

## Wahrscheinliche Ursachen (Reihenfolge nach Gewicht)

1. **30 Posts in 40 Minuten:** TikTok verteilt neue Posts eines Accounts gegeneinander; Massen-Posting wirkt wie Spam/Bot
   → jeder Post bekommt nur einen winzigen Test-Pool (dreistellig). klickguru verteilt 5–8 Posts über den Tag.
2. **Verkaufs-Hashtags überall gleich** (`#tiktokshopblackfriday #livedeals #superdeals`): klar als Werbung erkennbar, alle
   Posts sehen gleich aus. klickguru schreibt gar nichts.
3. **KI-Bilder ohne KI-Label:** TikTok erkennt KI-Bilder auch selbst; nicht gekennzeichnete KI-Inhalte können von „Für dich“
   ausgeschlossen werden. Eure beiden Hits und alle klickguru-Posts haben das Label an → **Label anlassen** (kostet nichts).
4. **Gleiche Slideshows nur mit neuem Text:** TikTok erkennt wiederverwendete Bilder (Duplikat) → wenig Reichweite.
   Das passt dazu, dass es erst ging und dann nicht mehr.
5. **Bild 1 zeigt das Produkt statt einer Story/eines Gefühls** – klickguru und eure Hits starten mit Story/Meme/Mensch.

## Vorschlag zum Testen (1 Woche)

- Pro Account **max. 6–8 Slideshows pro Tag**, Abstand ≥ 45 Min. (posten über den Tag verteilt statt Stapel).
- **Beschreibung leer** oder 1 kurzer Satz ohne Hashtags; KI-Label **an**.
- Jede Slideshow **neue Bilder** (nie dieselben Bilder mit neuem Text).
- Bild 1 = Meme/Story/Gefühl („3 Zeichen, dass …“, Weggabelung, Pärchen-Hook), Produkt erst ab Bild 2–3, 2–4 Bilder.
- Sounds: Gewinner-Sounds wiederverwenden (die von euren / klickgurus Hits), nicht jedes Mal neu.
- A/B: 1 Account nach diesen Regeln, 1 Account wie bisher → nach 5 Tagen Aufrufe vergleichen.

## Research-Anbindung (umsetzbar)

- klickguru (und ähnliche Slideshow-Accounts) täglich auslesen: neue Posts, Aufrufe nach 24 h, Bild 1 + Sound
  → Liste „SLIDES-Vorbilder“ mit den Hits (> 30K) zum Nachbauen (eigene Bilder, gleiche Idee).

## Kopplung mit dem Editing System 1.5 (Slideshow-Auto) – Plan

Heute: Social1-Liste → `eigene/slideshow-auto` (ChatGPT-Bilder, Texte nah am Original) → `auto_posten.py` postet alles
direkt hintereinander (bis 50/Tag je Konto) → `post_slideshow.py` mit 3 Pflicht- + 2 Themen-Hashtags.

1. **Vorlagen-Quelle:** `research.py vorbilder` liest klickguru (+ weitere Slideshow-Accounts) und legt deren Hits (> 30K in 48 h)
   als Liste im selben Format wie `social1.py` ab → Slideshow-Auto kann sie direkt abarbeiten (Idee nachbauen, eigene Bilder).
2. **Posten verteilen:** `auto_posten.py`: Abstand ≥ 45 Min. und max. 8 Slideshows/Tag je Konto (statt 50 am Stück).
3. **Beschreibung/Label:** `post_slideshow.py`: Beschreibung leer bzw. ohne Hashtags, „KI-generierte Inhalte“ einschalten
   (Schalter unter „Weitere Optionen“, muss einmal am iPhone eingebaut werden).
4. **Bild 1 = Story/Meme-Hook** als Regel in `REZEPT-SLIDESHOW-AUTO.md`, Sound: Gewinner-Sounds wiederverwenden.
5. Test: andreasfastlane neu, anderes Konto wie bisher, nach 5 Tagen vergleichen.
