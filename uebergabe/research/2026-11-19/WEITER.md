# Research 19.11.2026 – Stand (Pause wegen Claude-Neustart)
Fertig: DE gelesen (600), gefiltert (408 Kandidaten), sortiert (de-sortiert.json: 124 BOF, 33 SLIDES), Rangliste de-rangliste.md.
Fertig auch: Social1-Listen BOF DE 19.11.2026 (121) + SLIDES DE 19.11.2026 (31). Offen: USA (Produktcheck DE, Amazon.es), Zeiten messen.

Weiter (aus Projektordner, im Hintergrund):
  O=uebergabe/research/2026-11-19
  B=$(python3 -c "import json;d=json.load(open('$O/de-sortiert.json'));print(' '.join(sorted([n for n,a in d.items() if a=='BOF'],key=int)))")
  S=$(python3 -c "import json;d=json.load(open('$O/de-sortiert.json'));print(' '.join(sorted([n for n,a in d.items() if a=='SLIDES'],key=int)))")
  python3 werkzeuge/research.py speichern de "BOF DE 19.11.2026" "$B"; python3 werkzeuge/research.py speichern de "SLIDES DE 19.11.2026" "$S"
Doku: docs/RESEARCH.md

## 19.11. Vormittag (geplanter Lauf 7 Uhr, Claude)
- DE `lesen --frisch` gestartet 08:45 (alter Stand → de-0845.json), hing nach Seite 1 → zweimal neu gestartet, ohne Fortschritt, um 12:34 abgebrochen.
- Ursache: Mac stark überlastet (Load 45–52; coreduetd, modelcatalogd, linkd, Apple-Intelligence-Dienste), Safari-AppleScript antwortete erst nach Minuten.
- Weiter: Mac neu starten, dann `python3 werkzeuge/research.py lesen de` (ohne --frisch, setzt bei Seite 2 fort), danach Tageslauf DE ab filtern, dann USA ab `blaetter us --neu`.
- Außerdem: stündliche Messung (launchd) scheitert: „research.py: Operation not permitted“ → Python braucht Festplattenvollzugriff (macht Artur).
