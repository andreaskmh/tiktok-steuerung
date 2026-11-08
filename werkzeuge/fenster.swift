import AppKit
import CoreGraphics
// fenster [bundle-id]: gibt "id x y breite hoehe" des größten sichtbaren Fensters der App aus.
// Standard: iPhone-Synchronisierung (com.apple.ScreenContinuity). Exit 1, wenn kein Fenster offen ist.
let bundle = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "com.apple.ScreenContinuity"
let pids = Set(NSRunningApplication.runningApplications(withBundleIdentifier: bundle).map { Int($0.processIdentifier) })
guard !pids.isEmpty else { FileHandle.standardError.write("App \(bundle) läuft nicht\n".data(using: .utf8)!); exit(1) }
let liste = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
var best: (Int, CGRect)? = nil
for w in liste {
    guard let pid = w[kCGWindowOwnerPID as String] as? Int, pids.contains(pid),
          (w[kCGWindowLayer as String] as? Int) == 0,
          let id = w[kCGWindowNumber as String] as? Int,
          let b = w[kCGWindowBounds as String] as? NSDictionary,
          let r = CGRect(dictionaryRepresentation: b) else { continue }
    if best == nil || r.width * r.height > best!.1.width * best!.1.height { best = (id, r) }
}
guard let (id, r) = best else { FileHandle.standardError.write("Kein sichtbares Fenster von \(bundle)\n".data(using: .utf8)!); exit(1) }
print(id, Int(r.minX), Int(r.minY), Int(r.width), Int(r.height))
