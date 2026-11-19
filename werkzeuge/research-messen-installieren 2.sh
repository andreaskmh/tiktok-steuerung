#!/bin/zsh
# Kopiert research.py + Regeln nach ~/.tiktok-research (launchd darf ~/Documents nicht lesen) und lädt die stündliche Messung neu.
H=~/.tiktok-research; P=${0:A:h}
mkdir -p $H/werkzeuge
cp $P/research.py $P/research_regeln.json $H/werkzeuge/
sed "s#/Users/andreask/Documents/Coding/TikTok-Steuerung/werkzeuge/research.py#$H/werkzeuge/research.py#; s#/Users/andreask/Documents/Coding/TikTok-Steuerung/uebergabe/research/messen.log#$H/messen.log#g" \
  $P/research-messen.plist > ~/Library/LaunchAgents/de.tiktoksteuerung.research-messen.plist
launchctl unload ~/Library/LaunchAgents/de.tiktoksteuerung.research-messen.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/de.tiktoksteuerung.research-messen.plist && echo "Messung installiert ($H)"
