import Foundation
import SwiftUI

struct Daten: Codable { let stand: String; let konten: [Konto] }
struct Konto: Codable, Identifiable {
    var id: String { name }
    let name: String
    let kennzahlen: Kennzahlen
    let bestellmonate: [Bestellmonat]
    let auszahlmonate: [Auszahlmonat]
    let videos: [Top]
    let produkte: [Top]
    let offen: [Offen]
}
struct Kennzahlen: Codable {
    let ausgezahlt, offen, verloren, quote_prozent, praemien: Double
    let offen_anzahl, bestellungen: Int
}
struct Bestellmonat: Codable, Identifiable {
    var id: String { monat }
    let monat: String; let bestellungen: Int
    let fertig_prozent, ausgezahlt, offen, vorauss, verloren: Double
}
struct Auszahlmonat: Codable, Identifiable { var id: String { monat }; let monat: String; let betrag: Double }
struct Top: Codable, Identifiable {
    let id: String; let name: String; let betrag: Double; let bestellungen: Int; let quote_prozent: Double
}
struct Offen: Codable, Identifiable {
    var id: String { produkt + bestellt + String(betrag) }
    let produkt, bestellt: String; let betrag: Double
}

func euro(_ x: Double) -> String { x.formatted(.currency(code: "EUR").locale(Locale(identifier: "de_DE"))) }
func monatName(_ m: String) -> String {
    let f = DateFormatter(); f.dateFormat = "yyyy-MM"
    guard let d = f.date(from: m) else { return m }
    let g = DateFormatter(); g.locale = Locale(identifier: "de_DE"); g.dateFormat = "MMM yy"
    return g.string(from: d)
}
func laufenderMonat() -> String { let f = DateFormatter(); f.dateFormat = "yyyy-MM"; return f.string(from: Date()) }

@MainActor
final class Speicher: ObservableObject {
    @Published var daten: Daten?
    @Published var quelle = "eingebaut"
    @Published var fehler: String?
    private let schluessel = "ordnerLesezeichen"

    init() { laden() }

    var hatOrdner: Bool { UserDefaults.standard.data(forKey: schluessel) != nil }

    func ordnerGewaehlt(_ url: URL) {
        let zugriff = url.startAccessingSecurityScopedResource()
        defer { if zugriff { url.stopAccessingSecurityScopedResource() } }
        if let b = try? url.bookmarkData(options: [], includingResourceValuesForKeys: nil, relativeTo: nil) {
            UserDefaults.standard.set(b, forKey: schluessel)
        }
        laden()
    }

    func laden() {
        fehler = nil
        if let b = UserDefaults.standard.data(forKey: schluessel) {
            var alt = false
            if let ordner = try? URL(resolvingBookmarkData: b, options: [], relativeTo: nil, bookmarkDataIsStale: &alt) {
                let zugriff = ordner.startAccessingSecurityScopedResource()
                defer { if zugriff { ordner.stopAccessingSecurityScopedResource() } }
                let datei = ordner.appendingPathComponent("provision.json")
                try? FileManager.default.startDownloadingUbiquitousItem(at: datei)
                var err: NSError?
                var gelesen: Data?
                NSFileCoordinator().coordinate(readingItemAt: datei, options: [], error: &err) { gelesen = try? Data(contentsOf: $0) }
                if let g = gelesen, let d = try? JSONDecoder().decode(Daten.self, from: g) {
                    daten = d; quelle = "iCloud"; return
                }
                fehler = "provision.json im Ordner nicht lesbar – zeige eingebaute Daten."
            } else { fehler = "Ordner nicht mehr erreichbar – bitte neu wählen." }
        }
        if let u = Bundle.main.url(forResource: "provision", withExtension: "json"),
           let g = try? Data(contentsOf: u), let d = try? JSONDecoder().decode(Daten.self, from: g) {
            daten = d; quelle = "eingebaut"
        }
    }
}
