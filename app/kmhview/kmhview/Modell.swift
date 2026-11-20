import Foundation
import SwiftUI
#if os(iOS)
import UIKit
#else
import AppKit
#endif

struct Daten: Codable { let stand: String; let konten: [Konto] }
struct Konto: Codable, Identifiable, Equatable {
    static func == (a: Konto, b: Konto) -> Bool { a.name == b.name }
    var id: String { name }
    let name: String
    let avatar: String?
    let stand: String?
    let kennzahlen: Kennzahlen
    let zeitraeume: Zeitraeume
    let verlauf: [Tag]
    let bestellmonate: [Bestellmonat]
    let auszahlmonate: [Auszahlmonat]
    let videos: [Top]
    let produkte: [Top]
    let offen: [Offen]
    var istAlle: Bool { name == "Alle Accounts" }
}
struct Kennzahlen: Codable {
    let ausgezahlt, offen, verloren, quote_prozent, praemien: Double
    let offen_anzahl, bestellungen: Int
}
struct Zeitraum: Codable { let provision: Double; let bestellungen: Int; let umsatz: Double }
struct Zeitraeume: Codable { let heute, gestern, tage7, tage30: Zeitraum }
struct Tag: Codable, Identifiable { var id: String { tag }; let tag: String; let provision: Double }
struct Bestellmonat: Codable, Identifiable {
    var id: String { monat }
    let monat: String; let bestellungen: Int
    let fertig_prozent, ausgezahlt, offen, vorauss, verloren: Double
}
struct Auszahlmonat: Codable, Identifiable { var id: String { monat }; let monat: String; let betrag: Double }
struct Top: Codable, Identifiable {
    let id: String; let name: String; let konto: String?; let betrag: Double; let bestellungen: Int; let quote_prozent: Double
}
struct Offen: Codable, Identifiable {
    var id: String { produkt + bestellt + String(betrag) + (konto ?? "") }
    let produkt: String; let konto: String?; let bestellt: String; let betrag: Double
}

enum Periode: String, CaseIterable, Identifiable {
    case heute = "Heute", gestern = "Gestern", tage7 = "7 Tage", tage30 = "30 Tage"
    var id: String { rawValue }
    func wert(_ z: Zeitraeume) -> Zeitraum {
        switch self { case .heute: z.heute; case .gestern: z.gestern; case .tage7: z.tage7; case .tage30: z.tage30 }
    }
}

let deDE = Locale(identifier: "de_DE")
func euro(_ x: Double, kurz: Bool = false) -> String {
    if kurz && abs(x) >= 10_000 { return (x / 1000).formatted(.number.precision(.fractionLength(1)).locale(deDE)) + " Tsd. €" }
    return x.formatted(.currency(code: "EUR").locale(deDE))
}
func zahl(_ x: Int) -> String { x.formatted(.number.locale(deDE)) }
func monatName(_ m: String, lang: Bool = false) -> String {
    let f = DateFormatter(); f.dateFormat = "yyyy-MM"
    guard let d = f.date(from: m) else { return m }
    let g = DateFormatter(); g.locale = deDE; g.dateFormat = lang ? "LLLL yyyy" : "LLL"
    return g.string(from: d)
}
func tagDatum(_ t: String) -> Date { let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; return f.date(from: t) ?? Date() }
func laufenderMonat() -> String { let f = DateFormatter(); f.dateFormat = "yyyy-MM"; return f.string(from: Date()) }

func avatarBild(_ b64: String?) -> Image? {
    guard let s = b64, let d = Data(base64Encoded: s) else { return nil }
    #if os(iOS)
    guard let u = UIImage(data: d) else { return nil }; return Image(uiImage: u)
    #else
    guard let u = NSImage(data: d) else { return nil }; return Image(nsImage: u)
    #endif
}

@MainActor
final class Speicher: ObservableObject {
    @Published var daten: Daten?
    @Published var quelle = "eingebaut"
    @Published var fehler: String?
    private let schluessel = "ordnerLesezeichen"

    init() { laden() }

    var hatOrdner: Bool {
        #if os(macOS)
        return true
        #else
        return UserDefaults.standard.data(forKey: schluessel) != nil
        #endif
    }

    func ordnerGewaehlt(_ url: URL) {
        let zugriff = url.startAccessingSecurityScopedResource()
        defer { if zugriff { url.stopAccessingSecurityScopedResource() } }
        if let b = try? url.bookmarkData(options: [], includingResourceValuesForKeys: nil, relativeTo: nil) {
            UserDefaults.standard.set(b, forKey: schluessel)
        }
        laden()
    }

    private func lese(_ datei: URL) -> Daten? {
        try? FileManager.default.startDownloadingUbiquitousItem(at: datei)
        var err: NSError?; var g: Data?
        NSFileCoordinator().coordinate(readingItemAt: datei, options: [], error: &err) { g = try? Data(contentsOf: $0) }
        return g.flatMap { try? JSONDecoder().decode(Daten.self, from: $0) }
    }

    func laden() {
        fehler = nil
        #if os(macOS)
        let datei = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Mobile Documents/com~apple~CloudDocs/kmhview/provision.json")
        if let d = lese(datei) { daten = d; quelle = "iCloud"; return }
        #else
        if let b = UserDefaults.standard.data(forKey: schluessel) {
            var alt = false
            if let ordner = try? URL(resolvingBookmarkData: b, options: [], relativeTo: nil, bookmarkDataIsStale: &alt) {
                let zugriff = ordner.startAccessingSecurityScopedResource()
                defer { if zugriff { ordner.stopAccessingSecurityScopedResource() } }
                if let d = lese(ordner.appendingPathComponent("provision.json")) { daten = d; quelle = "iCloud"; return }
                fehler = "provision.json im Ordner nicht lesbar"
            } else { fehler = "Ordner nicht erreichbar – bitte neu wählen" }
        }
        #endif
        if let u = Bundle.main.url(forResource: "provision", withExtension: "json"),
           let g = try? Data(contentsOf: u), let d = try? JSONDecoder().decode(Daten.self, from: g) {
            daten = d; quelle = "eingebaut"
        }
    }
}
