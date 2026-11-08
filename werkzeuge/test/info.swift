import CoreGraphics
import Foundation
let b = CGDisplayBounds(CGMainDisplayID()); print("display", b)
if let l = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] {
  for w in l where (w[kCGWindowLayer as String] as? Int) == 0 { 
    let o = w[kCGWindowOwnerName as String] as? String ?? ""; let bd = w[kCGWindowBounds as String] ?? ""
    print(o, bd) }
}
print("mouse", CGEvent(source: nil)!.location)
