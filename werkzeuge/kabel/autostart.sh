#!/bin/zsh
# autostart.sh an|aus|status – iPhone-Server-Wächter (waechter.py) beim Anmelden automatisch starten.
# Nach Änderungen an waechter.py erneut „an“ ausführen (kopiert die neue Fassung).
set -e
HIER=${0:A:h}
NAME=de.tiktok-steuerung.iphone-waechter
PLIST=~/Library/LaunchAgents/$NAME.plist
case ${1:-status} in
an)
  mkdir -p ~/Library/LaunchAgents ~/Library/Logs ~/.local/share/ts-iphone-waechter
  # Kopie außerhalb von ~/Documents: Autostart-Programme dürfen dort oft nicht lesen (macOS-Datenschutz)
  cp $HIER/waechter.py ~/.local/share/ts-iphone-waechter/waechter.py
  cat > $PLIST <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$NAME</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$HOME/.local/share/ts-iphone-waechter/waechter.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>30</integer>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/ts-iphone-waechter.err</string>
</dict></plist>
EOF
  launchctl bootout gui/$(id -u)/$NAME 2>/dev/null || true
  launchctl bootstrap gui/$(id -u) $PLIST
  echo "Autostart an ($PLIST)" ;;
aus)
  launchctl bootout gui/$(id -u)/$NAME 2>/dev/null || true
  rm -f $PLIST
  echo "Autostart aus" ;;
status)
  launchctl print gui/$(id -u)/$NAME 2>/dev/null | grep -E "state =|pid =" || echo "Autostart nicht eingerichtet"
  tail -3 ~/Library/Logs/ts-iphone-waechter.log 2>/dev/null || true ;;
*) echo "Aufruf: zsh werkzeuge/kabel/autostart.sh an|aus|status"; exit 1 ;;
esac
