#!/bin/zsh
# Baut iPhone Mirroring.app und legt sie in /Applications.  Aufruf: zsh app/spiegel/bauen.sh
set -e
cd "${0:A:h}"
APP="build/iPhone Mirroring.app"
rm -rf build && mkdir -p "$APP/Contents/MacOS"
swiftc -O Spiegel.swift -o "$APP/Contents/MacOS/Spiegel"
# App-Symbol aus icon.swift (1024er PNG → alle Größen → .icns)
mkdir -p "$APP/Contents/Resources" build/AppIcon.iconset
swift icon.swift build/icon.png
for g in 16 32 128 256 512; do
  sips -z $g $g build/icon.png --out build/AppIcon.iconset/icon_${g}x${g}.png >/dev/null
  sips -z $((g*2)) $((g*2)) build/icon.png --out build/AppIcon.iconset/icon_${g}x${g}@2x.png >/dev/null
done
iconutil -c icns build/AppIcon.iconset -o "$APP/Contents/Resources/AppIcon.icns"
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleExecutable</key><string>Spiegel</string>
  <key>CFBundleIdentifier</key><string>de.tiktok-steuerung.spiegel</string>
  <key>CFBundleName</key><string>iPhone Mirroring</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>NSAppTransportSecurity</key><dict><key>NSAllowsLocalNetworking</key><true/></dict>
  <key>CFBundleURLTypes</key><array><dict><key>CFBundleURLName</key><string>de.tiktok-steuerung.spiegel</string>
    <key>CFBundleURLSchemes</key><array><string>iphonespiegel</string></array></dict></array>
  <key>NSCameraUsageDescription</key><string>Zeigt den Bildschirm des per Kabel angeschlossenen iPhones.</string>
</dict></plist>
EOF
# Feste Signatur (Apple-Development-Zertifikat): macOS merkt sich „Kamera erlauben“ dann über jeden Neubau hinweg.
# Ad-hoc („-“) nur als Notlösung – dann fragt macOS nach jedem Neubau neu.
ID=$(security find-identity -v -p codesigning | awk -F'"' '/Apple Development/{print $2; exit}')
xattr -cr "$APP"; codesign --force --sign "${ID:--}" "$APP"
rm -rf /Applications/iPhone-Spiegel.app "/Applications/iPhone Mirroring.app" && cp -R "$APP" /Applications/
echo "fertig: /Applications/iPhone Mirroring.app"
