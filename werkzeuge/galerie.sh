#!/bin/zsh
# galerie.sh <ordnername> [produktname] [social1_link] [tts_link]
# Voraussetzung: Produkt ist in der TikTok-App in der Vollbild-Galerie offen (Zähler oben rechts sichtbar),
# virtuelle Maus oder Mini-Gerät läuft (geraet/geraet.py STATUS).
# Holt alle Bilder: erst zurück auf 1, dann vorwärts, nach jedem Schritt Zähler prüfen.
# Ergebnis: uebergabe/ausgang/<ordnername>/bild-01.png … + produkt.json
set -e
HIER=${0:A:h}; W=$HIER/..; B=$HIER/bin
NAME=${1:?Aufruf: galerie.sh <ordnername> [produktname] [social1_link] [tts_link]}
OUT=$W/uebergabe/ausgang/$NAME; mkdir -p $OUT; TMP=$(mktemp -d)/z.png  # screencapture darf nicht direkt nach ~/Documents
zsh $HIER/build.sh >/dev/null
open -b com.apple.ScreenContinuity; sleep 0.5
zaehler() { zsh $HIER/aufnahme.sh $TMP >/dev/null; $B/zaehler $TMP; }
schritt() { $B/zeiger rel 0.5 0.45 >/dev/null; python3 $W/geraet/geraet.py "SHIFTSCROLL $1 10" >/dev/null; sleep 1.1; }

Z=($(zaehler)) || { echo "Kein Galerie-Zähler zu sehen – ist die Vollbild-Galerie offen?"; exit 1; }
N=${Z[2]}; echo "Galerie: ${Z[1]}/$N"
# zurück auf Bild 1
v=0; while (( Z[1] > 1 )); do schritt -7; Z=($(zaehler)); (( ++v > N + 3 )) && { echo "Zurück klappt nicht (Maus wach? siehe docs/ABLAUF.md)"; exit 1; }; done
bilder=()
for i in $(seq 1 $N); do
  Z=($(zaehler)); [[ ${Z[1]} == $i ]] || { echo "Erwartet Bild $i, Zähler zeigt ${Z[1]} – Abbruch"; exit 1; }
  f=$(printf "bild-%02d.png" $i); mv $TMP $OUT/$f; bilder+=$f; echo "✓ $f"
  (( i < N )) && schritt 7
done
rm -f $TMP
python3 - "$OUT" "$N" "${2:-$NAME}" "${3:-}" "${4:-}" "${bilder[@]}" <<'PY'
import json, sys, datetime
out, n, produkt, s1, tts, *bilder = sys.argv[1:]
json.dump({"version": 1, "produkt": produkt, "social1_link": s1, "tts_link": tts,
           "geholt_am": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "bilder": bilder, "anzahl_laut_galerie": int(n)},
          open(f"{out}/produkt.json", "w"), ensure_ascii=False, indent=2)
PY
echo "Fertig: $N Bilder in $OUT"
