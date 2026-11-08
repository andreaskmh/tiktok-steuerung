#!/bin/zsh
# aufnahme.sh <ziel.png> [bundle-id]
# Nimmt nur das Fenster der iPhone-Synchronisierung auf (ohne Schatten, ohne Ton).
set -e
HIER=${0:A:h}
ZIEL=${1:?Aufruf: aufnahme.sh <ziel.png>}
[[ -x $HIER/bin/fenster ]] || zsh $HIER/build.sh >/dev/null
INFO=$($HIER/bin/fenster ${2:-com.apple.ScreenContinuity}) || { echo "iPhone-Synchronisierung ist nicht offen"; exit 1; }
ID=${INFO%% *}
mkdir -p ${ZIEL:h}
screencapture -x -o -l $ID $ZIEL
echo "$ZIEL ($(sips -g pixelWidth -g pixelHeight $ZIEL | awk '/pixel/{printf "%s ", $2}')px)"
