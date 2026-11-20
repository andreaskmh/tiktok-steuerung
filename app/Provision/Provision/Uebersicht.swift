import SwiftUI
import Charts

struct Uebersicht: View {
    @EnvironmentObject var s: Speicher
    @State private var kontoName = ""
    @State private var waehlen = false

    var konto: Konto? { s.daten?.konten.first { $0.name == kontoName } ?? s.daten?.konten.first }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let f = s.fehler { Text(f).font(.footnote).foregroundStyle(.orange) }
                    if let d = s.daten, d.konten.count > 1 {
                        Picker("Konto", selection: $kontoName) {
                            ForEach(d.konten) { Text($0.name).tag($0.name) }
                        }.pickerStyle(.segmented)
                    }
                    if let k = konto { Inhalt(k: k) } else { ContentUnavailableView("Keine Daten", systemImage: "tray") }
                    if let d = s.daten {
                        Text("Stand \(d.stand.replacingOccurrences(of: "T", with: " ")) · Quelle: \(s.quelle)")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }.padding()
            }
            .refreshable { s.laden() }
            .navigationTitle(konto?.name ?? "Provision")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                Button { waehlen = true } label: { Image(systemName: s.hatOrdner ? "folder.badge.gearshape" : "folder.badge.plus") }
            }
            .fileImporter(isPresented: $waehlen, allowedContentTypes: [.folder]) { r in
                if case .success(let url) = r { s.ordnerGewaehlt(url) }
            }
        }
    }
}

struct Inhalt: View {
    let k: Konto
    var body: some View {
        let z = k.kennzahlen
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
            Kachel(titel: "Ausgezahlt", wert: euro(z.ausgezahlt), farbe: .green)
            Kachel(titel: "Noch offen", wert: euro(z.offen), unter: "\(z.offen_anzahl) Bestellungen", farbe: .blue)
            Kachel(titel: "Prämien", wert: euro(z.praemien), farbe: .purple)
            Kachel(titel: "Nicht berechtigt", wert: "\(z.quote_prozent.formatted()) %", unter: euro(z.verloren) + " verloren", farbe: .red)
        }

        Abschnitt("Nach Bestellmonat") {
            Chart(k.bestellmonate) { m in
                BarMark(x: .value("Monat", monatName(m.monat)), y: .value("€", m.ausgezahlt)).foregroundStyle(by: .value("Art", "Ausgezahlt"))
                BarMark(x: .value("Monat", monatName(m.monat)), y: .value("€", m.offen)).foregroundStyle(by: .value("Art", "Offen"))
            }
            .chartForegroundStyleScale(["Ausgezahlt": Color.green, "Offen": Color.blue.opacity(0.6)])
            .frame(height: 180)
            ForEach(k.bestellmonate.reversed()) { m in
                HStack {
                    VStack(alignment: .leading) {
                        Text(monatName(m.monat) + (m.monat == laufenderMonat() ? " (läuft)" : "")).bold()
                        Text("\(m.bestellungen) Bestellungen · \(m.fertig_prozent.formatted()) % fertig")
                            .font(.caption).foregroundStyle(m.fertig_prozent < 95 ? .orange : .secondary)
                    }
                    Spacer()
                    VStack(alignment: .trailing) {
                        Text(euro(m.vorauss)).bold()
                        Text("davon offen \(euro(m.offen))").font(.caption).foregroundStyle(.secondary)
                    }
                }
                Divider()
            }
        }

        Abschnitt("Auszahlungen pro Monat") {
            Chart(k.auszahlmonate) { m in
                BarMark(x: .value("Monat", monatName(m.monat)), y: .value("€", m.betrag))
                    .foregroundStyle(m.monat == laufenderMonat() ? Color.green.opacity(0.45) : Color.green)
                    .annotation(position: .top) { Text(euro(m.betrag)).font(.caption2) }
            }.frame(height: 160)
        }

        Abschnitt("Top-Videos") {
            ForEach(k.videos) { v in
                Link(destination: URL(string: "https://www.tiktok.com/@\(k.name)/video/\(v.id)")!) {
                    Zeile(name: v.name, rechts: euro(v.betrag), unter: "\(v.bestellungen) Bestellungen")
                }.foregroundStyle(.primary)
            }
        }
        Abschnitt("Top-Produkte") {
            ForEach(k.produkte) { p in
                Zeile(name: p.name, rechts: euro(p.betrag), unter: "\(p.bestellungen) Bestellungen · \(p.quote_prozent.formatted()) % nicht berechtigt")
            }
        }
        if !k.offen.isEmpty {
            Abschnitt("Offene Bestellungen") {
                ForEach(k.offen) { o in Zeile(name: o.produkt, rechts: euro(o.betrag), unter: "bestellt " + o.bestellt) }
            }
        }
    }
}

struct Kachel: View {
    let titel: String; let wert: String; var unter: String? = nil; let farbe: Color
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(titel).font(.caption).foregroundStyle(.secondary)
            Text(wert).font(.title3.bold()).foregroundStyle(farbe).minimumScaleFactor(0.7).lineLimit(1)
            if let u = unter { Text(u).font(.caption2).foregroundStyle(.secondary) }
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(12)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 14))
    }
}

struct Abschnitt<C: View>: View {
    let titel: String; @ViewBuilder let inhalt: C
    init(_ t: String, @ViewBuilder inhalt: () -> C) { titel = t; self.inhalt = inhalt() }
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(titel).font(.headline)
            inhalt
        }
        .padding(14).background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}

struct Zeile: View {
    let name: String; let rechts: String; let unter: String
    var body: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 2) {
                Text(name).font(.subheadline).lineLimit(2)
                Text(unter).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            Text(rechts).font(.subheadline.bold())
        }
        Divider()
    }
}
