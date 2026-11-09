import AppKit
import Vision
// text <bild.png>: erkennt allen Text im Bild. Eine Zeile pro Fund:
//   x y b h<TAB>text     (x/y = Mitte, alles relativ 0..1, Ursprung oben links)
let img = NSImage(contentsOfFile: CommandLine.arguments[1])!
var r = CGRect(origin: .zero, size: img.size)
let cg = img.cgImage(forProposedRect: &r, context: nil, hints: nil)!
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = ["de-DE", "en-US"]
try! VNImageRequestHandler(cgImage: cg).perform([req])
for o in req.results ?? [] {
  guard let t = o.topCandidates(1).first?.string else { continue }
  let b = o.boundingBox
  print(String(format: "%.4f %.4f %.4f %.4f\t", b.midX, 1 - b.midY, b.width, b.height) + t)
}
