#!/bin/zsh
# Sync zwischen Arturs MacBooks über das private GitHub-Repo andreaskmh/tiktok-steuerung (seit 09.11.2026).
#   zsh werkzeuge/sync.sh holen       -> neuesten Stand holen (bei Chat-Start, vor jedem Stapel)
#   zsh werkzeuge/sync.sh sichern ["Text"] -> eigene Änderungen hochladen (nach jedem Stapel / jeder Regel)
#   zsh werkzeuge/sync.sh einrichten  -> einmal pro Mac: Gedächtnis-Verknüpfung + Werkzeuge bauen
# Ausgabe: OK / NICHTS_NEU / KONFLIKT <dateien> / OFFLINE
ROOT="${0:A:h:h}"; cd "$ROOT" || exit 1
case "$1" in
holen)
  git fetch -q origin 2>/dev/null || { echo OFFLINE; exit 0; }
  if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A && git commit -q -m "Zwischenstand $(scutil --get ComputerName 2>/dev/null) $(date '+%d.%m.%Y %H:%M')"
  fi
  [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && { echo NICHTS_NEU; exit 0; }
  if git rebase -q origin/main 2>/dev/null; then zsh werkzeuge/build.sh >/dev/null; echo OK; else
    echo "KONFLIKT $(git diff --name-only --diff-filter=U | tr '\n' ' ')"; fi ;;
sichern)
  git add -A
  git diff --cached --quiet || git commit -q -m "${2:-Sync} – $(scutil --get ComputerName 2>/dev/null) $(date '+%d.%m.%Y %H:%M')"
  git fetch -q origin 2>/dev/null || { echo OFFLINE; exit 0; }
  git rebase -q origin/main 2>/dev/null || { echo "KONFLIKT $(git diff --name-only --diff-filter=U | tr '\n' ' ')"; exit 0; }
  git push -q origin main 2>&1 && echo OK ;;
einrichten)
  KEY="$(echo "$ROOT" | sed 's#[/. ]#-#g')"; MEM="$HOME/.claude/projects/$KEY/memory"
  mkdir -p "${MEM:h}" gedaechtnis
  if [ -L "$MEM" ]; then :; elif [ -d "$MEM" ]; then
    cp -n "$MEM"/*.md gedaechtnis/ 2>/dev/null; mv "$MEM" "$MEM.vor-sync-backup"; fi
  [ -e "$MEM" ] || ln -s "$ROOT/gedaechtnis" "$MEM"
  echo "Gedächtnis -> $MEM"
  zsh werkzeuge/build.sh
  echo "Noch von Hand (einmal pro Mac, macht Artur): virtuelle Maus einrichten (vmaus/ANLEITUNG.md), Freigaben für"
  echo "Bildschirmaufnahme + Bedienungshilfen, iPhone-Synchronisierung mit dem iPhone verbinden." ;;
*) echo "Aufruf: zsh werkzeuge/sync.sh holen|sichern|einrichten"; exit 1 ;;
esac
