#!/bin/zsh
# wischtest.sh – erster Test mit angestecktem Mini-Gerät.
# Vorher: iPhone-Synchronisierung offen, TikTok-Produkt in der Vollbild-Galerie (Zähler z. B. 1/12).
# Probiert nacheinander drei Wisch-Arten und macht nach jeder ein Fensterfoto.
set -e
HIER=${0:A:h}; W=$HIER/../werkzeuge
OUT=${1:-$HIER/../uebergabe/ausgang/wischtest-$(date +%H%M%S)}
mkdir -p $OUT
zsh $W/build.sh >/dev/null
python3 $HIER/geraet.py ping
zsh $W/aufnahme.sh $OUT/0-start.png
i=1
for b in "SHIFTSCROLL -3" "SCROLL -1 0 6" "DRAG -250 0 25"; do
  $W/bin/zeiger rel 0.5 0.45 >/dev/null
  python3 $HIER/geraet.py "$b"
  sleep 1.2
  zsh $W/aufnahme.sh $OUT/$i-${b// /_}.png
  i=$((i+1))
done
echo "Fotos in $OUT – Zähler in der Galerie vergleichen."
