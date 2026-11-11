// airdrop <datei> [<datei> …]
// Öffnet das AirDrop-Fenster von macOS mit den Dateien (Empfänger wählt werkzeuge/airdrop.py per Bedienungshilfen).
// Gleiche Apple-ID auf Mac und iPhone → das iPhone nimmt ohne Nachfrage an, Videos landen in Fotos.
import AppKit

let pfade = CommandLine.arguments.dropFirst().map { URL(fileURLWithPath: $0) }
guard !pfade.isEmpty else { print("Aufruf: airdrop <datei> …"); exit(2) }

class Delegat: NSObject, NSSharingServiceDelegate {
    func sharingService(_ s: NSSharingService, didShareItems items: [Any]) { print("OK gesendet"); exit(0) }
    func sharingService(_ s: NSSharingService, didFailToShareItems items: [Any], error: Error) {
        print("FEHLER \(error.localizedDescription)"); exit(1)
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
guard let dienst = NSSharingService(named: .sendViaAirDrop) else { print("FEHLER AirDrop nicht verfügbar"); exit(1) }
let d = Delegat()
dienst.delegate = d
guard dienst.canPerform(withItems: pfade) else { print("FEHLER AirDrop kann diese Dateien nicht senden"); exit(1) }
DispatchQueue.main.async {
    app.activate(ignoringOtherApps: true)
    dienst.perform(withItems: pfade)
}
DispatchQueue.main.asyncAfter(deadline: .now() + 600) { print("FEHLER Zeitüberschreitung"); exit(1) }
app.run()
