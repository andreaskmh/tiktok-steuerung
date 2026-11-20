import AppKit
func f(_ x: UInt32, _ a: CGFloat = 1) -> CGColor { CGColor(red: CGFloat(x >> 16 & 255) / 255, green: CGFloat(x >> 8 & 255) / 255, blue: CGFloat(x & 255) / 255, alpha: a) }
func gr(_ c: [CGColor]) -> CGGradient { CGGradient(colorsSpace: CGColorSpace(name: CGColorSpace.sRGB), colors: c as CFArray, locations: nil)! }
// Logo A „Puls“: Türkis→Blau, weiße Kurslinie, leuchtender Endpunkt (statsKMH, Artur 20.11.)
func zeichne(_ n: Int, rand: CGFloat, rund: Bool, schatten: Bool) -> CGImage {
    let N = CGFloat(n)
    let c = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    let r = CGRect(x: rand * N, y: rand * N, width: N * (1 - 2 * rand), height: N * (1 - 2 * rand)); let s = r.width
    let form = rund ? CGPath(roundedRect: r, cornerWidth: s * 0.225, cornerHeight: s * 0.225, transform: nil) : CGPath(rect: r, transform: nil)
    if schatten { c.saveGState(); c.setShadow(offset: CGSize(width: 0, height: -N * 0.012), blur: N * 0.03, color: f(0x000000, 0.35)); c.addPath(form); c.setFillColor(f(0x2C6BFF)); c.fillPath(); c.restoreGState() }
    c.saveGState(); c.addPath(form); c.clip()
    c.drawLinearGradient(gr([f(0x2FE0B5), f(0x2C6BFF)]), start: CGPoint(x: r.minX, y: r.maxY), end: CGPoint(x: r.maxX, y: r.minY), options: [])
    c.drawRadialGradient(gr([f(0xFFFFFF, 0.28), f(0xFFFFFF, 0)]), startCenter: CGPoint(x: r.minX + s * 0.2, y: r.maxY - s * 0.1), startRadius: 0, endCenter: CGPoint(x: r.minX + s * 0.2, y: r.maxY - s * 0.1), endRadius: s * 0.9, options: [])
    let pts = [(0.2, 0.35), (0.4, 0.55), (0.55, 0.42), (0.8, 0.72)].map { CGPoint(x: r.minX + $0.0 * s, y: r.minY + $0.1 * s) }
    let p = CGMutablePath(); p.move(to: pts[0]); for q in pts.dropFirst() { p.addLine(to: q) }
    c.setShadow(offset: CGSize(width: 0, height: -s * 0.01), blur: s * 0.03, color: f(0x0B2A6B, 0.35))
    c.addPath(p); c.setStrokeColor(f(0xFFFFFF)); c.setLineWidth(s * 0.075); c.setLineCap(.round); c.setLineJoin(.round); c.strokePath()
    c.setShadow(offset: .zero, blur: s * 0.1, color: f(0xFFFFFF, 0.9)); c.setFillColor(f(0xFFFFFF))
    c.fillEllipse(in: CGRect(x: pts[3].x - s * 0.07, y: pts[3].y - s * 0.07, width: s * 0.14, height: s * 0.14))
    c.restoreGState(); return c.makeImage()!
}
func sp(_ i: CGImage, _ p: String) { try! NSBitmapImageRep(cgImage: i).representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: p)) }
let a = CommandLine.arguments[1], l = CommandLine.arguments[2]
sp(zeichne(1024, rand: 0, rund: false, schatten: false), a + "/ios.png")
for z in [16, 32, 128, 256, 512] { for k in [1, 2] { sp(zeichne(z * k, rand: 0.098, rund: true, schatten: z >= 128), a + "/mac\(z)@\(k)x.png") } }
sp(zeichne(192, rand: 0, rund: true, schatten: false), l + "/logo@3x.png"); sp(zeichne(128, rand: 0, rund: true, schatten: false), l + "/logo@2x.png"); sp(zeichne(64, rand: 0, rund: true, schatten: false), l + "/logo@1x.png")
sp(zeichne(1024, rand: 0.06, rund: true, schatten: true), "logo/A_vorschau.png")
