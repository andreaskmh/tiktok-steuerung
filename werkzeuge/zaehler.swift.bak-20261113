import AppKit
import Vision
// zaehler <bild.png>: liest den Galerie-Zähler oben rechts (z. B. "3/12") per Texterkennung.
// Ausgabe "3 12", Exit 1 wenn kein Zähler zu sehen ist.
let img = NSImage(contentsOfFile: CommandLine.arguments[1])!
var r = CGRect(origin: .zero, size: img.size)
let cg = img.cgImage(forProposedRect: &r, context: nil, hints: nil)!
// nur das obere Viertel, rechte Hälfte
let w = cg.width, h = cg.height
let ausschnitt = cg.cropping(to: CGRect(x: w / 2, y: 0, width: w / 2, height: h / 4))!
let req = VNRecognizeTextRequest(); req.recognitionLevel = .accurate; req.usesLanguageCorrection = false
try! VNImageRequestHandler(cgImage: ausschnitt).perform([req])
for o in req.results ?? [] {
  let t = o.topCandidates(1).first?.string.replacingOccurrences(of: " ", with: "") ?? ""
  let p = t.split(separator: "/")
  if p.count == 2, let a = Int(p[0]), let b = Int(p[1]) { print(a, b); exit(0) }
}
exit(1)
