import Foundation
import CoreGraphics
// rec2 <out> <sec>: zeichnet ALLE Maus-/Gesten-/Tasten-Ereignisse auf
let out = CommandLine.arguments[1]; let secs = Double(CommandLine.arguments[2]) ?? 20
try? FileManager.default.createDirectory(atPath: out, withIntermediateDirectories: true)
var n = 0; let t0 = Date(); var log = ""
var mask: CGEventMask = 0
for t: UInt32 in [1,2,3,4,5,6,7,10,11,12,22,29,30,31,32] { mask |= (1 << CGEventMask(t)) }
let cb: CGEventTapCallBack = { _, type, ev, _ in
  if let d = ev.data as Data? {
    try? d.write(to: URL(fileURLWithPath: "\(out)/e\(String(format: "%05d", n)).bin"))
    log += String(format: "%05d %.4f type=%d x=%.0f y=%.0f\n", n, Date().timeIntervalSince(t0), type.rawValue, ev.location.x, ev.location.y); n += 1 }
  return Unmanaged.passUnretained(ev) }
guard let tap = CGEvent.tapCreate(tap: .cgSessionEventTap, place: .headInsertEventTap, options: .listenOnly, eventsOfInterest: mask, callback: cb, userInfo: nil) else { print("tap failed"); exit(1) }
CFRunLoopAddSource(CFRunLoopGetCurrent(), CFMachPortCreateRunLoopSource(nil, tap, 0), .commonModes)
CGEvent.tapEnable(tap: tap, enable: true)
CFRunLoopRunInMode(.defaultMode, secs, false)
try? log.write(toFile: "\(out)/log.txt", atomically: true, encoding: .utf8); print("events", n)
