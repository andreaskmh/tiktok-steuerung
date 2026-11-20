#!/bin/zsh
# Artur 20.11.2026: Ranglisten-Seite im WLAN dauerhaft starten (auch nach Neustart). launchd darf ~/Documents nicht lesen
# → Server + Seite nach ~/.tiktok-research kopieren. Nach Änderungen an Seite/Server einfach erneut ausführen.
H=~/.tiktok-research; P=${0:A:h}; L=~/Library/LaunchAgents/de.tiktoksteuerung.ranglisten-seite.plist
mkdir -p $H/seite
cp $P/ranglisten_server.py $H/
cp $P/../uebergabe/ranglisten-seite/index.html $P/../uebergabe/ranglisten-seite/daten-*.json $H/seite/
cat > $L <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>de.tiktoksteuerung.ranglisten-seite</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$H/ranglisten_server.py</string></array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
  <key>StandardErrorPath</key><string>$H/ranglisten-seite.log</string>
</dict></plist>
PL
launchctl unload $L 2>/dev/null
launchctl load $L && echo "Ranglisten-Seite läuft: http://$(scutil --get LocalHostName).local:8080"
