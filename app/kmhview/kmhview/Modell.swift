import Foundation
import SwiftUI
#if os(iOS)
import UIKit
#else
import AppKit
#endif

struct Daten: Codable { let stand: String; let konten: [Konto] }
let appName = "viewKMH"
struct Konto: Codable, Identifiable, Equatable {
    static func == (a: Konto, b: Konto) -> Bool { a.name == b.name }
    var id: String { name }
    let name: String
    let avatar: String?
    let stand: String?
    let kennzahlen: Kennzahlen
    let zeitraeume: Zeitraeume
    let tage: [[Wert]]
    let videos_tage: [VideoTage]
    let verlauf: [Tag]
    let bestellmonate: [Bestellmonat]
    let auszahlmonate: [Auszahlmonat]
    let videos: [Top]
    let produkte: [Top]
    let offen: [Offen]
    let videos_aufrufe: [VideoAufrufe]?
    var istAlle: Bool { name == "Alle Accounts" }
}
struct Kennzahlen: Codable {
    let ausgezahlt, offen, verloren, quote_prozent, praemien: Double
    let offen_anzahl, bestellungen: Int
    let bereit: Double?
    let bank: Double?
}
struct Zeitraum: Codable {
    var provision: Double; var bestellungen: Int; var umsatz: Double
    var aufrufe: Int? = nil
    /// Anteil der Provision aus TikToks offiziellen Zahlen (Seite „Daten“), 0…1; Rest aus dem Export gerechnet
    var offiziell: Double? = nil
}
/// Video laut TikTok („Daten“ → Video → Alle anzeigen, Top 25 je Tag nach Aufrufen): t = [[tag, aufrufe, gmv, artikel]]
struct VideoAufrufe: Codable { let titel: String; let datum: String; let konto: String; let t: [[Wert]] }
struct AufrufZeile { let titel: String; let datum: String; let konto: String; let aufrufe: Int; let gmv: Double; let artikel: Int }
struct Zeitraeume: Codable { let heute, gestern, tage3, tage7, tage30: Zeitraum }

/// Gemischtes JSON-Feld (Text oder Zahl) für kompakte Tageslisten [tag, provision, bestellungen, umsatz]
enum Wert: Codable {
    case text(String), zahl(Double)
    init(from d: Decoder) throws {
        let c = try d.singleValueContainer()
        if let x = try? c.decode(Double.self) { self = .zahl(x) } else { self = .text(try c.decode(String.self)) }
    }
    func encode(to e: Encoder) throws { var c = e.singleValueContainer(); switch self { case .text(let t): try c.encode(t); case .zahl(let z): try c.encode(z) } }
    var t: String { if case .text(let x) = self { return x }; return "" }
    var z: Double { if case .zahl(let x) = self { return x }; return 0 }
}
struct VideoTage: Codable { let id: String; let konto: String; let name: String; let t: [[Wert]] }

/// Zeitraum = von…bis (Bestelldatum, inklusive). „Letzte N Tage“ = rollierend inkl. heute, kein Kalendermonat.
struct Spanne: Equatable { var von: Date; var bis: Date }
let tagFormat: DateFormatter = { let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; f.timeZone = .current; return f }()
func tagText(_ d: Date) -> String { tagFormat.string(from: d) }
func kurzDatum(_ d: Date) -> String { d.formatted(.dateTime.day().month(.twoDigits).year().locale(deDE)) }

extension Konto {
    func summe(_ s: Spanne) -> Zeitraum {
        let a = tagText(s.von), b = tagText(s.bis)
        var z = Zeitraum(provision: 0, bestellungen: 0, umsatz: 0, aufrufe: 0, offiziell: 1)
        var amtlich = 0.0
        for r in tage where r.count >= 4 && r[0].t >= a && r[0].t <= b {
            z.provision += r[1].z; z.bestellungen += Int(r[2].z); z.umsatz += r[3].z
            if r.count >= 6 { z.aufrufe! += Int(r[4].z); amtlich += r[1].z * r[5].z }
        }
        if z.provision > 0 { z.offiziell = amtlich / z.provision }
        return z
    }
    func aufrufVideos(_ s: Spanne) -> [AufrufZeile] {
        let a = tagText(s.von), b = tagText(s.bis)
        return (videos_aufrufe ?? []).compactMap { v in
            var n = 0, g = 0.0, art = 0
            for r in v.t where r.count >= 4 && r[0].t >= a && r[0].t <= b { n += Int(r[1].z); g += r[2].z; art += Int(r[3].z) }
            return n > 0 ? AufrufZeile(titel: v.titel, datum: v.datum, konto: v.konto, aufrufe: n, gmv: g, artikel: art) : nil
        }
    }
    func videos(_ s: Spanne) -> [VideoZeile] {
        let a = tagText(s.von), b = tagText(s.bis)
        return videos_tage.compactMap { v in
            var n = 0, g = 0.0, p = 0.0
            for r in v.t where r[0].t >= a && r[0].t <= b { n += Int(r[1].z); g += r[2].z; p += r[3].z }
            return n > 0 ? VideoZeile(id: v.konto + "/" + v.id, video: v.id, konto: v.konto, name: v.name, bestellungen: n, gmv: g, provision: p) : nil
        }.sorted { $0.gmv > $1.gmv }
    }
}
struct VideoZeile: Identifiable { let id: String; let video: String; let konto: String; let name: String; let bestellungen: Int; let gmv: Double; let provision: Double }
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
    case heute = "Heute", gestern = "Gestern", tage3 = "3 Tage", tage7 = "7 Tage", tage30 = "30 Tage", eigen = "Zeitraum"
    var id: String { rawValue }
    /// Feste Zeiträume relativ zu heute; „Letzte N Tage“ enthält heute.
    func spanne(eigen: Spanne) -> Spanne {
        let k = Calendar.current, h = k.startOfDay(for: Date()), minus = { (n: Int) in k.date(byAdding: .day, value: -n, to: h)! }
        switch self {
        case .heute: return Spanne(von: h, bis: h)
        case .gestern: return Spanne(von: minus(1), bis: minus(1))
        case .tage3: return Spanne(von: minus(2), bis: h)
        case .tage7: return Spanne(von: minus(6), bis: h)
        case .tage30: return Spanne(von: minus(29), bis: h)
        case .eigen: return eigen
        }
    }
    func erklaerung(_ s: Spanne) -> String {
        let von = kurzDatum(s.von), bis = kurzDatum(s.bis)
        switch self {
        case .heute: return "Heute, \(bis) (bis zum letzten Abruf)"
        case .gestern: return "Gestern, \(bis), ganzer Tag"
        case .tage3, .tage7, .tage30:
            let n = self == .tage3 ? 3 : self == .tage7 ? 7 : 30
            return "\(von) – \(bis) · letzte \(n) Tage inkl. heute (rollierend, kein Kalendermonat)"
        case .eigen: return "\(von) – \(bis) · eigener Zeitraum"
        }
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
            .appendingPathComponent("Library/Mobile Documents/com~apple~CloudDocs/statsKMH/provision.json")
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
