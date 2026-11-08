import Foundation
import CoreGraphics
let dir = CommandLine.arguments[1]
let lines = try! String(contentsOfFile: dir + "/log.txt").split(separator: "\n")
for l in lines {
  let p = l.split(separator: " "); guard p[2] == "type=22" else { continue }
  let d = try! Data(contentsOf: URL(fileURLWithPath: "\(dir)/e\(p[0]).bin"))
  guard let e = CGEvent(withDataAllocator: nil, data: d as CFData) else { continue }
  let ph = e.getIntegerValueField(.scrollWheelEventScrollPhase), mo = e.getIntegerValueField(.scrollWheelEventMomentumPhase)
  let dx = e.getIntegerValueField(.scrollWheelEventPointDeltaAxis2), dy = e.getIntegerValueField(.scrollWheelEventPointDeltaAxis1)
  if ph != 0 || mo != 0 || dx != 0 { print(p[0], p[1], "ph", ph, "mo", mo, "dx", dx, "dy", dy) }
}
