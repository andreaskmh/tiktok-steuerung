import Foundation
import CoreGraphics
// zeiger <x> <y>        : setzt den Mauszeiger auf Bildschirmpunkte (ohne Klick).
// zeiger rel <fx> <fy>  : relativ zum iPhone-Fenster (0..1), z. B. "zeiger rel 0.5 0.5" = Fenstermitte.
// Danach kann das Mini-Gerät an dieser Stelle echt wischen/scrollen (Gerät bewegt den Zeiger nicht absolut).
let a = CommandLine.arguments
var x = 0.0, y = 0.0
if a.count == 4 && a[1] == "rel" {
    let p = Process(); p.executableURL = URL(fileURLWithPath: ((Bundle.main.executablePath ?? a[0]) as NSString).deletingLastPathComponent + "/fenster")
    let pipe = Pipe(); p.standardOutput = pipe; try! p.run(); p.waitUntilExit()
    let f = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8)!.split(separator: " ").compactMap { Double($0.trimmingCharacters(in: .whitespacesAndNewlines)) }
    guard p.terminationStatus == 0, f.count == 5 else { print("iPhone-Fenster nicht gefunden"); exit(1) }
    x = f[1] + f[3] * Double(a[2])!; y = f[2] + f[4] * Double(a[3])!
} else if a.count == 3 {
    x = Double(a[1])!; y = Double(a[2])!
} else { print("Aufruf: zeiger <x> <y> | zeiger rel <fx> <fy>"); exit(2) }
CGWarpMouseCursorPosition(CGPoint(x: x, y: y))
CGAssociateMouseAndMouseCursorPosition(1)
print(Int(x), Int(y))
