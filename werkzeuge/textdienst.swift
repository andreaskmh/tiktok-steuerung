import AppKit
import Vision
// textdienst: wie „text“, aber bleibt laufen (16.11.2026, Tempo): liest Bildpfade zeilenweise von stdin, gibt je Bild
// die Funde aus (x y b h<TAB>text, wie text.swift) und danach eine Zeile „##ENDE“. Gleiche Erkennung (accurate,
// de-DE + en-US, ohne Sprachkorrektur) – es entfällt nur der Programmstart + das Laden der Erkennung pro Bild.
setvbuf(stdout, nil, _IOFBF, 1 << 16)
while let pfad = readLine() {
  autoreleasepool {
    if let img = NSImage(contentsOfFile: pfad) {
      var r = CGRect(origin: .zero, size: img.size)
      if let cg = img.cgImage(forProposedRect: &r, context: nil, hints: nil) {
        let req = VNRecognizeTextRequest()
        req.recognitionLevel = .accurate
        req.usesLanguageCorrection = false
        req.recognitionLanguages = ["de-DE", "en-US"]
        try? VNImageRequestHandler(cgImage: cg).perform([req])
        for o in req.results ?? [] {
          guard let t = o.topCandidates(1).first?.string else { continue }
          let b = o.boundingBox
          print(String(format: "%.4f %.4f %.4f %.4f\t", b.midX, 1 - b.midY, b.width, b.height) + t.replacingOccurrences(of: "\n", with: " "))
        }
      }
    }
    print("##ENDE")
    fflush(stdout)
  }
}
