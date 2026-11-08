import Foundation
import CoreGraphics
// rec <out-dir> <seconds>: records scroll + gesture events (raw) with timestamps
let out = CommandLine.arguments[1]; let secs = Double(CommandLine.arguments[2]) ?? 20
try? FileManager.default.createDirectory(atPath: out, withIntermediateDirectories: true)
var n = 0; let t0 = Date()
var log = ""
let types: [UInt32] = [22, 29, 30, 31, 32]  // scroll, gesture & friends
var mask: CGEventMask = 0
for t in types { mask |= (1 << CGEventMask(t)) }
let cb: CGEventTapCallBack = { _, type, ev, _ in
    if let d = ev.data as Data? {
        let dt = Date().timeIntervalSince(t0)
        try? d.write(to: URL(fileURLWithPath: "\(out)/e\(String(format: "%05d", n)).bin"))
        log += String(format: "%05d %.4f type=%d x=%.0f y=%.0f\n", n, dt, type.rawValue, ev.location.x, ev.location.y)
        n += 1
    }
    return Unmanaged.passUnretained(ev)
}
guard let tap = CGEvent.tapCreate(tap: .cgSessionEventTap, place: .headInsertEventTap, options: .listenOnly, eventsOfInterest: mask, callback: cb, userInfo: nil) else { print("tap failed"); exit(1) }
let src = CFMachPortCreateRunLoopSource(nil, tap, 0)
CFRunLoopAddSource(CFRunLoopGetCurrent(), src, .commonModes)
CGEvent.tapEnable(tap: tap, enable: true)
print("recording"); fflush(stdout)
CFRunLoopRunInMode(.defaultMode, secs, false)
try? log.write(toFile: "\(out)/log.txt", atomically: true, encoding: .utf8)
print("events", n)
