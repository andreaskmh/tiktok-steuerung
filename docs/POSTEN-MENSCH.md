# Posten wie Artur – `werkzeuge/post_mensch.py` (seit 12.11.2026 abends)

Folgt Arturs eigenem Ablauf aus seinen Bildschirmaufnahmen (Editing System `eigene/POSTEN-ABLAUF.md`).
Ersetzt `post_wagen.py`/`posten.py` beim Posten (`eingang.py posten` ruft es auf; alter Weg nur mit `TS_ALT=1`).

```bash
python3 werkzeuge/post_mensch.py --stapel <stapel>                 # alle „freigegeben“, Account für Account, AirDrop vorher
python3 werkzeuge/post_mensch.py <eingang.json>                    # ein Video
python3 werkzeuge/post_mensch.py <json> --entwurf --ohne-airdrop   # Test: bis „Entwürfe“, nichts veröffentlichen
python3 werkzeuge/post_mensch.py --aufraeumen <json>               # nur Social1-Lesezeichen + Fotos
```
Ausgabe: eine Zeile pro Schritt mit Sekunden seit Start, je Video `✓ … 84 s`, am Ende `FERTIG x/y, Ø … s`. `STOPP …` → Foto
(`python3 werkzeuge/kabel.py foto`), Ursache beheben, denselben Befehl neu starten (Gepostete überspringt der Stapel über den Status).

## Ablauf pro Video
1. **Account** (nur beim 1. Video und bei Wechsel): TikTok → Profil (300/681) → `@account`? sonst Name oben links → „Konto wechseln“ →
   Account erst antippen, wenn die Liste ruht (nie „Konto hinzufügen“).
2. **Produkt:** Home → Suche „Safari“ → ⌘L → `social1.ai/products/<id>` → warten bis Produktname da → „View on TikTok Shop“ →
   Banner „ÖFFNEN“ / Dialog „Öffnen“ / „TikTok öffnen“ antippen, bis die Produktseite (Einkaufswagen + Kasse) mit dem Shop da ist.
3. **Showcase:** „Verdiene … pro Verkauf“ → „Zum Showcase hinzufügen“. Steht dort „Mehr erkunden“ (schon drin) oder fehlt der Streifen →
   **Einkaufswagen** (grau, links; Lage gegen „Kasse“ geprüft) → erste verfügbare Variante → rotes „Einkaufswagen“ → „hinzugefügt“.
4. Blatt runterwischen, Produktseite X → „+“ (erkannt an türkis/pink Rand, Pixel) → Galerie unten links → Kachel mit Hook-Titel
   (Kabel-OCR) → Vorschau → „Auswählen“ → „Weiter“ → Editor „Weiter“ → **Vorschaubild muss den Hook-Titel zeigen** (sonst STOPP).
5. „Beschreibung hinzufügen“ → menschlich tippen (Häppchen 2–5 Zeichen). Text: `beschreibung` aus der JSON, sonst
   1 Produkt-Hashtag (erster eigener aus `hashtags`) + `#tiktokshopblackfriday #superdeals #livedeals` (bis 30.11.2026) in
   wechselnder Reihenfolge, optional `kurz` (1–2 Wörter) davor.
6. „Link hinzufügen“ → „Produkt“ → warten bis „Dein Showcase“ geladen → Showcase: oberstes Produkt prüfen (Name) → „Hinzufügen“;
   Wagen: „Weitere Produkte hinzufügen“ → „Einkaufswagen“ → oberstes → „Hinzufügen“. Dialog „zum Video hinzufügen?“ → Hinzufügen.
   „Produkt umbenennen“: **nicht umbenennen**, warten bis „Hinzufügen“ kräftig rot ist (blass = lädt), dann tippen. „zustimmen“ → tippen.
   Pilot-Hinweis „noch x von 3“ wird geloggt.
7. **@Brand** nur mit `handle` und wenn genau dieser Nutzername in der Trefferliste steht; sonst zurück, ohne Brand.
   Brands ohne Konto merkt sich `uebergabe/ausgang/brand-konten.json` (dann keine Suche mehr, spart ~10 s).
8. **Veröffentlichen** erst, wenn der Knopf kräftig rot ist (Pixel). `--entwurf` / `ausverkauft` → „Entwürfe“ (links geprüft).
9. **Aufräumen:** Social1 am **Mac** (Safari, Liste offen in einem Tab `social1.ai/saved-videos/<liste>`): Karte mit der Produkt-ID →
   Lesezeichen „Save to list“ → Haken der offenen Liste raus → „Done“ (per JavaScript, nie „Delete“). Spart den App-Wechsel am iPhone.
   Fotos: Video löschen – **noch nicht freigeschaltet** (`FOTOS_GETESTET`), Lagen werden im Test gemessen.

## Gefahren-Sperre (jeder Tipp)
- Kein Tipp, wenn im Umkreis von ~38 Pkt ein Label steht: Kasse, Jetzt kaufen, LIVE (auch OCR „ÇIVE“/„LIV“), LIVE gehen/Event,
  Konto hinzufügen, Delete, Registrieren, Abmelden, Event erstellen.
- **Nie oben links tippen, wenn der Feed oben steht** („Für dich/Gefolgt/In der Nähe/Entdecken“): dort liegt das LIVE-Symbol.
  (Ursache der LIVE-Event-Seite am 12.11.: blinder Zurück-Tipp 23/57 im Feed.)
- CAPTCHA-/Prüfungs-Wörter irgendwo am Bildschirm → sofort STOPP (Artur löst).
- Tipp-Punkte ±3 Pkt zufällig, Pausen ±25 %, Tippen in Häppchen → kein gleiches Muster.
- Doppel-Schutz (`gepostet.sh`), Tageslimit andreas.testet 3 (Zähler `posts-<tag>.json`), Status in der Eingang-JSON.

## Messwerte (12.11.2026, anduri.official, Testvideo „Beheizte Decke“, als Entwurf)
| Schritt | Showcase-Weg (Einzelschritte) | Wagen-Weg (am Stück) |
|---|---|---|
| Account prüfen | 10 s | 10 s |
| Social1 → Produktseite | 24 s | 20 s |
| Showcase / Wagen | 4 s | 20 s |
| „+“ → Beitragsseite | 19 s | 21 s |
| Beschreibung tippen | 13 s | 13 s |
| Link | 8 s | 17 s |
| Brand (nicht gefunden) | 10 s | 10 s |
| Entwürfe | 3 s | 5 s |
| **Summe** | **~91 s** | **116 s** |
Im Stapel fallen Account-Prüfung (außer beim 1. Video eines Accounts) und bekannte Brands ohne Konto weg → Showcase-Weg ~70 s,
Wagen-Weg ~95 s.

## Bekannte Stolpersteine
- Steuerverbindung reißt manchmal ab („Connection was terminated abruptly“, Bild läuft weiter) → `open-iphone-use stop`,
  `python3 werkzeuge/kabel/waechter.py einmal`.
- Teilen-Blatt in Fotos („3 Videos ausgewählt“) nimmt keine Kabel-Tipps an → Artur schließt es von Hand.
- TikTok-Leiste unten hat keine Texte → Hauptseite über die Farben des „+“ (`bin/pixel`, Swift, `zsh werkzeuge/build.sh`).
