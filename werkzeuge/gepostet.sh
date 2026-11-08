#!/bin/zsh
# Doppel-Schutz: merkt sich jedes gepostete Video (Prüfsumme + Name + Account).
#   zsh werkzeuge/gepostet.sh pruefen   "<video>"            -> "NEU" (Exit 0) oder "SCHON GEPOSTET: ..." (Exit 1)
#   zsh werkzeuge/gepostet.sh eintragen "<video>" <account>   -> nach dem Veröffentlichen
# Erkennt dasselbe Video auch unter anderem Dateinamen (Prüfsumme).
liste="${0:A:h:h}/uebergabe/ausgang/gepostet.txt"
touch "$liste"
befehl=$1; datei=$2; account=$3
[[ -f "$datei" ]] || { echo "Datei fehlt: $datei"; exit 2; }
summe=$(shasum -a 1 "$datei" | cut -d' ' -f1)
name=${datei:t}
treffer=$(grep -F -e "$summe" -e "|$name|" "$liste")
case $befehl in
  pruefen)
    if [[ -n "$treffer" ]]; then echo "SCHON GEPOSTET: $treffer"; exit 1; fi
    echo "NEU"; exit 0 ;;
  eintragen)
    if [[ -n "$treffer" ]]; then echo "War schon eingetragen: $treffer"; exit 1; fi
    echo "$summe|$name|${account:-?}|$(date '+%Y-%m-%d %H:%M')" >> "$liste"
    echo "Eingetragen." ;;
  *) echo "Nutzung: pruefen <video> | eintragen <video> <account>"; exit 2 ;;
esac
