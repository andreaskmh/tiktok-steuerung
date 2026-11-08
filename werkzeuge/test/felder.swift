import Foundation
import CoreGraphics
// felder <bin...>: gibt alle nicht-null Integer-Felder (0..255) eines rohen CGEvents aus
for f in CommandLine.arguments.dropFirst() {
  let d = try! Data(contentsOf: URL(fileURLWithPath: f))
  guard let e = CGEvent(withDataAllocator: nil, data: d as CFData) else { continue }
  var s = "\((f as NSString).lastPathComponent) type=\(e.type.rawValue) flags=\(e.flags.rawValue):"
  for i in 0..<256 { if let fld = CGEventField(rawValue: UInt32(i)) { let v = e.getIntegerValueField(fld); if v != 0 { s += " \(i)=\(v)" } } }
  print(s)
}
