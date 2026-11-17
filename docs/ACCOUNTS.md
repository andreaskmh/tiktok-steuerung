# Accounts und Verteilung (Stand 08.11.2026, von Artur)

| Account | Was | Anteil / Limit |
|---|---|---|
| `anduri.official` | Videos, **höchste Priorität**, Qualitätsvideos (MoF, HoF, Remakes) | zusammen mit ella ≈ 60 % |
| `ella_robinson2` | Videos, **höchste Priorität**, Qualitätsvideos (MoF, HoF, Remakes) | zusammen mit anduri ≈ 60 % |
| `andreas.testet` | Videos, eher BoF/Trend | **max. 3 Videos pro Tag** (Pilotprogramm) |
| `artur.official` | Videos, eher BoF/Trend | Rest – **möglichst wenig** (Artur 08.11.: anduri + ella haben Vorrang) |
| `andreasfastlane` | **nur Slideshows** | – |

Beispiel 20 Videos: 12 auf anduri + ella (je 6), 4 auf andreas.testet (Limit 3 beachten!), 4 auf artur.official.

## Regeln

- **Gleiche Idee + gleiches Produkt** in mehreren Videos → auf **verschiedene Accounts** verteilen (jeden Account testen).
- **Abstand:** keiner (Artur 09.11.2026).
- **Ein Account nach dem anderen:** erst alle Videos eines Accounts fertig, dann zum nächsten wechseln.
- Pro Video: Produktlink (Showcase) hinzufügen, Beschreibung mit Hashtags, **Brand markieren**.
- Vor dem Posten: Stapel-Plan (Video → Account, Text, Hashtags, Produkt, Brand, Reihenfolge) Artur zeigen, posten erst nach seinem OK.
- Tageszähler je Account führen (`uebergabe/ausgang/posts-JJJJ-MM-TT.json`), damit das Pilot-Limit nicht überschritten wird.

## Produktlink (Artur, 08.11.2026)

- Immer den **TikTok-Shop-Produktlink aus Social1** nehmen (`shop.tiktok.com/view/product/<id>`).
- Produkt ins **Showcase** des Accounts legen, falls noch nicht drin. Geht das nicht → in den **Einkaufswagen** legen
  (nur hinzufügen, nie kaufen/Kasse).
- Beim Video dann den Produktlink aus Showcase bzw. Einkaufswagen auswählen.
- **Jeder Account hat eigenen Showcase und eigenen Einkaufswagen** → nach jedem Account-Wechsel erneut prüfen/hinzufügen.
- Button-Text (Feld „Produktname“ beim Verlinken): **≤ 20 Zeichen, keine Emojis**, durchmischen:
  „Wenige verfügbar“, „Fast ausverkauft“, „Fast vergriffen“, „Wenige auf Lager“, „Geringer Bestand“. (Nicht „Bald vergriffen“ – Artur 15.11.2026.)
  Artur prüft den Bestand jedes Produkts vorher (Aussage 08.11.2026). Konkrete Zahlen („Noch 12 Stück“) nur, wenn
  Artur die Zahl fürs Produkt nennt. Nicht nachfragen, einfach durchmischen.

- **Hashtags bei jedem Video immer: #superdeals #TikTokShopBlackFriday #LIVEDeals** (Artur, 11.11.2026).

## Freigabe (Artur, 11.11.2026)
- Abnahme der Videos („passt“, /fertig, auch per Sprache) = Freigabe zum Posten. Kein extra Posting-Plan, keine zweite Rückfrage. Ohne Signal im Chat wird nie gepostet.

- **Tageslimit TikTok: max. 25 Videos pro Account und Tag** (Artur 17.11.2026; andreas.testet weiter 3). Bis zum Maximum verteilen (Zähler `posts-JJJJ-MM-TT.json`), Rest nicht posten, sondern für den nächsten Tag vormerken (`REST-POSTEN.md` im Videoordner).

**17.11.2026 19:35 – Tageslimit zeigt sich als Hänger beim Verlinken (Artur, Video 148-51):** Bei anduri.official (23 Posts + 1 Entwurf heute) blieb das 25. Video auf „Produkt umbenennen“ hängen („nach dem Verlinken nicht zurück auf der Beitragsseite“). Laut Artur heißt das: Tageslimit von 25 erreicht, Entwürfe zählen offenbar mit bzw. der eigene Zähler weicht ab. Dann nicht nochmal versuchen, Beitrag verwerfen, der Account ist für heute fertig, das Video auf einen anderen Account umhängen oder in REST-POSTEN für morgen. Seit 17.11. sichert post_mensch bei diesem Hänger ein Foto (`uebergabe/ausgang/verlinken-haenger-*.png`).

**17.11.2026 19:40 – Limit-Hinweis lesen statt auf Hänger warten (Artur: „achte lieber auf den Hinweis“):** Den genauen Wortlaut bei 148-51 (anduri) haben wir nicht festgehalten: kein Foto, und der Bildschirmtext wurde nicht geloggt. Neu in post_mensch: Beim Verlinken wird jede Runde zuerst der Bildschirmtext auf einen Limit-Hinweis geprüft (`limit_hinweis`: „Limit“/„Tageslimit“/„Limit erreicht“, „maximale Anzahl“, „heute keine/nicht mehr“, „morgen erneut/wieder“, „daily limit“, „noch 0 von“; „limitiert“/„Limited“ zählen nicht). Treffer → Foto `limit-*.png`, Bildschirmtext ins Log, `✗ … LIMIT <account>`, Beitrag verwerfen, alle weiteren Videos dieses Accounts heute überspringen (Status fehler „LIMIT“), weiter mit dem nächsten Account. Hänger beim Verlinken loggen jetzt den ganzen Bildschirmtext + Foto. Sobald der echte Wortlaut bekannt ist: hier eintragen und `LIMIT_RE` schärfen. Nebenwirkung bei 51: Beim Verwerfen landete TikTok im Editor (Sound „Vivaldi“ angehängt), beim Zurück speicherte TikTok automatisch einen **Entwurf von 51 auf anduri** (nicht veröffentlicht, Artur löscht ihn).
