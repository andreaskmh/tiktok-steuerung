#!/bin/zsh
# EINMALIG von Artur im Terminal auszuführen (fragt einmal nach dem Mac-Passwort):
#   sudo zsh ~/Documents/Coding/TikTok-Steuerung/vmaus/einrichten.sh
# Danach starten Treiber-Dienst und vmaus bei jedem Mac-Start automatisch, ohne weitere Abfragen.
set -e
[[ $EUID -eq 0 ]] || { echo "Bitte mit sudo starten: sudo zsh $0"; exit 1; }
HIER=${0:A:h}
BENUTZER=${SUDO_USER:-andreask}; UIDNR=$(id -u $BENUTZER)
KD="/Library/Application Support/org.pqrs/Karabiner-DriverKit-VirtualHIDDevice/Applications/Karabiner-VirtualHIDDevice-Daemon.app/Contents/MacOS/Karabiner-VirtualHIDDevice-Daemon"
[[ -x $KD ]] || { echo "Treiber-Paket fehlt: zuerst vmaus/Karabiner-DriverKit-VirtualHIDDevice-8.8.0.pkg installieren"; exit 1; }
[[ -x $HIER/bin/vmaus ]] || { echo "vmaus nicht gebaut: zsh vmaus/build.sh (ohne sudo)"; exit 1; }

# 1) Programm an einen Ort, den nur root ändern kann (sonst könnte jeder Code als root laufen lassen)
install -d -o root -g wheel -m 755 /usr/local/libexec
install -o root -g wheel -m 755 $HIER/bin/vmaus /usr/local/libexec/tiktok-vmaus

# 2) Dienste
schreibe() { # label programm args…
  local L=$1; shift
  local A=""; for x in "$@"; do A+="    <string>$x</string>
"; done
  cat > /Library/LaunchDaemons/$L.plist <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$L</string>
  <key>ProgramArguments</key><array>
$A  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Interactive</string>
  <key>StandardErrorPath</key><string>/var/log/$L.log</string>
</dict></plist>
PL
  chown root:wheel /Library/LaunchDaemons/$L.plist; chmod 644 /Library/LaunchDaemons/$L.plist
  launchctl bootout system/$L 2>/dev/null || true
  launchctl bootstrap system /Library/LaunchDaemons/$L.plist
}
schreibe de.tiktoksteuerung.vhid-daemon "$KD"
sleep 2
schreibe de.tiktoksteuerung.vmaus /usr/local/libexec/tiktok-vmaus /var/run/tiktok-maus.sock $UIDNR
sleep 3
echo "Fertig. Status:"
echo STATUS | nc -U /var/run/tiktok-maus.sock -w 2 || true
