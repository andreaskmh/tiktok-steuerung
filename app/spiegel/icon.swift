// Zeichnet das App-Symbol (iPhone mit Spiegel-Wellen auf dunklem Grund) als 1024er-PNG.
// Aufruf: swift icon.swift <ziel.png>   (bauen.sh macht daraus AppIcon.icns)
import AppKit

let groesse: CGFloat = 1024
let bild = NSImage(size: NSSize(width: groesse, height: groesse))
bild.lockFocus()
// macOS-Symbolraster: 824er Fläche mittig, runde Ecken
let flaeche = NSRect(x: 100, y: 100, width: 824, height: 824)
let grund = NSBezierPath(roundedRect: flaeche, xRadius: 185, yRadius: 185)
NSGradient(starting: NSColor(calibratedWhite: 0.32, alpha: 1), ending: NSColor(calibratedWhite: 0.10, alpha: 1))!
    .draw(in: grund, angle: -90)
let konfig = NSImage.SymbolConfiguration(pointSize: 400, weight: .regular)
    .applying(NSImage.SymbolConfiguration(paletteColors: [.white]))
let symbol = NSImage(systemSymbolName: "iphone.radiowaves.left.and.right", accessibilityDescription: nil)!
    .withSymbolConfiguration(konfig)!
let s = symbol.size
symbol.draw(in: NSRect(x: (groesse - s.width) / 2, y: (groesse - s.height) / 2, width: s.width, height: s.height))
bild.unlockFocus()

let rep = NSBitmapImageRep(data: bild.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
