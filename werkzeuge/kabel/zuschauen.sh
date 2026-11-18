#!/bin/zsh
# zuschauen.sh an|aus|status – Zuschau-Link fürs iPhone im WLAN (nur Livebild, keine Steuerung), Autostart beim Anmelden.
set -e
HIER=${0:A:h}
NAME=de.tiktok-steuerung.iphone-zuschauen
PLIST=~/Library/LaunchAgents/$NAME.plist
ZIEL=~/.local/share/ts-iphone-zuschauen
case ${1:-status} in
an)
  mkdir -p ~/Library/LaunchAgents $ZIEL
  cp $HIER/zuschauen.py $ZIEL/zuschauen.py
  cat > $PLIST <<P
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$NAME</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$ZIEL/zuschauen.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/ts-iphone-zuschauen.err</string>
</dict></plist>
P
  launchctl bootout gui/$(id -u)/$NAME 2>/dev/null || true
  launchctl bootstrap gui/$(id -u) $PLIST
  echo "Zuschauen an: http://$(scutil --get LocalHostName).local:27894  /  http://$(ipconfig getifaddr en0):27894" ;;
aus)
  launchctl bootout gui/$(id -u)/$NAME 2>/dev/null || true
  rm -f $PLIST; echo "Zuschauen aus" ;;
*)
  launchctl print gui/$(id -u)/$NAME >/dev/null 2>&1 && echo "an: http://$(scutil --get LocalHostName).local:27894  /  http://$(ipconfig getifaddr en0):27894" || echo "aus" ;;
esac
