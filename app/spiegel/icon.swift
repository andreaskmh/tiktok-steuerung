// Zeichnet das App-Symbol als 1024er-PNG (Grautöne, passend zum Space-Grau-Mac): fast schwarzer Graphit-Grund wie das Claude-Symbol im Graphit-Look, ein iPhone vorne und sein
// durchscheinendes Spiegelbild dahinter (= Mirroring). Aufruf: swift icon.swift <ziel.png>  (bauen.sh macht .icns daraus)
import AppKit

let groesse: CGFloat = 1024
let bild = NSImage(size: NSSize(width: groesse, height: groesse))
bild.lockFocus()
func farbe(_ hex: Int, _ a: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat(hex >> 16 & 255) / 255, green: CGFloat(hex >> 8 & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: a)
}

// macOS-Symbolraster: 824er Fläche mittig, runde Ecken, leichter Schlagschatten
let nurGeraete = CommandLine.arguments.count > 2   // 2. Argument: nur die iPhones (Ebene fürs .icon, Grund macht macOS)
let flaeche = NSRect(x: 100, y: 100, width: 824, height: 824)
let grund = NSBezierPath(roundedRect: flaeche, xRadius: 185, yRadius: 185)
if !nurGeraete {
NSGraphicsContext.saveGraphicsState()
let schatten = NSShadow()
schatten.shadowColor = .black.withAlphaComponent(0.35); schatten.shadowBlurRadius = 24; schatten.shadowOffset = NSSize(width: 0, height: -10)
schatten.set()
farbe(0x1C1D20).setFill(); grund.fill()
NSGraphicsContext.restoreGraphicsState()
NSGradient(colors: [farbe(0x3A3A3D), farbe(0x232325), farbe(0x141415)], atLocations: [0, 0.45, 1], colorSpace: .sRGB)!
    .draw(in: grund, angle: -90)
// Glanz oben
NSGraphicsContext.saveGraphicsState()
grund.addClip()
NSGradient(starting: .white.withAlphaComponent(0.08), ending: .white.withAlphaComponent(0))!
    .draw(in: NSRect(x: 100, y: 512, width: 824, height: 412), angle: -90)
NSGraphicsContext.restoreGraphicsState()
// feiner heller Rand wie bei den dunklen Apple-Symbolen (z. B. Claude im Graphit-Look)
let kante = NSBezierPath(roundedRect: flaeche.insetBy(dx: 2, dy: 2), xRadius: 183, yRadius: 183)
kante.lineWidth = 4
NSColor.white.withAlphaComponent(0.14).setStroke(); kante.stroke()
}

/// Ein iPhone: Gehäuse, Bildschirm mit Verlauf, Dynamic Island
func iphone(_ r: NSRect, alpha: CGFloat) {
    let ecke = r.width * 0.2
    let koerper = NSBezierPath(roundedRect: r, xRadius: ecke, yRadius: ecke)
    NSGraphicsContext.saveGraphicsState()
    if alpha == 1 {
        let s = NSShadow()
        s.shadowColor = .black.withAlphaComponent(0.4); s.shadowBlurRadius = 40; s.shadowOffset = NSSize(width: 0, height: -18)
        s.set()
    }
    farbe(0xD4D6DA, alpha).setFill(); koerper.fill()
    NSGraphicsContext.restoreGraphicsState()
    let rand = r.width * 0.06
    let schirm = r.insetBy(dx: rand, dy: rand)
    let schirmPfad = NSBezierPath(roundedRect: schirm, xRadius: ecke - rand, yRadius: ecke - rand)
    NSGradient(colors: [farbe(0x111215, alpha), farbe(0x2A2C31, alpha)], atLocations: [0, 1], colorSpace: .sRGB)!
        .draw(in: schirmPfad, angle: -90)
    // Inhalt: zwei weiche Farbflächen wie ein Video
    NSGraphicsContext.saveGraphicsState()
    schirmPfad.addClip()
    NSGradient(starting: farbe(0x9AA3B5, 0.55 * alpha), ending: farbe(0x9AA3B5, 0))!
        .draw(fromCenter: NSPoint(x: schirm.minX + schirm.width * 0.3, y: schirm.minY + schirm.height * 0.35), radius: 0,
              toCenter: NSPoint(x: schirm.minX + schirm.width * 0.3, y: schirm.minY + schirm.height * 0.35), radius: schirm.width * 0.9,
              options: [])
    NSGradient(starting: farbe(0xD9DCE3, 0.4 * alpha), ending: farbe(0xD9DCE3, 0))!
        .draw(fromCenter: NSPoint(x: schirm.maxX - schirm.width * 0.2, y: schirm.maxY - schirm.height * 0.3), radius: 0,
              toCenter: NSPoint(x: schirm.maxX - schirm.width * 0.2, y: schirm.maxY - schirm.height * 0.3), radius: schirm.width * 0.8,
              options: [])
    NSGraphicsContext.restoreGraphicsState()
    let insel = NSRect(x: r.midX - r.width * 0.15, y: schirm.maxY - r.width * 0.13, width: r.width * 0.3, height: r.width * 0.085)
    NSColor.black.withAlphaComponent(alpha).setFill()
    NSBezierPath(roundedRect: insel, xRadius: insel.height / 2, yRadius: insel.height / 2).fill()
}

/// Für die .icon-Ebene: nur Umriss + Dynamic Island, wie die schlanken Zeichen der Apple-Symbole im Graphit-Look
func umriss(_ r: NSRect, alpha: CGFloat, breite: CGFloat) {
    let ecke = r.width * 0.2
    let p = NSBezierPath(roundedRect: r.insetBy(dx: breite / 2, dy: breite / 2), xRadius: ecke, yRadius: ecke)
    p.lineWidth = breite
    NSColor.white.withAlphaComponent(alpha).setStroke(); p.stroke()
    let insel = NSRect(x: r.midX - r.width * 0.14, y: r.maxY - breite - r.width * 0.15, width: r.width * 0.28, height: r.width * 0.09)
    NSColor.white.withAlphaComponent(alpha).setFill()
    NSBezierPath(roundedRect: insel, xRadius: insel.height / 2, yRadius: insel.height / 2).fill()
}

let b: CGFloat = 290, h: CGFloat = 590
if nurGeraete {
    umriss(NSRect(x: 512 - b / 2 + 120, y: 512 - h / 2 + 30, width: b, height: h), alpha: 0.45, breite: 26)
    // vorderes iPhone deckt das hintere ab (innen kurz ausradieren), dann sein Umriss
    let vorne = NSRect(x: 512 - b / 2 - 60, y: 512 - h / 2 - 10, width: b, height: h)
    NSGraphicsContext.current!.compositingOperation = .clear
    NSBezierPath(roundedRect: vorne.insetBy(dx: -14, dy: -14), xRadius: b * 0.24, yRadius: b * 0.24).fill()
    NSGraphicsContext.current!.compositingOperation = .sourceOver
    umriss(vorne, alpha: 1, breite: 34)
} else {
iphone(NSRect(x: 512 - b / 2 + 120, y: 512 - h / 2 + 30, width: b, height: h), alpha: 0.35)   // Spiegelbild hinten rechts
iphone(NSRect(x: 512 - b / 2 - 60, y: 512 - h / 2 - 10, width: b, height: h), alpha: 1)
}

bild.unlockFocus()
let rep = NSBitmapImageRep(data: bild.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
