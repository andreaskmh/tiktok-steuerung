# Stand & nächste Schritte (zuletzt 09.11.2026, 00:40)

**Zuerst lesen:** `CLAUDE.md` → `docs/ABLAUF.md` → `docs/ACCOUNTS.md`. Memory: upload-speed-regeln, produkt-immer-ueber-social1.

## Offen
- Stapel 08.11. komplett (12/12). artur.official 09.11.: Tunnelblick 00:29, Rock Shorts 00:35.
- Rock Shorts: orangener Shop-Button direkt nach Post noch nicht sichtbar (Link war gesetzt) → Artur kurz prüfen.
- **Neu: `werkzeuge/posten.py <stapel.json>`** postet einen ganzen Stapel am Stück (Texterkennung statt Fotos).
  Noch nicht live gelaufen → beim ersten Video mitschauen; bei STOPP Foto machen und von Hand weiter.
  Vorlage: `uebergabe/beispiel/stapel-posten.json`.
- **`werkzeuge/stock.py`** (Stock automatisch über Social1): kommt bis zur TikTok-Produktkarte. Offen: Die Seite öffnet
  sich als Vorschaukarte, ein Tipp aufs Bild öffnet keine Galerie, „^“ öffnet die Provisions-Info. Den richtigen Weg zur
  Vollbild-Galerie einmal mit Artur klären, dann in `zur_galerie()` einbauen.
- Kopplung mit dem Editing System + Sync aufs 2. MacBook: wartet auf Arturs Antwort (Nicolas abgeklärt? GitHub-Repo).
- Kein Abstand zwischen Posts (Artur 09.11.).

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
