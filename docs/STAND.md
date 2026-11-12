# Stand & nächste Schritte (zuletzt 12.11.2026)

**Zuerst lesen:** `CLAUDE.md` → `docs/ABLAUF.md` → `docs/ACCOUNTS.md`. Memory: upload-speed-regeln, produkt-immer-ueber-social1.

## Offen
- Stapel 08.11. komplett (12/12). artur.official 09.11.: Tunnelblick 00:29, Rock Shorts 00:35.
- Rock Shorts: orangener Shop-Button direkt nach Post noch nicht sichtbar (Link war gesetzt) → Artur kurz prüfen.
- **Neu: `werkzeuge/posten.py <stapel.json>`** postet einen ganzen Stapel am Stück (Texterkennung statt Fotos).
  Noch nicht live gelaufen → beim ersten Video mitschauen; bei STOPP Foto machen und von Hand weiter.
  Vorlage: `uebergabe/beispiel/stapel-posten.json`.
- **`werkzeuge/stock.py`** läuft (09.11. getestet: Hosenrock 2/2 Bilder). Wichtig: TikTok zeigt erst eine Vorschaukarte,
  die muss **hochgezogen** werden (macht stock.py), dann Bild antippen → Galerie.
- **Kopplung mit dem Editing System** steht (Brücke dort `eigene/TIKTOK-STEUERUNG.md`). Offen: In dessen Skills
  (/bof, /mof, /hof, /remake, /fertig) einen Verweis auf die Brücke eintragen – blockierte der Sicherheitsfilter, Artur muss das
  erlauben oder selbst eintragen. `eingang.py posten` (Drag aufs iPhone + posten) noch nicht live gelaufen.
- **Sync:** Repo `andreaskmh/tiktok-steuerung`. Auf dem 2. MacBook: klonen nach ~/Documents/Coding/TikTok-Steuerung,
  `zsh werkzeuge/sync.sh einrichten`, dann vmaus einrichten (vmaus/ANLEITUNG.md, Artur bestätigt den Treiber).

- **Geplant (Artur, 09.11.):** Slideshows (andreasfastlane) ebenfalls automatisch posten – Artur meldet sich dazu.

## Schnellster Ablauf (seit 08.11. nachts)
- Tippen: `python3 werkzeuge/tap.py x y [wSek] …` (virtuelle Maus, sitzt beim 1. Mal). Text: `post.tippe()` (menschlich, Buchstabe für Buchstabe, KEINE Emojis möglich).
- `werkzeuge/post.py a|b|c` und `upload.py publish|like` – Abschnitte am Stück, dazwischen nur kurz Foto.
- Produkt: Safari am iPhone → `social1.ai/products/<ID>` → View on TikTok Shop → Provisionsfeld → Zum Showcase.
  Kein Provisionsfeld oder Produkt nicht oben in der Showcase-Liste → **Einkaufswagen** (beliebige Farbe/Größe),
  beim Verlinken „Weitere Produkte hinzufügen → Einkaufswagen“. Nie scrollen/suchen.
- Produkt-IDs: Safari am Mac, `do JavaScript` (Apple-Events-JS ist an).
- Nach „+“: „Kamera nicht verfügbar“ → OK. Keine Pausen zwischen Uploads. Profil nicht neu laden. Like/Speichern nicht nachprüfen.
- Kein Preis in Beschreibung. Vor „Weiter“ Vorschaubild prüfen (Galerie verschiebt sich) – Artur erlaubt: Video nach Upload aus Galerie löschen.
- Auf artur.official liegt „Link hinzufügen“ bei y≈388 (eine Zeile weniger als bei ella/anduri, dort 428).

## Stolpersteine
- iPhone-Zeiger friert ein, wenn Arturs Maus sich bewegt oder das runde Claude-Symbol über dem iPhone-Fenster liegt → Artur fährt kurz mit dem Trackpad drüber. iPhone-Fenster liegt jetzt bei x=700.
- Arturs Tastatur landet im iPhone, solange das Fenster vorne ist.
- Kontext wird schnell riesig → neue Session pro Stapel.

## 10.11.2026 23:00 – Stapel 2026-11-10-bof139 (Video 139, 28 BoF) – von Artur gestoppt
- Gepostet (anduri.official): 01 Roll-on Parfümset, 03 VEVOR Rollbock, 05 SPZK, 07 Crocs (Brand von Artur gewählt).
- 09 Dr.Melaxin: im Einkaufswagen, Beitragsseite offen, beim Button-Text gestoppt → Status „fehler“; Rest „freigegeben“ (alle mit #superdeals).
- Weiter mit `python3 werkzeuge/post_wagen.py 2026-11-10-bof139` (Showcase zuerst, Wagen nur wenn schon im Showcase). Texte per ⌘V (dauert bis ~15 s), iPhone-Fenster bei x=700.

## 10.11.2026 23:33 – Stapel 2026-11-10-bof139 von Artur gestoppt
- Gepostet: anduri.official 01, 03, 05, 07, 09, 11, 13, 15, 17 (9). Offen (freigegeben): 02–28 gerade + 19–28 → ella (02–18 gerade), andreas.testet (19–21), artur.official (22–28).
- Weiter: `python3 werkzeuge/post_wagen.py 2026-11-10-bof139` (iPhone-Fenster x=700). Ohne Brand gepostet: siehe uebergabe/ausgang/ohne-brand.txt.

## 11.11.2026
- Stapel 2026-11-10-bof139: Rest (19) hat Artur selbst hochgeladen, Posten beendet. Pflicht-Hashtags: #superdeals #TikTokShopBlackFriday #LIVEDeals.

## 12.11.2026 – Umstellung auf Kabel
- iPhone 11 per USB über open-iphone-use (docs/KABEL.md). Stock per Kabel getestet (Hosenrock 2/2, 41 s, verlustfrei).
- Video aufs iPhone per AirDrop (`werkzeuge/airdrop.py`, 11 s, getestet). `eingang.py` nutzt es automatisch.
- posten.py / post_wagen.py laufen übers Kabel; ganzer Post als Entwurf getestet (anduri, BotaBay, 12.11. 01:12).
  Echtes Veröffentlichen per Kabel noch nicht → 1. Post im nächsten Stapel mitschauen, bei STOPP Foto (`python3 werkzeuge/kabel.py foto`).
- Probe-Entwurf „9 DÜFTE UNTER 20€“ liegt in den Entwürfen von anduri.official (kann weg). Video liegt 2× in Fotos am iPhone.
