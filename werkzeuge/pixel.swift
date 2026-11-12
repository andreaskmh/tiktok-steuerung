// Farben einzelner Punkte eines Bilds: pixel <bild.png> <nx> <ny> [<nx> <ny> …]  (nx/ny = Anteil 0..1)
// Ausgabe je Punkt: "r g b" (0–255), gemittelt über 5×5 Pixel.
import Foundation
import CoreGraphics
import ImageIO
let a = CommandLine.arguments
guard a.count >= 4, let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { exit(1) }
let w = img.width, h = img.height
var buf = [UInt8](repeating: 0, count: w * h * 4)
let ctx = CGContext(data: &buf, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
var i = 2
while i + 1 < a.count {
  let cx = Int(Double(a[i])! * Double(w)), cy = Int(Double(a[i + 1])! * Double(h))
  var s = [0, 0, 0], n = 0
  for y in max(0, cy - 2)...min(h - 1, cy + 2) { for x in max(0, cx - 2)...min(w - 1, cx + 2) {
    let o = (y * w + x) * 4; s[0] += Int(buf[o]); s[1] += Int(buf[o + 1]); s[2] += Int(buf[o + 2]); n += 1 } }
  print(s[0] / n, s[1] / n, s[2] / n)
  i += 2
}
