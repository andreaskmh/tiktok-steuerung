# Research 19.11.2026 – Stand (Pause wegen Claude-Neustart)
Fertig: DE gelesen (600), gefiltert (408 Kandidaten), sortiert (de-sortiert.json: 124 BOF, 33 SLIDES), Rangliste de-rangliste.md.
Fertig auch: Social1-Listen BOF DE 19.11.2026 (121) + SLIDES DE 19.11.2026 (31). Offen: USA (Produktcheck DE, Amazon.es), Zeiten messen.

Weiter (aus Projektordner, im Hintergrund):
  O=uebergabe/research/2026-11-19
  B=$(python3 -c "import json;d=json.load(open('$O/de-sortiert.json'));print(' '.join(sorted([n for n,a in d.items() if a=='BOF'],key=int)))")
  S=$(python3 -c "import json;d=json.load(open('$O/de-sortiert.json'));print(' '.join(sorted([n for n,a in d.items() if a=='SLIDES'],key=int)))")
  python3 werkzeuge/research.py speichern de "BOF DE 19.11.2026" "$B"; python3 werkzeuge/research.py speichern de "SLIDES DE 19.11.2026" "$S"
Doku: docs/RESEARCH.md
