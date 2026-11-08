import Foundation
import CoreGraphics
// usage: swipe <x> <y> <dx> <dy> [steps] [mode]   mode: pad (trackpad phases) | shift (mouse wheel + shift)
let a = CommandLine.arguments
func arg(_ i: Int, _ d: String) -> String { a.count > i ? a[i] : d }
let x = Double(arg(1, "0"))!, y = Double(arg(2, "0"))!
let dx = Int32(arg(3, "-30"))!, dy = Int32(arg(4, "0"))!
let steps = Int(arg(5, "12"))!
let mode = arg(6, "pad")
CGWarpMouseCursorPosition(CGPoint(x: x, y: y))
usleep(50000)
func post(_ ex: Int32, _ ey: Int32, _ phase: Int64?, cont: Bool, flags: CGEventFlags = []) {
    guard let e = CGEvent(scrollWheelEvent2Source: nil, units: cont ? .pixel : .line, wheelCount: 2, wheel1: ey, wheel2: ex, wheel3: 0) else { return }
    e.location = CGPoint(x: x, y: y)
    if cont { e.setIntegerValueField(.scrollWheelEventIsContinuous, value: 1) }
    if let p = phase { e.setIntegerValueField(.scrollWheelEventScrollPhase, value: p) }
    e.flags = flags
    e.post(tap: .cghidEventTap)
    usleep(12000)
}
if mode == "h" {
    for _ in 0..<steps { post(dx > 0 ? 3 : -3, 0, nil, cont: false); usleep(30000) }
} else if mode == "shift" {
    for _ in 0..<steps { post(0, dx > 0 ? 1 : -1, nil, cont: false, flags: .maskShift) }
} else {
    post(0, 0, 128, cont: true)
    post(dx, dy, 1, cont: true)
    for _ in 0..<steps { post(dx, dy, 2, cont: true) }
    post(0, 0, 4, cont: true)
}
