import Foundation
import CoreGraphics
import AppKit
// tipp rel <fx> <fy>  : Klick wie von Arturs Trackpad (Untertyp "Touch") an eine Stelle im iPhone-Fenster.
// Felder wie bei Arturs echtem Tipp (08.11.2026): Feld 7 (Untertyp) = 3, Druck = 255, Feld 108 = 1.
// Geht direkt an die iPhone-Synchronisierung (postToPid) und zusätzlich normal ins System, wenn "hid" angehängt ist.
let a = CommandLine.arguments
guard a.count >= 4, a[1] == "rel" else { print("Aufruf: tipp rel <fx> <fy> [hid]"); exit(2) }
let p = Process(); p.executableURL = URL(fileURLWithPath: ((Bundle.main.executablePath ?? a[0]) as NSString).deletingLastPathComponent + "/fenster")
let pipe = Pipe(); p.standardOutput = pipe; try! p.run(); p.waitUntilExit()
let f = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8)!.split(separator: " ").compactMap { Double($0.trimmingCharacters(in: .whitespacesAndNewlines)) }
guard p.terminationStatus == 0, f.count == 5 else { print("iPhone-Fenster nicht gefunden"); exit(1) }
let pt = CGPoint(x: f[1] + f[3] * Double(a[2])!, y: f[2] + f[4] * Double(a[3])!)
guard let app = NSRunningApplication.runningApplications(withBundleIdentifier: "com.apple.ScreenContinuity").first else { print("App läuft nicht"); exit(1) }
let hid = a.count > 4 && a[4] == "hid"
CGWarpMouseCursorPosition(pt); CGAssociateMouseAndMouseCursorPosition(1)
usleep(80_000)
func ev(_ t: CGEventType, _ druck: Double) -> CGEvent {
  let e = CGEvent(mouseEventSource: CGEventSource(stateID: .hidSystemState), mouseType: t, mouseCursorPosition: pt, mouseButton: .left)!
  e.setIntegerValueField(.mouseEventClickState, value: 1)
  e.setIntegerValueField(CGEventField(rawValue: 7)!, value: 3)
  e.setDoubleValueField(.mouseEventPressure, value: druck)
  e.setIntegerValueField(CGEventField(rawValue: 108)!, value: 1)
  return e }
for (t, d) in [(CGEventType.leftMouseDown, 1.0), (CGEventType.leftMouseUp, 0.0)] {
  let e = ev(t, d)
  if hid { e.post(tap: .cghidEventTap) } else { e.postToPid(app.processIdentifier) }
  usleep(90_000) }
print("getippt", Int(pt.x), Int(pt.y), hid ? "(hid)" : "(pid)")
