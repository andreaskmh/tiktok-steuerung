#!/bin/zsh
# Alles wieder weg:  sudo zsh ~/Documents/Coding/TikTok-Steuerung/vmaus/entfernen.sh
[[ $EUID -eq 0 ]] || { echo "Bitte mit sudo starten"; exit 1; }
for L in de.tiktoksteuerung.vmaus de.tiktoksteuerung.vhid-daemon; do
  launchctl bootout system/$L 2>/dev/null; rm -f /Library/LaunchDaemons/$L.plist /var/log/$L.log
done
rm -f /usr/local/libexec/tiktok-vmaus /var/run/tiktok-maus.sock
echo "Dienste entfernt. Treiber selbst entfernen (optional):"
echo "  bash '/Library/Application Support/org.pqrs/Karabiner-DriverKit-VirtualHIDDevice/scripts/uninstall/deactivate_driver.sh'"
echo "  sudo bash '/Library/Application Support/org.pqrs/Karabiner-DriverKit-VirtualHIDDevice/scripts/uninstall/remove_files.sh'"
