import Foundation
import CoreGraphics
// play <dir> <from> <to> <x> <y>: replays recorded raw events with original timing at (x,y)
let a = CommandLine.arguments
let dir = a[1], from = Int(a[2])!, to = Int(a[3])!, x = Double(a[4])!, y = Double(a[5])!
var times: [Int: Double] = [:]
for l in try! String(contentsOfFile: dir + "/log.txt").split(separator: "\n") {
  let p = l.split(separator: " "); times[Int(p[0])!] = Double(p[1])!
}
CGWarpMouseCursorPosition(CGPoint(x: x, y: y)); usleep(80000)
let start = Date(); let t0 = times[from]!
for i in from...to {
  guard let t = times[i], let d = try? Data(contentsOf: URL(fileURLWithPath: String(format: "%@/e%05d.bin", dir, i))),
        let e = CGEvent(withDataAllocator: nil, data: d as CFData) else { continue }
  let wait = (t - t0) - Date().timeIntervalSince(start)
  if wait > 0 { usleep(useconds_t(wait * 1_000_000)) }
  e.location = CGPoint(x: x, y: y)
  e.timestamp = CGEventTimestamp(clock_gettime_nsec_np(CLOCK_UPTIME_RAW))
  e.post(tap: .cghidEventTap)
}
