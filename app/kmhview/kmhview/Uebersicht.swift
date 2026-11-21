import SwiftUI
import Charts

// Mac-Look (Artur 20.11.): Grautöne wie die getönten Dock-Symbole, Farbe nur gedämpft in kleinen Symbolen; hell/dunkel automatisch
func hd(_ hell: UInt32, _ dunkel: UInt32, _ ah: CGFloat = 1, _ ad: CGFloat = 1) -> Color {
    func c(_ x: UInt32) -> (CGFloat, CGFloat, CGFloat) { (CGFloat(x >> 16 & 255) / 255, CGFloat(x >> 8 & 255) / 255, CGFloat(x & 255) / 255) }
    let (a, b) = (c(hell), c(dunkel))
    #if os(iOS)
    return Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: b.0, green: b.1, blue: b.2, alpha: ad) : UIColor(red: a.0, green: a.1, blue: a.2, alpha: ah) })
    #else
    return Color(NSColor(name: nil) { $0.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? NSColor(red: b.0, green: b.1, blue: b.2, alpha: ad) : NSColor(red: a.0, green: a.1, blue: a.2, alpha: ah) })
    #endif
}
extension Color {   // Revolut-artig (Artur 20.11. nachts): Blau-Grau-Verlauf, halbdurchsichtige Glas-Karten, Türkis/Rot für Zahlen
    static let grund = hd(0xEEF1F5, 0x12161D)                  // Grundton (unter dem Verlauf)
    static let flaeche = hd(0xFFFFFF, 0xFFFFFF, 0.78, 0.075)     // Glas-Karten
    static let linie = hd(0x000000, 0xFFFFFF, 0.08, 0.10)
    static let mulde = hd(0x000000, 0xFFFFFF, 0.06, 0.08)        // Spur der Umschalter
    static let symbolGrund = hd(0x000000, 0xFFFFFF, 0.07, 0.12)  // gewählter Umschalter / Zeile
    static let akzent = hd(0x101318, 0xFFFFFF)                  // Hauptknopf, Auswahl
    static let akzent2 = akzent
    static let gut = hd(0x109A7C, 0x34D6AE)
    static let warn = hd(0xC98A2E, 0xE0A95A)
    static let schlecht = hd(0xE0414A, 0xFF5C63)
    static let blau = hd(0x2F6FEB, 0x4C8DFF), lila = hd(0x8E44D9, 0xB57BFF), orange = hd(0xE8820C, 0xFF9F2E)
    static let pink = hd(0xD6336C, 0xFF5C9A), gelb = hd(0xC79A00, 0xFFD23F)
}
/// Rundes buntes Symbol (Revolut-Liste: Krypto lila, Verknüpft türkis …)
struct Symbol: View {
    let name: String; let farbe: Color; var groesse: CGFloat = 30
    var body: some View {
        Image(systemName: name).font(.system(size: groesse * 0.47, weight: .bold)).foregroundStyle(.white)
            .frame(width: groesse, height: groesse).background(farbe.gradient, in: Circle())
    }
}
let verlaufFarbe = LinearGradient(colors: [.gut, .gut], startPoint: .top, endPoint: .bottom)   // Balken (Artur: nicht grau)

struct Uebersicht: View {
    @EnvironmentObject var s: Speicher
    @State private var auswahl = "Alle Accounts"
    @State private var periode: Periode = .heute
    @State private var videoPeriode: Periode = .tage3
    @State private var eigen = Spanne(von: Calendar.current.date(byAdding: .day, value: -13, to: Calendar.current.startOfDay(for: Date()))!, bis: Calendar.current.startOfDay(for: Date()))
    @State private var waehlen = false
    @State private var ranglisten = false

    var konto: Konto? { s.daten?.konten.first { $0.name == auswahl } ?? s.daten?.konten.first }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    kopf
                    Aktualisieren()
                    if let k = konto {
                        Hero(k: k, periode: $periode, eigen: $eigen)
                        Kacheln(k: k)
                        if let d = s.daten { Rangliste(alle: d.konten[0], konten: Array(d.konten.dropFirst()), auswahl: $auswahl) }
                        VideoStatistik(k: k, periode: $videoPeriode, eigen: $eigen)
                        Monate(k: k)
                        Auszahlungen(k: k)
                        TopListe(titel: "Top-Videos", eintraege: k.videos, video: true, zeigeKonto: k.istAlle)
                        TopListe(titel: "Top-Produkte", eintraege: k.produkte, video: false, zeigeKonto: k.istAlle)
                        if !k.offen.isEmpty { OffeneListe(k: k) }
                    } else {
                        ContentUnavailableView("Keine Daten", systemImage: "tray")
                    }
                    fuss
                }
                .padding(.horizontal, randAussen).padding(.bottom, 30)
                .frame(maxWidth: 720).frame(maxWidth: .infinity)
            }
            .background(Hintergrund())
            .dynamicTypeSize(...DynamicTypeSize.large)   // große iPhone-Schrift nicht weiter aufblähen (sonst „reingezoomt“, Artur 20.11.)
            .tint(Color.akzent)   // keine blaue Systemfarbe (Mac-Look)
            .refreshable { s.laden() }
            .task {   // Fortschritt vom Mac: alle 4 s, wenn etwas läuft/wartet, sonst alle 20 s
                while !Task.isCancelled {
                    s.statusLaden()
                    try? await Task.sleep(for: .seconds(s.status?.laeuft == true || s.auftragGesendet != nil ? 4 : 20))
                }
            }
            #if os(iOS)
            .toolbar(.hidden, for: .navigationBar)
            .fileImporter(isPresented: $waehlen, allowedContentTypes: [.folder]) { r in
                if case .success(let url) = r { s.ordnerGewaehlt(url) }
            }
            #endif
        }
    }

    var kopf: some View {
        HStack(spacing: 10) {
            if let d = s.daten { KontoWahl(konten: d.konten, auswahl: $auswahl) }
            else { Text(appName).font(.title2.weight(.bold)); Spacer() }
            Button { ranglisten = true } label: {   // Research-Ranglisten (Seite vom Mac)
                Image(systemName: "list.number").font(.system(size: 16, weight: .semibold)).frame(width: 44, height: 44)
                    .background(Color.flaeche, in: Circle())
            }.buttonStyle(.plain)
            #if os(iOS)
            Button { waehlen = true } label: {
                Image(systemName: s.hatOrdner ? "icloud.fill" : "icloud.and.arrow.down")
                    .font(.system(size: 16, weight: .semibold)).frame(width: 44, height: 44)
                    .background(Color.flaeche, in: Circle())
            }.buttonStyle(.plain)
            #else
            Button { s.laden() } label: {
                Image(systemName: "arrow.clockwise").font(.system(size: 15, weight: .semibold)).frame(width: 40, height: 40).background(Color.flaeche, in: Circle())
            }.buttonStyle(.plain)
            #endif
        }
        .padding(.top, 8)
        #if os(iOS)
        .fullScreenCover(isPresented: $ranglisten) { Ranglisten() }
        #else
        .sheet(isPresented: $ranglisten) { Ranglisten() }
        #endif
        .overlay(alignment: .bottomLeading) {
            if let f = s.fehler { Text(f).font(.caption).foregroundStyle(Color.warn).offset(y: 18) }
        }
    }

    var fuss: some View {
        Text("Vorauss. Provisionen = offizielle Zahl von TikTok (Creator-Bereich → „Daten“), je Tag abgelesen; fehlt ein Tag, wird er aus dem Export gerechnet (ausgezahlte + offene Provision nach Bestelldatum, ohne „nicht berechtigt“). Sales/GMV/Aufrufe ebenso. „Abgerechnet gesamt“ = von TikTok gutgeschrieben (Status „Bezahlt“). „Zur Auszahlung bereit“ = „Verfügbare Auszahlung“ in der App (abgelesen). „Bereits ausgezahlt“ = abgerechnet + Prämien − bereit (Näherung, ohne Gebühren/Abzüge). „Letzte N Tage“ = rollierend inkl. heute, kein Kalendermonat. Quelle: Partnerbestellungen-Export (\(s.quelle)).")
            .font(.caption2).foregroundStyle(.tertiary).padding(.top, 6)
    }
}

/// Knöpfe „Schnell“ / „Voll“ + Fortschritt (der Mac-Dienst bedient dafür das Daten-Handy). Nur auf Knopfdruck.
struct Aktualisieren: View {
    @EnvironmentObject var s: Speicher
    @AppStorage("datenHandy") private var handy = "00008030-00096C8621C3402E"   // Standard: iPhone 11
    @State private var frage: (art: String, titel: String, sek: Int)?   // Rückfrage vor jedem Start (Artur 20.11.)
    static let fmt: DateFormatter = { let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"; return f }()
    func datum(_ t: String?) -> Date { t.flatMap { Self.fmt.date(from: $0) } ?? Date() }
    func dauer(_ sek: Double) -> String {
        let m = Int((sek / 60).rounded())
        return m < 1 ? "< 1 Min." : m < 60 ? "\(m) Min." : "\(m / 60) Std. \(m % 60) Min."
    }
    func uhr(_ sek: Double) -> String { let x = max(0, Int(sek)); return String(format: "%d:%02d", x / 60, x % 60) }

    var body: some View {
        let st = s.status
        Karte {
            if let st, st.laeuft {
                TimelineView(.periodic(from: .now, by: 1)) { ctx in
                    let vergangen = ctx.date.timeIntervalSince(datum(st.start))
                    let rest = max(0, Double(st.rest_sek ?? 0) - ctx.date.timeIntervalSince(datum(st.jetzt)))
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            ProgressView().controlSize(.small)
                            Text("\(st.art == "voll" ? "Voll" : "Schnell")-Aktualisierung läuft").font(.subheadline.weight(.semibold))
                            Spacer()
                            Text("noch ca. \(dauer(rest))").font(.subheadline.weight(.semibold)).monospacedDigit()
                        }
                        ProgressView(value: Double(st.fertig ?? 0), total: Double(max(1, st.gesamt ?? 1))).tint(Color.gut)
                        HStack {
                            Text([st.konto, st.schritt].compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: " · ")).lineLimit(1)
                            Spacer()
                            Text("läuft seit \(uhr(vergangen))").monospacedDigit()
                        }.font(.caption).foregroundStyle(.secondary)
                        Text("Das Daten-Handy wird gerade bedient – bitte solange nicht benutzen. Live-Bild: iPhone-Spiegel auf dem Mac.").font(.caption2).foregroundStyle(.tertiary)
                    }
                }
            } else {
                HStack {
                    Symbol(name: "arrow.triangle.2.circlepath", farbe: .blau, groesse: 26)
                    Text("Daten aktualisieren  ›").font(.subheadline.weight(.semibold)).foregroundStyle(.secondary)
                    Spacer()
                    if let e = st?.ende { Text("zuletzt " + datum(e).formatted(.dateTime.day().month().hour().minute().locale(deDE))).font(.caption).foregroundStyle(.secondary) }
                }
                let wartet = s.auftragGesendet.map { Date().timeIntervalSince($0) < 300 } ?? false
                let gewaehlt = s.geraete.first { $0.udid == handy }
                HStack(spacing: 8) {
                    Image(systemName: "iphone").foregroundStyle(.secondary)
                    Picker("Handy", selection: $handy) {
                        ForEach(s.geraete) { g in Text(g.titel).tag(g.udid) }
                        if gewaehlt == nil { Text(s.geraete.isEmpty ? "Handys werden gesucht …" : "nicht gefunden").tag(handy) }
                    }
                    .labelsHidden().pickerStyle(.menu).lineLimit(1).truncationMode(.middle)
                    .frame(maxWidth: .infinity, alignment: .leading)   // nie breiter als der Bildschirm (sonst ist alles „reingezoomt“)
                    #if os(macOS)
                    Button { s.spiegelOeffnen(handy) } label: { Label("Spiegel", systemImage: "rectangle.on.rectangle") }
                        .buttonStyle(.borderless).font(.caption)
                    #endif
                }
                Text(gewaehlt.map { $0.konten.isEmpty ? "Auf diesem Handy werden alle Accounts versucht (fehlende übersprungen)." : "Accounts: " + $0.konten.joined(separator: ", ") }
                     ?? "Nur Handys mit Entwicklermodus im WLAN/am Kabel erscheinen hier (Mac muss an sein).")
                    .font(.caption2).foregroundStyle(.secondary).lineLimit(2)
                HStack(spacing: 10) {
                    knopf("schnell", "Schnell", "bolt.fill", "Heute, Gestern, Guthaben", st?.schaetzung?["schnell"] ?? 12 * 60, wartet)
                    knopf("voll", "Voll", "arrow.triangle.2.circlepath", "+ 30 Tage, Videos, Export, Prämien", st?.schaetzung?["voll"] ?? 42 * 60, wartet)
                }
                if let g = s.auftragGesendet, wartet {
                    TimelineView(.periodic(from: .now, by: 5)) { ctx in
                        Text(ctx.date.timeIntervalSince(g) > 90 ? "Mac antwortet nicht – ist er an und der Dienst gestartet?" : "Auftrag gesendet – wartet auf den Mac …")
                            .font(.caption).foregroundStyle(ctx.date.timeIntervalSince(g) > 90 ? Color.warn : .secondary)
                    }
                }
                if let f = st?.fehler, !f.isEmpty, Date().timeIntervalSince(datum(st?.ende)) < 6 * 3600 {
                    ForEach(f.reduce(into: [String]()) { if !$0.contains($1) { $0.append($1) } }.prefix(3), id: \.self) { Text($0).font(.caption2).foregroundStyle(Color.warn).lineLimit(2) }
                }
                #if os(iOS)
                if !s.hatOrdner { Text("Erst oben rechts (Wolke) den iCloud-Ordner „statsKMH“ wählen.").font(.caption).foregroundStyle(Color.warn) }
                #endif
            }
        }
        .alert(frage.map { "\($0.titel)-Aktualisierung starten?" } ?? "", isPresented: Binding(get: { frage != nil }, set: { if !$0 { frage = nil } })) {
            Button("Ja, starten") { if let f = frage { s.auftrag(f.art, udid: handy) }; frage = nil }
            Button("Abbrechen", role: .cancel) { frage = nil }
        } message: {
            let g = s.geraete.first { $0.udid == handy }
            Text("\(g?.titel ?? "Das Handy") wird ca. \(dauer(Double(frage?.sek ?? 0))) lang bedient – solange nicht benutzen.")
        }
    }

    func knopf(_ art: String, _ titel: String, _ symbol: String, _ unter: String, _ sek: Int, _ gesperrt: Bool) -> some View {
        Button { frage = (art, titel, sek) } label: {
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Image(systemName: symbol)
                    Text(titel).font(.headline.weight(.bold))
                    Spacer()
                    Text("~\(dauer(Double(sek)))").font(.caption.weight(.semibold)).monospacedDigit().opacity(0.6)
                }
                Text(unter).font(.caption2).opacity(0.6).lineLimit(2).multilineTextAlignment(.leading)
            }
            .foregroundStyle(art == "schnell" ? hd(0xFFFFFF, 0x000000) : Color.primary)
            .padding(.horizontal, 16).padding(.vertical, 14).frame(maxWidth: .infinity, alignment: .leading)
            .background(art == "schnell" ? Color.akzent : Color.symbolGrund, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain).disabled(gesperrt).opacity(gesperrt ? 0.5 : 1)
    }
}

#if os(iOS)
let randAussen: CGFloat = 12, randInnen: CGFloat = 14   // iPhone: kompakter
#else
let randAussen: CGFloat = 18, randInnen: CGFloat = 18
#endif

struct Hintergrund: View {
    @Environment(\.colorScheme) var schema
    var body: some View {
        ZStack {
            Color.grund
            LinearGradient(colors: [hd(0xD6DEE8, 0x3A4656), hd(0xE8ECF1, 0x1D232D), Color.grund], startPoint: .top, endPoint: .center)
            RadialGradient(colors: [hd(0xC9D8E6, 0x4E6276, 1, 0.55), .clear], center: UnitPoint(x: 0.85, y: 0.02), startRadius: 0, endRadius: 420)
        }.ignoresSafeArea()
    }
}

struct Karte<C: View>: View {
    var titel: String? = nil
    var rechts: String? = nil
    var symbol: String? = nil
    var farbe: Color = .gut
    @ViewBuilder let inhalt: C
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let t = titel {
                HStack(spacing: 10) {
                    if let sy = symbol { Symbol(name: sy, farbe: farbe, groesse: 26) }
                    Text(t + "  ›").font(.subheadline.weight(.semibold)).foregroundStyle(.secondary)
                    Spacer()
                    if let r = rechts { Text(r).font(.caption.weight(.medium)).foregroundStyle(.secondary).multilineTextAlignment(.trailing) }
                }
            }
            inhalt
        }
        .padding(16)
        .background(Color.flaeche, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

struct Avatar: View {
    let konto: Konto?; let name: String; var groesse: CGFloat = 44
    var body: some View {
        Group {
            if name == "Alle Accounts" {
                ZStack { Color.flaeche; Image(systemName: "square.stack.3d.up.fill").foregroundStyle(Color.akzent).font(.system(size: groesse * 0.38, weight: .semibold)) }
            } else if let b = Avatar.bild(name, konto?.avatar) {
                b.resizable().scaledToFill()
            } else {
                ZStack { Color.symbolGrund; Text(String(name.prefix(1)).uppercased()).font(.system(size: groesse * 0.42, weight: .bold)) }
            }
        }
        .frame(width: groesse, height: groesse)
        .clipShape(Circle())
        .overlay(Circle().strokeBorder(Color.linie, lineWidth: 0.5))
    }
    /// Bild nur einmal entpacken (sonst ruckelt der Account-Wechsel)
    @MainActor static var cache: [String: Image] = [:]
    @MainActor static func bild(_ name: String, _ b64: String?) -> Image? {
        if let i = cache[name] { return i }
        let i = avatarBild(b64); cache[name] = i; return i
    }
}

/// Account-Auswahl als ein Feld + Liste mit Suche (bleibt übersichtlich bei 10–20 Accounts)
struct KontoWahl: View {
    let konten: [Konto]; @Binding var auswahl: String
    @State private var offen = false
    @State private var neu = false
    @State private var suche = ""
    func titel(_ k: Konto) -> String { k.istAlle ? "Alle Accounts" : k.name }
    var body: some View {
        let k = konten.first { $0.name == auswahl } ?? konten[0]
        Button { offen = true } label: {
            HStack(spacing: 10) {
                Avatar(konto: k, name: k.name, groesse: 44)
                HStack(spacing: 8) {
                    Image(systemName: "magnifyingglass").font(.system(size: 15, weight: .semibold))
                    Text(titel(k)).font(.subheadline.weight(.medium)).lineLimit(1)
                    Spacer(minLength: 4)
                    Text("\(konten.count - 1) Accounts").font(.caption).foregroundStyle(.secondary)
                }
                .padding(.horizontal, 14).frame(height: 44)
                .background(Color.flaeche, in: Capsule())
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .sheet(isPresented: $offen) {
            NavigationStack {
                List(konten.filter { suche.isEmpty || $0.name.localizedCaseInsensitiveContains(suche) }) { x in
                    Button { auswahl = x.name; offen = false } label: {
                        HStack(spacing: 12) {
                            Avatar(konto: x, name: x.name, groesse: 32)
                            VStack(alignment: .leading, spacing: 1) {
                                Text(titel(x)).lineLimit(1)
                                Text("Gestern \(euro(x.zeitraeume.gestern.provision)) · 7 T \(euro(x.zeitraeume.tage7.provision, kurz: true))")
                                    .font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()
                            if x.name == auswahl { Image(systemName: "checkmark").foregroundStyle(Color.akzent) }
                        }.contentShape(Rectangle())
                    }.buttonStyle(.plain)
                    .listRowBackground(Color.flaeche)
                }
                .scrollContentBackground(.hidden).background(Hintergrund())
                .searchable(text: $suche, prompt: "Account suchen")
                .navigationTitle("Account wählen")
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) { Button("Fertig") { offen = false } }
                    ToolbarItem(placement: .cancellationAction) { Button { neu = true } label: { Label("Account hinzufügen", systemImage: "plus") } }
                }
                .sheet(isPresented: $neu) { KontoNeu() }
            }
            #if os(macOS)
            .frame(minWidth: 380, minHeight: 460)
            #endif
        }
    }
}

/// Account hinzufügen: Name + Handy. Einloggen in TikTok macht Artur selbst auf dem Handy.
struct KontoNeu: View {
    @EnvironmentObject var s: Speicher
    @Environment(\.dismiss) var weg
    @AppStorage("datenHandy") private var handy = "00008030-00096C8621C3402E"
    @State private var name = ""
    @State private var fehler = false
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("TikTok-Name, z. B. anduri.official", text: $name)
                        .listRowBackground(Color.flaeche)
                        #if os(iOS)
                        .textInputAutocapitalization(.never).autocorrectionDisabled()
                        #endif
                    Picker("Handy", selection: $handy) { ForEach(s.geraete) { Text($0.titel).tag($0.udid) } }
                } footer: {
                    Text("1. Auf dem gewählten Handy in TikTok mit diesem Account einloggen (Konto hinzufügen) – das machst du selbst.\n2. Hier speichern. Bei der nächsten Aktualisierung „Voll“ wird er abgelesen und erscheint in der Liste.")
                }
                if fehler { Text("Konnte nicht gespeichert werden – iCloud-Ordner gewählt?").foregroundStyle(Color.warn) }
            }
            .scrollContentBackground(.hidden).background(Hintergrund())
            .navigationTitle("Account hinzufügen")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Abbrechen") { weg() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Speichern") { if s.kontoHinzufuegen(name, udid: handy) { weg() } else { fehler = true } }.disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
        }
        #if os(macOS)
        .frame(minWidth: 420, minHeight: 300)
        #endif
    }
}

/// Zeitraum wie bei TikTok: 1. Tipp = Start, 2. Tipp = Ende
struct BereichWahl: View {
    @Binding var spanne: Spanne
    @State private var monat = Calendar.current.date(from: Calendar.current.dateComponents([.year, .month], from: Date()))!
    @State private var start: Date?
    var body: some View {
        let kal = Calendar.current, heute = kal.startOfDay(for: Date())
        let tage = kal.range(of: .day, in: .month, for: monat)!.count
        let vorne = (kal.component(.weekday, from: monat) + 5) % 7   // Montag zuerst
        VStack(spacing: 8) {
            HStack {
                Button { monat = kal.date(byAdding: .month, value: -1, to: monat)! } label: { Image(systemName: "chevron.left").frame(width: 30, height: 28) }
                Spacer()
                Text(monat.formatted(.dateTime.month(.wide).year().locale(deDE))).font(.subheadline.weight(.semibold))
                Spacer()
                Button { monat = kal.date(byAdding: .month, value: 1, to: monat)! } label: { Image(systemName: "chevron.right").frame(width: 30, height: 28) }
                    .disabled(kal.date(byAdding: .month, value: 1, to: monat)! > heute)
            }.buttonStyle(.plain)
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 2), count: 7), spacing: 4) {
                ForEach(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], id: \.self) { Text($0).font(.caption2).foregroundStyle(.secondary) }
                ForEach(0..<vorne, id: \.self) { i in Color.clear.frame(height: 32).id("leer\(i)") }
                ForEach(1...tage, id: \.self) { n in
                    let d = kal.date(byAdding: .day, value: n - 1, to: monat)!
                    let ende = start == nil && (d == spanne.von || d == spanne.bis) || d == start
                    let drin = start == nil && d > spanne.von && d < spanne.bis
                    Button { tippe(d) } label: {
                        Text("\(n)").font(.subheadline.weight(ende ? .bold : .regular)).monospacedDigit()
                            .frame(maxWidth: .infinity, minHeight: 32)
                            .background(ende ? Color.akzent : drin ? Color.symbolGrund : .clear, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
                            .foregroundStyle(ende ? Color.grund : d > heute ? Color.secondary.opacity(0.4) : Color.primary)
                    }.buttonStyle(.plain).disabled(d > heute)
                }
            }
            Text(start == nil ? "\(kurzDatum(spanne.von)) – \(kurzDatum(spanne.bis)) · Starttag antippen zum Ändern" : "Jetzt Endtag antippen")
                .font(.caption).foregroundStyle(.secondary)
        }
        .onAppear { monat = kal.date(from: kal.dateComponents([.year, .month], from: spanne.bis))! }
    }
    func tippe(_ d: Date) {
        if let s = start { spanne = Spanne(von: min(s, d), bis: max(s, d)); start = nil }
        else { start = d }
    }
}

struct Hero: View {
    let k: Konto; @Binding var periode: Periode; @Binding var eigen: Spanne
    var body: some View {
        let sp = periode.spanne(eigen: eigen)
        let z = k.summe(sp)
        VStack(alignment: .leading, spacing: 16) {
            HStack(spacing: 8) {   // welcher Account gerade gezeigt wird – auch ohne nach oben zu scrollen
                Avatar(konto: k, name: k.name, groesse: 22)
                Text(k.istAlle ? "Alle Accounts" : k.name).font(.footnote.weight(.semibold)).foregroundStyle(.secondary)
            }
            VStack(alignment: .leading, spacing: 4) {
                Text("Vorauss. Provisionen").font(.subheadline.weight(.medium)).foregroundStyle(.secondary)
                let tage = (Calendar.current.dateComponents([.day], from: sp.von, to: sp.bis).day ?? 0) + 1
                let vor = k.summe(Spanne(von: Calendar.current.date(byAdding: .day, value: -tage, to: sp.von)!, bis: Calendar.current.date(byAdding: .day, value: -1, to: sp.von)!)).provision
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Text(euro(z.provision)).font(.system(size: 34, weight: .bold))
                        .contentTransition(.numericText()).minimumScaleFactor(0.6).lineLimit(1)
                    if periode != .heute, vor > 0 || z.provision > 0 {   // Veränderung zum gleich langen Zeitraum davor (heute läuft noch → kein Vergleich)
                        Text((z.provision >= vor ? "▲ " : "▼ ") + euro(abs(z.provision - vor)))
                            .font(.subheadline.weight(.semibold)).monospacedDigit().foregroundStyle(z.provision >= vor ? Color.gut : Color.schlecht)
                    }
                }
                Text("\(zahl(z.bestellungen)) Sales · \(euro(z.umsatz, kurz: true)) GMV" + ((z.aufrufe ?? 0) > 0 ? " · \(aufrufeText(z.aufrufe!)) Aufrufe" : ""))
                    .font(.footnote).foregroundStyle(.secondary)
                Text(quelleText(z.offiziell ?? 0)).font(.caption2.weight(.semibold))
                    .padding(.horizontal, 8).padding(.vertical, 3)
                    .background(Color.symbolGrund, in: Capsule()).foregroundStyle((z.offiziell ?? 0) >= 0.999 ? Color.gut : Color.secondary)
                Text(mitZeit(periode.erklaerung(sp), sp)).font(.caption2).foregroundStyle(.secondary).padding(.top, 2)
            }
            ZeitTabs(periode: $periode, ohne: [.tage3])   // 3 Tage nur in der Video-/Aufrufstatistik (Artur 20.11.)
            if periode == .eigen {
                BereichWahl(spanne: $eigen)
            }
            VerlaufChart(k: k).equatable()
            Text("Verlauf: letzte 30 Tage, Provision je Bestelltag · gepunktet = Durchschnitt · Tag antippen für den Wert").font(.caption2).foregroundStyle(.secondary)
        }
        .padding(16)
        .background(Color.flaeche, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

/// 30-Tage-Verlauf. Eigene Ansicht mit eigenem Zustand: Tippen zeichnet nur das Diagramm neu (sonst ruckelt es, Artur 20.11.)
struct VerlaufChart: View, Equatable {
    let k: Konto
    struct P: Identifiable { let id: String; let d: Date; let w: Double }
    let punkte: [P], schnitt: Double, hoch: Double
    @State private var gewaehlt: P?
    init(k: Konto) {
        self.k = k
        punkte = k.verlauf.map { P(id: $0.tag, d: tagDatum($0.tag), w: $0.provision) }
        schnitt = punkte.isEmpty ? 0 : punkte.reduce(0) { $0 + $1.w } / Double(punkte.count)
        hoch = punkte.map(\.w).max() ?? 0
    }
    static func == (a: Self, b: Self) -> Bool { a.k.name == b.k.name && a.punkte.count == b.punkte.count && a.hoch == b.hoch && a.schnitt == b.schnitt }
    var body: some View {
        Chart {
            RuleMark(y: .value("Ø", schnitt)).foregroundStyle(Color.secondary.opacity(0.6)).lineStyle(StrokeStyle(lineWidth: 1.5, lineCap: .round, dash: [0.5, 5]))
            ForEach(punkte) { t in
                AreaMark(x: .value("Tag", t.d), y: .value("€", t.w))
                    .foregroundStyle(LinearGradient(colors: [Color.gut.opacity(0.22), Color.gut.opacity(0)], startPoint: .top, endPoint: .bottom))
                LineMark(x: .value("Tag", t.d), y: .value("€", t.w))
                    .foregroundStyle(Color.gut).lineStyle(StrokeStyle(lineWidth: 2.2, lineCap: .round, lineJoin: .round))
            }
            if let p = gewaehlt {
                RuleMark(x: .value("Tag", p.d)).foregroundStyle(Color.akzent.opacity(0.5)).lineStyle(StrokeStyle(lineWidth: 1, dash: [3, 3]))
                    .annotation(position: .top, overflowResolution: .init(x: .fit(to: .chart), y: .disabled)) {
                        VStack(spacing: 1) {
                            Text(euro(p.w)).font(.caption.weight(.bold)).monospacedDigit()
                            Text(p.d.formatted(.dateTime.weekday(.abbreviated).day().month(.abbreviated).locale(deDE))).font(.caption2)
                        }
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(Color.akzent, in: RoundedRectangle(cornerRadius: 8, style: .continuous)).foregroundStyle(Color.grund)
                    }
                PointMark(x: .value("Tag", p.d), y: .value("€", p.w)).foregroundStyle(Color.akzent).symbolSize(70)
            }
        }
        .chartOverlay { proxy in   // Tippen wählt einen Tag (Ziehen würde mit dem Scrollen kämpfen → Ruckeln)
            GeometryReader { geo in
                Rectangle().fill(.clear).contentShape(Rectangle())
                    .onTapGesture { ort in
                        guard let ebene = proxy.plotFrame, let d: Date = proxy.value(atX: ort.x - geo[ebene].origin.x) else { return }
                        let n = punkte.min { abs($0.d.timeIntervalSince(d)) < abs($1.d.timeIntervalSince(d)) }
                        gewaehlt = n?.id == gewaehlt?.id ? nil : n
                    }
            }
        }
        .chartXAxis { AxisMarks(values: .stride(by: .day, count: 5)) { _ in AxisValueLabel(format: .dateTime.day()).foregroundStyle(Color.secondary) } }
        .chartYScale(domain: 0...max(1, hoch * 1.08))
        .chartYAxis { AxisMarks(position: .trailing, values: [hoch]) { v in
            AxisValueLabel { if let d = v.as(Double.self) { Text(euro(d, kurz: true)).font(.caption2).foregroundStyle(.secondary) } } } }
        .frame(height: 170).padding(.top, 26)
        .onChange(of: k.name) { gewaehlt = nil }
    }
}

/// Zeitraum-Auswahl als schlichte Textreihe (1T 1W 1M …): gewählter Eintrag weiß, Rest grau
struct ZeitTabs: View {
    @Binding var periode: Periode; var ohne: [Periode] = []; var beiWahl: () -> Void = {}
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 2) {
                ForEach(Periode.allCases.filter { !ohne.contains($0) }) { p in
                    Button { periode = p; beiWahl() } label: {
                        Text(p.rawValue).font(.footnote.weight(.semibold))
                            .foregroundStyle(periode == p ? Color.primary : Color.secondary)
                            .padding(.horizontal, 12).padding(.vertical, 7)
                            .background(periode == p ? Color.symbolGrund : .clear, in: Capsule()).contentShape(Capsule())
                    }.buttonStyle(.plain)
                }
            }
            .padding(3).background(Color.mulde, in: Capsule())
        }
    }
}

enum VideoAnsicht: String, CaseIterable, Identifiable { case verkauf = "Nach Verkäufen", aufrufe = "Nach Aufrufen"; var id: String { rawValue } }
enum VideoSortierung: String, CaseIterable, Identifiable {
    case provision = "Provision", gmv = "GMV", sales = "Sales", aufrufe = "Aufrufe", name = "Name"
    var id: String { rawValue }
}

/// Eine Zeile der Video-Liste (Export-Videos und TikTok-Top-Videos einheitlich)
struct VListe: Identifiable {
    let id: String; let titel: String; let unter: String; let provision: Double?; let gmv: Double; let sales: Int
    let aufrufe: Int?; let link: URL?
}

struct VideoStatistik: View {
    let k: Konto; @Binding var periode: Periode; @Binding var eigen: Spanne
    @State private var ansicht: VideoAnsicht = .verkauf
    @State private var sortierung: VideoSortierung = .provision
    @State private var seite = 0
    let proSeite = 10

    func zeilen(_ l: [VideoZeile]) -> [VListe] {
        if ansicht == .verkauf {
            return l.map { v in VListe(id: v.id, titel: v.name, unter: (k.istAlle ? v.konto + " · " : "") + "\(zahl(v.bestellungen)) Sales · \(euro(v.gmv)) GMV",
                                       provision: v.provision, gmv: v.gmv, sales: v.bestellungen, aufrufe: nil,
                                       link: URL(string: "https://www.tiktok.com/@\(v.konto)/video/\(v.video)")) }
        }
        return k.aufrufVideos(periode.spanne(eigen: eigen)).enumerated().map { i, v in
            VListe(id: "\(i)" + v.konto + v.titel, titel: v.titel, unter: (k.istAlle ? v.konto + " · " : "") + (v.datum.isEmpty ? "" : "gepostet \(v.datum) · ") + "\(zahl(v.artikel)) Sales · \(euro(v.gmv)) GMV",
                   provision: nil, gmv: v.gmv, sales: v.artikel, aufrufe: v.aufrufe, link: nil)
        }
    }
    func sortiert(_ z: [VListe]) -> [VListe] {
        switch sortierung {
        case .provision: return z.sorted { ($0.provision ?? $0.gmv) > ($1.provision ?? $1.gmv) }
        case .gmv: return z.sorted { $0.gmv > $1.gmv }
        case .sales: return z.sorted { $0.sales > $1.sales }
        case .aufrufe: return z.sorted { ($0.aufrufe ?? 0) > ($1.aufrufe ?? 0) }
        case .name: return z.sorted { $0.titel.localizedCompare($1.titel) == .orderedAscending }
        }
    }
    var sortierungen: [VideoSortierung] { ansicht == .verkauf ? [.provision, .gmv, .sales, .name] : [.aufrufe, .gmv, .sales, .name] }
    func wert(_ v: VListe) -> (String, String) {
        switch sortierung {
        case .aufrufe: return (aufrufeText(v.aufrufe ?? 0), "Aufrufe")
        case .gmv: return (euro(v.gmv), "GMV")
        case .sales: return (zahl(v.sales), "Sales")
        default: return v.provision.map { (euro($0), "Provision") } ?? (aufrufeText(v.aufrufe ?? 0), "Aufrufe")
        }
    }

    var body: some View {
        let spanne = periode.spanne(eigen: eigen)
        let l = k.videos(spanne)
        let z = k.summe(spanne)
        let alle = sortiert(zeilen(l))
        let seiten = max(1, (alle.count + proSeite - 1) / proSeite)
        let s = min(seite, seiten - 1)
        Karte(titel: "Video-Performance", rechts: "\(l.count) Videos mit Verkäufen", symbol: "play.fill", farbe: .pink) {
            ZeitTabs(periode: $periode) { seite = 0 }
            if periode == .eigen {
                BereichWahl(spanne: $eigen)
            }
            Text(periode.erklaerung(spanne)).font(.caption).foregroundStyle(.secondary)
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
                Mini(titel: "Aufrufe", wert: (z.aufrufe ?? 0) > 0 ? aufrufeText(z.aufrufe!) : "–")
                Mini(titel: "Sales", wert: zahl(l.reduce(0) { $0 + $1.bestellungen }))
                Mini(titel: "GMV", wert: euro(l.reduce(0) { $0 + $1.gmv }, kurz: true))
                Mini(titel: "Provision", wert: euro(l.reduce(0) { $0 + $1.provision }, kurz: true))
            }
            HStack(spacing: 2) {   // Umschalter wie „Top-Gewinner / Top-Verlierer“
                ForEach(VideoAnsicht.allCases) { a in
                    Button { ansicht = a } label: {
                        Text(a.rawValue).font(.footnote.weight(.semibold)).foregroundStyle(ansicht == a ? Color.primary : Color.secondary)
                            .frame(maxWidth: .infinity).padding(.vertical, 8)
                            .background(ansicht == a ? Color.symbolGrund : .clear, in: Capsule()).contentShape(Capsule())
                    }.buttonStyle(.plain)
                }
            }
            .padding(3).background(Color.mulde, in: Capsule())
                .onChange(of: ansicht) { _, a in sortierung = a == .verkauf ? .provision : .aufrufe; seite = 0 }
            HStack {
                Text("\(alle.count) Videos · Zeitraum oben")
                    .font(.caption).foregroundStyle(.secondary)
                Spacer()
                Menu {
                    ForEach(sortierungen) { o in Button { sortierung = o; seite = 0 } label: { if o == sortierung { Label(o.rawValue, systemImage: "checkmark") } else { Text(o.rawValue) } } }
                } label: {
                    Label("Sortiert: \(sortierung.rawValue)", systemImage: "arrow.up.arrow.down").font(.caption.weight(.semibold))
                }.menuStyle(.borderlessButton).fixedSize()
            }
            if alle.isEmpty {
                Text(ansicht == .verkauf ? "Keine Verkäufe in diesem Zeitraum." : "Für diesen Zeitraum noch keine Video-Aufrufe abgelesen.").font(.subheadline).foregroundStyle(.secondary)
            }
            ForEach(Array(alle.dropFirst(s * proSeite).prefix(proSeite).enumerated()), id: \.offset) { i, v in
                let (w, e) = wert(v)
                let zeile = HStack(spacing: 12) {
                    Text("\(s * proSeite + i + 1)").font(.system(.footnote).weight(.bold)).foregroundStyle(.secondary).frame(width: 24)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(v.titel).font(.subheadline).lineLimit(1)
                        Text(v.unter).font(.caption).foregroundStyle(.secondary).lineLimit(1)
                    }
                    Spacer(minLength: 8)
                    VStack(alignment: .trailing, spacing: 0) {
                        Text(w).font(.subheadline.weight(.semibold)).monospacedDigit()
                        Text(e).font(.caption2).foregroundStyle(.secondary)
                    }
                }
                if let url = v.link { Link(destination: url) { zeile }.buttonStyle(.plain) } else { zeile }
            }
            if seiten > 1 {
                HStack {
                    Button { withAnimation(.snappy) { seite = max(0, s - 1) } } label: { Image(systemName: "chevron.left").frame(width: 34, height: 30) }
                        .disabled(s == 0)
                    Spacer()
                    Text("Seite \(s + 1) von \(seiten)").font(.caption.weight(.semibold)).monospacedDigit()
                    Spacer()
                    Button { withAnimation(.snappy) { seite = min(seiten - 1, s + 1) } } label: { Image(systemName: "chevron.right").frame(width: 34, height: 30) }
                        .disabled(s >= seiten - 1)
                }
                .buttonStyle(.bordered).buttonBorderShape(.capsule)
            }
            Text("„Nach Verkäufen“: Sales/GMV/Provision je Video aus dem Partnerbestellungen-Export (nach Bestelldatum, Video antippen öffnet es). „Nach Aufrufen“: TikTok „Daten“ → Video → Alle anzeigen, je Tag die 25 Videos mit den meisten Aufrufen, für den Zeitraum oben zusammengezählt. Aufrufe oben: offizielle TikTok-Zahl. Likes/Kommentare zeigt TikTok dort nicht – folgen mit der TikTok-Schnittstelle (Display API).")
                .font(.caption2).foregroundStyle(.tertiary)
        }
        .onChange(of: k.name) { _, _ in seite = 0 }
    }
}

func aufrufeText(_ n: Int) -> String {
    if n >= 1_000_000 { return (Double(n) / 1e6).formatted(.number.precision(.fractionLength(1)).locale(deDE)) + " Mio." }
    if n >= 10_000 { return (Double(n) / 1e3).formatted(.number.precision(.fractionLength(1)).locale(deDE)) + "K" }
    return zahl(n)
}
/// Erklärung + wann die TikTok-Zahl abgelesen wurde („Heute, 20.11.2026 · Stand 07:05 Uhr“)
extension Hero {
    func mitZeit(_ text: String, _ sp: Spanne) -> String {
        let von = tagText(sp.von), bis = tagText(sp.bis)
        guard let z = k.gelesen?.filter({ $0.key >= von && $0.key <= bis }).values.max(), z.count >= 16 else {
            return text.replacingOccurrences(of: " (bis zum letzten Abruf)", with: "")
        }
        let uhr = String(z.suffix(5))
        if periode == .heute { return text.replacingOccurrences(of: " (bis zum letzten Abruf)", with: "") + " · Stand \(uhr) Uhr" }
        let tag = z.prefix(10).split(separator: "-")
        return text + " · abgelesen \(tag[2]).\(tag[1]). \(uhr) Uhr"
    }
}

func quelleText(_ anteil: Double) -> String {
    if anteil >= 0.999 { return "✓ Offizielle Zahl aus TikTok › Daten (Vorauss. Provisionen)" }
    if anteil <= 0.001 { return "aus Export gerechnet (TikTok-Zahl fehlt noch)" }
    return "\(Int((anteil * 100).rounded())) % offizielle TikTok-Zahl, Rest aus Export"
}

struct Mini: View {
    let titel: String; let wert: String
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(titel).font(.caption.weight(.semibold)).foregroundStyle(.secondary)
            Text(wert).font(.headline.weight(.bold)).monospacedDigit().lineLimit(1).minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(12)
        .background(Color.mulde, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

struct Kacheln: View {
    let k: Konto
    var body: some View {
        let z = k.kennzahlen
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
            Kachel(symbol: "building.columns.fill", farbe: .blau, titel: "Bereits ausgezahlt", wert: z.bank.map { euro($0) } ?? "–", unter: "aufs Bankkonto (ca.)")
            Kachel(symbol: "banknote.fill", farbe: .gut, titel: "Zur Auszahlung bereit", wert: z.bereit.map { euro($0) } ?? "–", unter: "Verfügbare Auszahlung")
            Kachel(symbol: "hourglass", farbe: .orange, titel: "Noch offen", wert: euro(z.offen), unter: "\(zahl(z.offen_anzahl)) Bestellungen")
            Kachel(symbol: "checkmark.seal.fill", farbe: .lila, titel: "Abgerechnet gesamt", wert: euro(z.ausgezahlt), unter: "von TikTok gutgeschrieben")
            Kachel(symbol: "gift.fill", farbe: .pink, titel: "Prämien", wert: euro(z.praemien), unter: "soweit abgelesen")
            Kachel(symbol: "xmark.octagon.fill", farbe: .schlecht, titel: "Nicht berechtigt", wert: z.quote_prozent.formatted(.number.locale(deDE)) + " %", unter: euro(z.verloren) + " entgangen")
        }
    }
}

struct Kachel: View {
    let symbol: String; let farbe: Color; let titel: String; let wert: String; var unter: String? = nil
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .top) {
                Text(titel).font(.subheadline.weight(.semibold)).foregroundStyle(.secondary).lineLimit(1).minimumScaleFactor(0.8)
                Spacer(minLength: 4)
                Symbol(name: symbol, farbe: farbe, groesse: 24)
            }
            Text(wert).font(.title3.weight(.bold)).minimumScaleFactor(0.6).lineLimit(1)
            Text(unter ?? " ").font(.caption).foregroundStyle(.secondary).lineLimit(1)
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(.horizontal, 16).padding(.vertical, 18)
        .background(Color.flaeche, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
    }
}

/// Account-Wechsel sofort, ohne Gleit-/Schiebe-Animation (Artur 21.11.)
func ohneAnimation(_ f: () -> Void) { var t = Transaction(); t.disablesAnimations = true; withTransaction(t, f) }

struct Rangliste: View {
    let alle: Konto; let konten: [Konto]; @Binding var auswahl: String
    var body: some View {
        let max = konten.map { $0.zeitraeume.tage30.provision }.max() ?? 1
        Karte(titel: "Accounts", rechts: "voraussichtlich, letzte 30 Tage", symbol: "person.2.fill", farbe: .blau) {
            Button { ohneAnimation { auswahl = alle.name } } label: {
                HStack(spacing: 12) {
                    Avatar(konto: alle, name: alle.name, groesse: 32)
                    Text("Alle Accounts").font(.subheadline.weight(.semibold))
                    Spacer()
                    Text(euro(alle.zeitraeume.tage30.provision)).font(.subheadline.weight(.semibold)).monospacedDigit()
                    Image(systemName: auswahl == alle.name ? "checkmark.circle.fill" : "circle").foregroundStyle(auswahl == alle.name ? Color.akzent : Color.secondary.opacity(0.4))
                }
                .padding(8).contentShape(Rectangle())
                .background(auswahl == alle.name ? Color.symbolGrund : .clear, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            }.buttonStyle(.plain)
            ForEach(konten) { k in
                let an = k.name == auswahl
                Button { ohneAnimation { auswahl = k.name } } label: {
                    HStack(spacing: 12) {
                        Avatar(konto: k, name: k.name, groesse: 40)
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(k.name).font(.subheadline.weight(.semibold)).lineLimit(1)
                                Spacer()
                                Text(euro(k.zeitraeume.tage30.provision)).font(.subheadline.weight(.semibold)).monospacedDigit()
                            }
                            GeometryReader { g in
                                ZStack(alignment: .leading) {
                                    Capsule().fill(Color.secondary.opacity(0.15))
                                    Capsule().fill(verlaufFarbe).frame(width: max > 0 ? g.size.width * k.zeitraeume.tage30.provision / max : 0)
                                }
                            }.frame(height: 6)
                            Text("Heute \(euro(k.zeitraeume.heute.provision)) · Gestern \(euro(k.zeitraeume.gestern.provision)) · 7 T \(euro(k.zeitraeume.tage7.provision, kurz: true))")
                                .font(.caption2).foregroundStyle(.secondary).lineLimit(1).minimumScaleFactor(0.8)
                        }
                        Image(systemName: an ? "checkmark.circle.fill" : "circle").foregroundStyle(an ? Color.akzent : Color.secondary.opacity(0.4))
                    }
                    .padding(8).contentShape(Rectangle())
                    .background(an ? Color.symbolGrund : .clear, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                }.buttonStyle(.plain)
            }
        }
    }
}

struct Ring: View {
    let anteil: Double; let farbe: Color
    var body: some View {
        ZStack {
            Circle().stroke(Color.secondary.opacity(0.15), lineWidth: 4)
            Circle().trim(from: 0, to: anteil).stroke(farbe, style: StrokeStyle(lineWidth: 4, lineCap: .round)).rotationEffect(.degrees(-90))
            Text("\(Int(anteil * 100))").font(.system(size: 10, weight: .bold))
        }.frame(width: 36, height: 36)
    }
}

struct Monate: View {
    let k: Konto
    var body: some View {
        Karte(titel: "Nach Bestellmonat", rechts: "nach Bestelldatum · % abgerechnet", symbol: "calendar", farbe: .orange) {
            ForEach(k.bestellmonate.reversed()) { m in
                let laeuft = m.monat == laufenderMonat()
                HStack(spacing: 14) {
                    Ring(anteil: m.fertig_prozent / 100, farbe: m.fertig_prozent >= 95 ? .gut : .warn)
                    VStack(alignment: .leading, spacing: 2) {
                        HStack(spacing: 6) {
                            Text(monatName(m.monat, lang: true)).font(.subheadline.weight(.semibold))
                            if laeuft { Text("läuft").font(.caption2.weight(.semibold)).padding(.horizontal, 6).padding(.vertical, 2).background(Color.akzent.opacity(0.18), in: Capsule()).foregroundStyle(Color.akzent) }
                        }
                        Text("\(zahl(m.bestellungen)) Bestellungen").font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {
                        Text(euro(m.vorauss)).font(.subheadline.weight(.semibold)).monospacedDigit()
                        Text(m.offen > 0 ? "davon \(euro(m.offen)) offen" : "komplett abgerechnet").font(.caption).foregroundStyle(.secondary)
                    }
                }
            }
        }
    }
}

struct Auszahlungen: View {
    let k: Konto
    @State private var gewaehlt: String?
    var body: some View {
        Karte(titel: "Abgerechnet pro Monat", rechts: "nach Abrechnungsdatum", symbol: "chart.bar.fill", farbe: .gut) {
            Chart(k.auszahlmonate) { m in
                BarMark(x: .value("Monat", monatName(m.monat)), y: .value("€", m.betrag), width: .ratio(0.55))
                    .foregroundStyle(m.monat == laufenderMonat() ? AnyShapeStyle(Color.gut.opacity(0.4)) : AnyShapeStyle(verlaufFarbe))
                    .opacity(gewaehlt == nil || gewaehlt == monatName(m.monat) ? 1 : 0.35)
                    .clipShape(RoundedRectangle(cornerRadius: 6, style: .continuous))
                    .annotation(position: .top) {
                        Text(gewaehlt == monatName(m.monat) ? euro(m.betrag) : euro(m.betrag, kurz: true))
                            .font(.caption2.weight(gewaehlt == monatName(m.monat) ? .bold : .medium)).foregroundStyle(gewaehlt == monatName(m.monat) ? .primary : .secondary)
                    }
            }
            .chartOverlay { proxy in
                GeometryReader { geo in
                    Rectangle().fill(.clear).contentShape(Rectangle())
                        .onTapGesture { ort in
                            guard let ebene = proxy.plotFrame else { return }
                            let m: String? = proxy.value(atX: ort.x - geo[ebene].origin.x)
                            gewaehlt = m == gewaehlt ? nil : m
                        }
                }
            }
            .chartYAxis(.hidden)
            .frame(height: 170)
        }
    }
}

/// Blätter-Leiste „‹ Seite x von y ›“ (je 10 Einträge)
struct Seiten: View {
    @Binding var seite: Int; let anzahl: Int
    var body: some View {
        if anzahl > 1 {
            HStack {
                Button { withAnimation(.snappy) { seite = max(0, seite - 1) } } label: { Image(systemName: "chevron.left").frame(width: 34, height: 30) }
                    .disabled(seite == 0)
                Spacer()
                Text("Seite \(seite + 1) von \(anzahl)").font(.caption.weight(.semibold)).monospacedDigit()
                Spacer()
                Button { withAnimation(.snappy) { seite = min(anzahl - 1, seite + 1) } } label: { Image(systemName: "chevron.right").frame(width: 34, height: 30) }
                    .disabled(seite >= anzahl - 1)
            }
            .buttonStyle(.bordered).buttonBorderShape(.capsule)
        }
    }
}
func seitenZahl(_ n: Int, pro: Int = 10) -> Int { max(1, (n + pro - 1) / pro) }

struct TopListe: View {
    let titel: String; let eintraege: [Top]; let video: Bool; let zeigeKonto: Bool
    @State private var seite = 0
    var body: some View {
        let s = min(seite, seitenZahl(eintraege.count) - 1)
        Karte(titel: titel, rechts: "\(eintraege.count) Einträge", symbol: video ? "flame.fill" : "bag.fill", farbe: video ? .schlecht : .lila) {
            ForEach(Array(eintraege.dropFirst(s * 10).prefix(10).enumerated()), id: \.offset) { i, e in
                let zeile = HStack(spacing: 12) {
                    Text("\(s * 10 + i + 1)").font(.system(.footnote).weight(.bold)).foregroundStyle(.secondary).frame(width: 24)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(e.name).font(.subheadline).lineLimit(1)
                        Text((zeigeKonto && e.konto != nil ? e.konto! + " · " : "") + "\(zahl(e.bestellungen)) Bestellungen" + (video ? "" : " · \(e.quote_prozent.formatted(.number.locale(deDE))) % n. b."))
                            .font(.caption).foregroundStyle(.secondary).lineLimit(1)
                    }
                    Spacer(minLength: 8)
                    Text(euro(e.betrag)).font(.subheadline.weight(.semibold)).monospacedDigit()
                    if video { Image(systemName: "arrow.up.right").font(.caption2).foregroundStyle(.tertiary) }
                }
                if video, let k = e.konto, !e.id.isEmpty, let url = URL(string: "https://www.tiktok.com/@\(k)/video/\(e.id)") {
                    Link(destination: url) { zeile }.buttonStyle(.plain)
                } else { zeile }
            }
            Seiten(seite: $seite, anzahl: seitenZahl(eintraege.count))
        }
        .onChange(of: eintraege.count) { _, _ in seite = 0 }
    }
}

struct OffeneListe: View {
    let k: Konto
    @State private var seite = 0
    var body: some View {
        let s = min(seite, seitenZahl(k.offen.count) - 1)
        Karte(titel: "Offene Bestellungen", rechts: "\(zahl(k.kennzahlen.offen_anzahl)) gesamt", symbol: "hourglass", farbe: .gelb) {
            ForEach(Array(k.offen.dropFirst(s * 10).prefix(10).enumerated()), id: \.offset) { _, o in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(o.produkt).font(.subheadline).lineLimit(1)
                        Text((k.istAlle ? (o.konto ?? "") + " · " : "") + "bestellt " + o.bestellt).font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Text(euro(o.betrag)).font(.subheadline.weight(.semibold)).monospacedDigit()
                }
            }
            Seiten(seite: $seite, anzahl: seitenZahl(k.offen.count))
            if k.kennzahlen.offen_anzahl > k.offen.count {
                Text("Die neuesten \(k.offen.count) von \(zahl(k.kennzahlen.offen_anzahl)) offenen Bestellungen.").font(.caption2).foregroundStyle(.tertiary)
            }
        }
        .onChange(of: k.name) { _, _ in seite = 0 }
    }
}
