import AppKit
import CoreGraphics
// echt <x> <y> <variante> [dir]
// variante: clean  = synthetisch, Flags 0, Feld 169 = mach-Ticks, HID-Quelle
//           pid    = wie clean, aber direkt an die iPhone-App (postToPid)
//           replay = echte Aufnahme (dir) mit Original-Blobs, nur Zeit/Ort neu, postToPid
let a = CommandLine.arguments
let x = Double(a[1])!, y = Double(a[2])!, v = a[3]
let pt = CGPoint(x: x, y: y)
let pid = NSRunningApplication.runningApplications(withBundleIdentifier: "com.apple.ScreenContinuity").first!.processIdentifier
let src = CGEventSource(stateID: .hidSystemState)
CGWarpMouseCursorPosition(pt); usleep(80000)
var tb = mach_timebase_info_data_t(); mach_timebase_info(&tb)
func fix(_ e: CGEvent) {
  e.location = pt
  e.flags = []
  let t = mach_absolute_time()
  e.timestamp = CGEventTimestamp(t * UInt64(tb.numer) / UInt64(tb.denom))
  if let f = CGEventField(rawValue: 169) { e.setIntegerValueField(f, value: Int64(t)) }
}
func send(_ e: CGEvent) { if v == "clean" { e.post(tap: .cghidEventTap) } else { e.postToPid(pid) } }
if v == "replay" {
  let dir = a[4]
  var rows: [(Int, Double)] = []
  for l in try! String(contentsOfFile: dir + "/log.txt", encoding: .utf8).split(separator: "\n") {
    let p = l.split(separator: " "); rows.append((Int(p[0])!, Double(p[1])!)) }
  let start = Date(); let t0 = rows.first(where: { $0.0 == 4 })!.1
  for (i, t) in rows where i >= 4 && i <= 200 {
    guard let d = try? Data(contentsOf: URL(fileURLWithPath: String(format: "%@/e%05d.bin", dir, i))),
          let e = CGEvent(withDataAllocator: nil, data: d as CFData) else { continue }
    let w = (t - t0) - Date().timeIntervalSince(start); if w > 0 { usleep(useconds_t(w * 1e6)) }
    fix(e); send(e)
  }
} else {
  func sc(_ dx: Int32, _ ph: Int64, mo: Int64 = 0) {
    let e = CGEvent(scrollWheelEvent2Source: src, units: .pixel, wheelCount: 2, wheel1: 0, wheel2: dx, wheel3: 0)!
    e.setIntegerValueField(.scrollWheelEventIsContinuous, value: 1)
    e.setIntegerValueField(.scrollWheelEventScrollPhase, value: ph)
    e.setIntegerValueField(.scrollWheelEventMomentumPhase, value: mo)
    fix(e); send(e); usleep(8000)
  }
  sc(0, 128); sc(-1, 1)
  for i in 0..<30 { sc(-Int32(3 + i / 4), 2) }
  sc(0, 4)
  for i in 0..<20 { sc(-Int32(12 - i / 2), 0, mo: i == 0 ? 1 : 2) }
  sc(0, 0, mo: 3)
}
