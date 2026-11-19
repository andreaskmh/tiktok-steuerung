// Sammelbild (Kontaktbogen) aus Vorschaubildern: blatt <ausgabe.jpg> <spalten> <bild1> <text1> [<bild2> <text2> ...]
// Jede Kachel 180x240 mit Nummer/Text oben links. Für die Research-Sortierung (werkzeuge/research.py).
import AppKit

let a = CommandLine.arguments
guard a.count >= 5, let spalten = Int(a[2]) else {
    print("blatt <ausgabe.jpg> <spalten> <bild> <text> ..."); exit(1)
}
let paare = stride(from: 3, to: a.count - 1, by: 2).map { (a[$0], a[$0 + 1]) }
let w = 180, h = 240
let zeilen = (paare.count + spalten - 1) / spalten
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: spalten * w, pixelsHigh: zeilen * h,
                           bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                           colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor.black.setFill(); NSRect(x: 0, y: 0, width: spalten * w, height: zeilen * h).fill()
for (i, (pfad, text)) in paare.enumerated() {
    let x = (i % spalten) * w, y = (zeilen - 1 - i / spalten) * h
    if let img = NSImage(contentsOfFile: pfad) {
        img.draw(in: NSRect(x: x + 1, y: y + 1, width: w - 2, height: h - 2))
    }
    let attr: [NSAttributedString.Key: Any] = [.font: NSFont.boldSystemFont(ofSize: 15),
                                               .foregroundColor: NSColor.yellow,
                                               .backgroundColor: NSColor.black.withAlphaComponent(0.75)]
    (" " + text + " " as NSString).draw(at: NSPoint(x: x + 3, y: y + h - 22), withAttributes: attr)
}
NSGraphicsContext.restoreGraphicsState()
let jpg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.7])!
try! jpg.write(to: URL(fileURLWithPath: a[1]))
