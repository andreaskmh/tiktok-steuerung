import AppKit
import Vision
// zaehler <bild.png>: liest den Galerie-Zähler oben rechts (z. B. "3/12") per Texterkennung.
// Ausgabe "3 12", Exit 1 wenn kein Zähler zu sehen ist.
// 13.11.2026: „2/7“ wurde als „217“ gelesen, „14/14“ als „DL/EL“ -> mehrere Kandidaten, engerer Ausschnitt (vergrößert), schneller Modus als Ersatz.
let img = NSImage(contentsOfFile: CommandLine.arguments[1])!
var r = CGRect(origin: .zero, size: img.size)
let cg = img.cgImage(forProposedRect: &r, context: nil, hints: nil)!
let w = cg.width, h = cg.height
func lies(_ bild: CGImage, _ lvl: VNRequestTextRecognitionLevel) -> (Int, Int)? {
  let req = VNRecognizeTextRequest(); req.recognitionLevel = lvl; req.usesLanguageCorrection = false
  try? VNImageRequestHandler(cgImage: bild).perform([req])
  for o in req.results ?? [] {
    for c in o.topCandidates(10) {
      let t = c.string.replacingOccurrences(of: " ", with: "")
      let p = t.split(separator: "/")
      if p.count == 2, let a = Int(p[0]), let b = Int(p[1]), a >= 1, a <= b, b < 100 { return (a, b) }
    }
  }
  // Ersatz: Schrägstrich als „1“/„l“/„I“/„|“ gelesen („2/7“ -> „217“). Nur eindeutige, gültige Teilung (a <= b).
  for o in req.results ?? [] {
    for c in o.topCandidates(10) {
      let t = Array(c.string.replacingOccurrences(of: " ", with: ""))
      var treffer: [(Int, Int)] = []
      for i in 1..<max(1, t.count - 1) where "1lI|".contains(t[i]) {
        if let a = Int(String(t[..<i])), let b = Int(String(t[(i + 1)...])), a >= 1, a <= b, b < 100 { treffer.append((a, b)) }
      }
      if treffer.count == 1 { return treffer[0] }
    }
  }
  return nil
}
func gross(_ c: CGImage, _ f: Int) -> CGImage {
  let ctx = CGContext(data: nil, width: c.width * f, height: c.height * f, bitsPerComponent: 8, bytesPerRow: 0,
                      space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
  ctx.interpolationQuality = .high; ctx.draw(c, in: CGRect(x: 0, y: 0, width: c.width * f, height: c.height * f))
  return ctx.makeImage()!
}
let viertel = cg.cropping(to: CGRect(x: w / 2, y: 0, width: w / 2, height: h / 4))!
let ecke = gross(cg.cropping(to: CGRect(x: w * 3 / 4, y: h / 20, width: w / 4, height: h / 20))!, 3)
for (b, l) in [(viertel, VNRequestTextRecognitionLevel.accurate), (ecke, .accurate), (ecke, .fast), (viertel, .fast)] {
  if let (a, n) = lies(b, l) { print(a, n); exit(0) }
}
exit(1)
