#!/bin/zsh
# Baut iPhone Mirroring.app und legt sie in /Applications.  Aufruf: zsh app/spiegel/bauen.sh
set -e
cd "${0:A:h}"
APP="build/iPhone Mirroring.app"
rm -rf build && mkdir -p "$APP/Contents/MacOS"
swiftc -O Spiegel.swift -o "$APP/Contents/MacOS/Spiegel"
# App-Symbol als Icon-Composer-Symbol (.icon → actool → Assets.car + .icns): nur so zeigt macOS es im
# Getönt-/Graphit-Look dunkel wie Claude; ein reines .icns steckt es in eine hellgraue Kachel.
# icon.swift zeichnet die iPhones als Ebene, den dunklen Grund macht das .icon.
mkdir -p "$APP/Contents/Resources" build/AppIcon.icon/Assets
swift icon.swift build/AppIcon.icon/Assets/geraete.png ebene
sips -z 1024 1024 build/AppIcon.icon/Assets/geraete.png >/dev/null   # Retina-Mac zeichnet 2048 px, .icon erwartet 1024
cat > build/AppIcon.icon/icon.json <<'JSON'
{
  "fill" : { "linear-gradient" : [ "srgb:0.22745,0.22745,0.23922,1.00000", "srgb:0.07843,0.07843,0.08235,1.00000" ] },
  "groups" : [ { "layers" : [ { "image-name" : "geraete.png", "name" : "geraete" } ],
                 "shadow" : { "kind" : "neutral", "opacity" : 0.3 },
                 "translucency" : { "enabled" : false, "value" : 0.5 } } ],
  "supported-platforms" : { "squares" : [ "macOS" ] }
}
JSON
xcrun actool build/AppIcon.icon --compile "$APP/Contents/Resources" --platform macosx --minimum-deployment-target 14.0 \
  --app-icon AppIcon --output-partial-info-plist build/icon-info.plist >/dev/null
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleIconName</key><string>AppIcon</string>
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
# Erst kopieren, dann in /Applications signieren: im iCloud-Ordner (~/Documents) hängt der Dateianbieter immer
# wieder FinderInfo an das Paket, daran scheitert codesign („detritus not allowed“).
rm -rf /Applications/iPhone-Spiegel.app "/Applications/iPhone Mirroring.app" && cp -R "$APP" /Applications/
ZIEL="/Applications/iPhone Mirroring.app"
xattr -cr "$ZIEL"; codesign --force --sign "${ID:--}" "$ZIEL"
echo "fertig: /Applications/iPhone Mirroring.app"
