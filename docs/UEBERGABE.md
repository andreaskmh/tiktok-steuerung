# Übergabe-Ordner

`uebergabe/` ist die **einzige Schnittstelle** zu anderen Projekten (z. B. dem Editing-System).
Andere Projekte legen nur Dateien hier ab bzw. holen sie ab – kein Projekt ändert Dateien des anderen.

```
uebergabe/
  eingang/   ← kommt rein: fertige Videos zum Posten (Video + JSON)
  ausgang/   ← geht raus: Stock-Bilder pro Produkt (Ordner + produkt.json)
  beispiel/  ← Muster-Dateien
```

## eingang/: ein Video = eine JSON

Video und JSON liegen nebeneinander, gleicher Name: `bof-138-03.mp4` + `bof-138-03.json`.

```json
{
  "version": 1,
  "datei": "bof-138-03.mp4",
  "account": "andreasfastlane",
  "social1_link": "https://social1.ai/saved-videos/…",
  "tts_link": "https://www.tiktok.com/view/product/…",
  "produkt": "Reisenthel Carrybag Leo",
  "titel": "Die Tasche, die jeder im Supermarkt anspricht 😍",
  "hashtags": ["#tiktokmademebuyit", "#carrybag", "#reisenthel"],
  "stapel": "2026-11-09-a",
  "status": "bereit",
  "notiz": "",
  "verlauf": []
}
```

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `version` | ja | Format-Version, aktuell `1` |
| `datei` | ja | Dateiname des Videos im selben Ordner |
| `account` | ja | TikTok-Account, auf dem gepostet wird (einer von Arturs 4) |
| `social1_link` | ja* | Link aus Social1 zum Produkt/Video |
| `tts_link` | ja* | TikTok-Shop-Produktlink (fürs Showcase) |
| `produkt` | ja | Produktname, wie er im Showcase heißt |
| `titel` | ja | Beschreibung/Caption des Posts |
| `hashtags` | nein | Liste, jeweils mit `#` |
| `stapel` | ja | Name des Stapels; Artur gibt immer einen ganzen Stapel frei |
| `status` | ja | siehe unten |
| `notiz` | nein | freier Text (z. B. „erst nach 18 Uhr“) |
| `verlauf` | nein | wird von diesem Projekt geschrieben: `[{"zeit": "…", "status": "…", "info": "…"}]` |

\* mindestens einer der beiden Links.

Zusatzfelder fürs automatische Posten (`einreichen.py` setzt sie, `eingang.py posten` braucht sie):

| Feld | Bedeutung |
|---|---|
| `kachel` | Text groß auf dem Video (Hook-Label), daran wird es in der iPhone-Galerie und im Profil gefunden |
| `button` | Button-Text beim Produktlink (≤ 20 Zeichen, keine Emojis) |
| `brand` | Shop-Name für „@ Erwähnung“ |
| `handle` | genauer Nutzername des Shops (optional, wenn der Shop-Name in der Trefferliste eindeutig ist) |
| `ausverkauft` | `true` → als Entwurf ohne Link speichern |
| `quelle` | Pfad der Export-Datei im Editing System |

Ablauf: Editing System `einreichen.py` → Status `bereit` → Artur sagt „geprüft, zufrieden“ → `eingang.py freigeben <stapel>`
→ `eingang.py posten <stapel>` → `gepostet` / `entwurf` (ausverkauft) / `fehler`.

### Status

| Status | Wer setzt ihn | Bedeutung |
|---|---|---|
| `entwurf` | Ersteller | noch nicht fertig, wird ignoriert |
| `bereit` | Ersteller | fertig, wartet auf Arturs Freigabe |
| `freigegeben` | nur nach Arturs OK im Chat | darf gepostet werden |
| `gepostet` | dieses Projekt | erledigt; zusätzlich `post_link` und `gepostet_um` |
| `fehler` | dieses Projekt | hat nicht geklappt, Grund im `verlauf` |

Zwischen zwei Posts gibt es **keinen Abstand** (Artur 09.11.2026).

## ausgang/: Stock-Bilder pro Produkt

```
ausgang/
  reisenthel-carrybag-leo/
    produkt.json
    bild-01.png
    bild-02.png
    …
```

```json
{
  "version": 1,
  "produkt": "Reisenthel Carrybag Leo",
  "social1_link": "https://social1.ai/saved-videos/…",
  "tts_link": "https://www.tiktok.com/view/product/…",
  "geholt_am": "2026-11-09T14:20:00+01:00",
  "bilder": ["bild-01.png", "bild-02.png"],
  "anzahl_laut_galerie": 12
}
```

Prüfen: `python3 werkzeuge/pruefe_uebergabe.py` (prüft alle JSONs in `eingang/` und `ausgang/`).
