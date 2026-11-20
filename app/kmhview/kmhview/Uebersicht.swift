import SwiftUI
import Charts

// Farben: ruhig, ein Akzent (Indigo→Cyan wie das Icon)
extension Color {
    static let akzent = Color(red: 0.46, green: 0.40, blue: 1.0)
    static let akzent2 = Color(red: 0.30, green: 0.82, blue: 1.0)
    static let gut = Color(red: 0.20, green: 0.78, blue: 0.55)
    static let warn = Color(red: 1.0, green: 0.62, blue: 0.25)
    static let schlecht = Color(red: 1.0, green: 0.36, blue: 0.42)
}
let verlaufFarbe = LinearGradient(colors: [.akzent, .akzent2], startPoint: .topLeading, endPoint: .bottomTrailing)

struct Uebersicht: View {
    @EnvironmentObject var s: Speicher
    @State private var auswahl = "Alle Accounts"
    @State private var periode: Periode = .heute
    @State private var eigen = Spanne(von: Calendar.current.date(byAdding: .day, value: -13, to: Calendar.current.startOfDay(for: Date()))!, bis: Calendar.current.startOfDay(for: Date()))
    @State private var waehlen = false

    var konto: Konto? { s.daten?.konten.first { $0.name == auswahl } ?? s.daten?.konten.first }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    kopf
                    if let d = s.daten { KontoLeiste(konten: d.konten, auswahl: $auswahl) }
                    if let k = konto {
                        Hero(k: k, periode: $periode, eigen: $eigen)
                        Kacheln(k: k)
                        VideoStatistik(k: k, spanne: periode.spanne(eigen: eigen), erklaerung: periode.erklaerung(periode.spanne(eigen: eigen)))
                        if k.istAlle, let d = s.daten { Rangliste(konten: Array(d.konten.dropFirst()), auswahl: $auswahl) }
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
                .padding(.horizontal, 18).padding(.bottom, 30)
                .frame(maxWidth: 720).frame(maxWidth: .infinity)
            }
            .background(Hintergrund())
            .refreshable { s.laden() }
            #if os(iOS)
            .toolbar(.hidden, for: .navigationBar)
            .fileImporter(isPresented: $waehlen, allowedContentTypes: [.folder]) { r in
                if case .success(let url) = r { s.ordnerGewaehlt(url) }
            }
            #endif
        }
    }

    var kopf: some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 2) {
                Text(appName).font(.system(size: 30, weight: .bold, design: .rounded))
                if let d = s.daten {
                    Text("Stand " + d.stand.replacingOccurrences(of: "T", with: " · ")).font(.footnote).foregroundStyle(.secondary)
                }
            }
            Spacer()
            #if os(iOS)
            Button { waehlen = true } label: {
                Image(systemName: s.hatOrdner ? "icloud.fill" : "icloud.and.arrow.down")
                    .font(.system(size: 16, weight: .semibold)).frame(width: 38, height: 38)
                    .background(.ultraThinMaterial, in: Circle())
            }.buttonStyle(.plain)
            #else
            Button { s.laden() } label: { Image(systemName: "arrow.clockwise") }.buttonStyle(.borderless)
            #endif
        }
        .padding(.top, 14)
        .overlay(alignment: .bottomLeading) {
            if let f = s.fehler { Text(f).font(.caption).foregroundStyle(Color.warn).offset(y: 18) }
        }
    }

    var fuss: some View {
        Text("Voraussichtlich = ausgezahlte/bereitstehende + offene Provision nach Bestelldatum, ohne „nicht berechtigt“. „Abgerechnet gesamt“ = von TikTok gutgeschrieben (Status „Bezahlt“). „Zur Auszahlung bereit“ = „Verfügbare Auszahlung“ in der App (abgelesen). „Bereits ausgezahlt“ = abgerechnet + Prämien − bereit (Näherung, ohne Gebühren/Abzüge). „Letzte N Tage“ = rollierend inkl. heute, kein Kalendermonat. Quelle: Partnerbestellungen-Export (\(s.quelle)).")
            .font(.caption2).foregroundStyle(.tertiary).padding(.top, 6)
    }
}

struct Hintergrund: View {
    @Environment(\.colorScheme) var schema
    var body: some View {
        ZStack {
            (schema == .dark ? Color(red: 0.04, green: 0.04, blue: 0.07) : Color(red: 0.96, green: 0.96, blue: 0.98))
            RadialGradient(colors: [Color.akzent.opacity(schema == .dark ? 0.28 : 0.14), .clear], center: .topTrailing, startRadius: 0, endRadius: 520)
        }.ignoresSafeArea()
    }
}

struct Karte<C: View>: View {
    var titel: String? = nil
    var rechts: String? = nil
    @ViewBuilder let inhalt: C
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let t = titel {
                HStack {
                    Text(t).font(.system(.headline, design: .rounded))
                    Spacer()
                    if let r = rechts { Text(r).font(.caption).foregroundStyle(.secondary) }
                }
            }
            inhalt
        }
        .padding(18)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 24, style: .continuous).strokeBorder(.white.opacity(0.06)))
    }
}

struct Avatar: View {
    let konto: Konto?; let name: String; var groesse: CGFloat = 44
    var body: some View {
        Group {
            if name == "Alle Accounts" {
                ZStack { Circle().fill(verlaufFarbe); Image(systemName: "square.stack.3d.up.fill").foregroundStyle(.white).font(.system(size: groesse * 0.38, weight: .semibold)) }
            } else if let b = avatarBild(konto?.avatar) {
                b.resizable().scaledToFill()
            } else {
                ZStack { Circle().fill(Color.secondary.opacity(0.25)); Text(String(name.prefix(1)).uppercased()).font(.system(size: groesse * 0.42, weight: .bold, design: .rounded)) }
            }
        }
        .frame(width: groesse, height: groesse).clipShape(Circle())
    }
}

struct KontoLeiste: View {
    let konten: [Konto]; @Binding var auswahl: String
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 14) {
                ForEach(konten) { k in
                    let an = k.name == auswahl
                    Button { withAnimation(.snappy) { auswahl = k.name } } label: {
                        VStack(spacing: 6) {
                            Avatar(konto: k, name: k.name, groesse: 54)
                                .padding(3)
                                .overlay(Circle().strokeBorder(an ? AnyShapeStyle(verlaufFarbe) : AnyShapeStyle(Color.clear), lineWidth: 2.5))
                            Text(k.istAlle ? "Alle" : k.name).font(.caption2.weight(an ? .semibold : .regular))
                                .lineLimit(1).frame(width: 72).foregroundStyle(an ? .primary : .secondary)
                        }
                    }.buttonStyle(.plain)
                }
            }.padding(.vertical, 2)
        }
    }
}

struct Hero: View {
    let k: Konto; @Binding var periode: Periode; @Binding var eigen: Spanne
    @State private var gewaehlt: Date?
    var punkt: Tag? {
        guard let g = gewaehlt else { return nil }
        return k.verlauf.min { abs(tagDatum($0.tag).timeIntervalSince(g)) < abs(tagDatum($1.tag).timeIntervalSince(g)) }
    }
    var body: some View {
        let sp = periode.spanne(eigen: eigen)
        let z = k.summe(sp)
        VStack(alignment: .leading, spacing: 16) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(Periode.allCases) { p in
                        Button { withAnimation(.snappy) { periode = p } } label: {
                            Text(p.rawValue).font(.footnote.weight(.semibold))
                                .padding(.horizontal, 12).padding(.vertical, 7)
                                .background(periode == p ? Color.white.opacity(0.95) : Color.white.opacity(0.14), in: Capsule())
                                .foregroundStyle(periode == p ? Color.black : Color.white)
                        }.buttonStyle(.plain)
                    }
                }
            }
            if periode == .eigen {
                HStack(spacing: 10) {
                    DatePicker("Von", selection: $eigen.von, in: ...eigen.bis, displayedComponents: .date)
                    DatePicker("Bis", selection: $eigen.bis, in: eigen.von...Date(), displayedComponents: .date)
                }
                .labelsHidden().environment(\.locale, deDE).tint(.white).colorScheme(.dark)
            }
            VStack(alignment: .leading, spacing: 4) {
                Text("Voraussichtliche Provision").font(.subheadline).foregroundStyle(.white.opacity(0.75))
                Text(euro(z.provision)).font(.system(size: 44, weight: .bold, design: .rounded)).foregroundStyle(.white)
                    .contentTransition(.numericText()).minimumScaleFactor(0.6).lineLimit(1)
                Text("\(zahl(z.bestellungen)) Bestellungen · \(euro(z.umsatz, kurz: true)) Umsatz")
                    .font(.footnote).foregroundStyle(.white.opacity(0.75))
                Text(periode.erklaerung(sp)).font(.caption2).foregroundStyle(.white.opacity(0.6)).padding(.top, 2)
            }
            Chart(k.verlauf) { t in
                AreaMark(x: .value("Tag", tagDatum(t.tag)), y: .value("€", t.provision))
                    .interpolationMethod(.catmullRom)
                    .foregroundStyle(LinearGradient(colors: [.white.opacity(0.35), .white.opacity(0)], startPoint: .top, endPoint: .bottom))
                LineMark(x: .value("Tag", tagDatum(t.tag)), y: .value("€", t.provision))
                    .interpolationMethod(.catmullRom).foregroundStyle(.white).lineStyle(StrokeStyle(lineWidth: 2.2, lineCap: .round))
                if let p = punkt, p.tag == t.tag {
                    RuleMark(x: .value("Tag", tagDatum(p.tag))).foregroundStyle(.white.opacity(0.5)).lineStyle(StrokeStyle(lineWidth: 1, dash: [3, 3]))
                        .annotation(position: .top, overflowResolution: .init(x: .fit(to: .chart), y: .disabled)) {
                            VStack(spacing: 1) {
                                Text(euro(p.provision)).font(.caption.weight(.bold)).monospacedDigit()
                                Text(tagDatum(p.tag).formatted(.dateTime.weekday(.abbreviated).day().month(.abbreviated).locale(deDE))).font(.caption2)
                            }
                            .padding(.horizontal, 8).padding(.vertical, 4)
                            .background(.white, in: RoundedRectangle(cornerRadius: 8, style: .continuous)).foregroundStyle(.black)
                        }
                    PointMark(x: .value("Tag", tagDatum(p.tag)), y: .value("€", p.provision)).foregroundStyle(.white).symbolSize(70)
                }
            }
            .chartXSelection(value: $gewaehlt)
            .chartXAxis { AxisMarks(values: .stride(by: .day, count: 7)) { _ in AxisValueLabel(format: .dateTime.day().month(.abbreviated)).foregroundStyle(.white.opacity(0.6)) } }
            .chartYAxis { AxisMarks(position: .trailing, values: .automatic(desiredCount: 3)) { v in
                AxisGridLine().foregroundStyle(.white.opacity(0.12))
                AxisValueLabel { if let d = v.as(Double.self) { Text(euro(d, kurz: true)).font(.caption2).foregroundStyle(.white.opacity(0.55)) } } } }
            .frame(height: 150).padding(.top, 26)
            Text("Verlauf: letzte 30 Tage, Provision je Bestelltag – antippen oder darüberfahren für Werte").font(.caption2).foregroundStyle(.white.opacity(0.6))
        }
        .padding(20)
        .background(
            ZStack {
                LinearGradient(colors: [Color(red: 0.27, green: 0.20, blue: 0.85), Color(red: 0.12, green: 0.45, blue: 0.95)], startPoint: .topLeading, endPoint: .bottomTrailing)
                RadialGradient(colors: [Color.akzent2.opacity(0.5), .clear], center: .topTrailing, startRadius: 0, endRadius: 260)
            }.clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous)))
        .shadow(color: Color.akzent.opacity(0.35), radius: 24, y: 10)
    }
}

struct VideoStatistik: View {
    let k: Konto; let spanne: Spanne; let erklaerung: String
    var body: some View {
        let l = k.videos(spanne)
        Karte(titel: "Video-Performance", rechts: "\(l.count) Videos mit Verkäufen") {
            Text(erklaerung).font(.caption).foregroundStyle(.secondary)
            HStack(spacing: 10) {
                Mini(titel: "Sales", wert: zahl(l.reduce(0) { $0 + $1.bestellungen }))
                Mini(titel: "GMV", wert: euro(l.reduce(0) { $0 + $1.gmv }, kurz: true))
                Mini(titel: "Aufrufe", wert: "–")
            }
            if l.isEmpty { Text("Keine Verkäufe in diesem Zeitraum.").font(.subheadline).foregroundStyle(.secondary) }
            ForEach(Array(l.prefix(10).enumerated()), id: \.offset) { i, v in
                let zeile = HStack(spacing: 12) {
                    Text("\(i + 1)").font(.system(.footnote, design: .rounded).weight(.bold)).foregroundStyle(.secondary).frame(width: 18)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(v.name).font(.subheadline).lineLimit(1)
                        Text((k.istAlle ? v.konto + " · " : "") + "\(zahl(v.bestellungen)) Sales · \(euro(v.provision)) Provision")
                            .font(.caption).foregroundStyle(.secondary).lineLimit(1)
                    }
                    Spacer(minLength: 8)
                    Text(euro(v.gmv)).font(.subheadline.weight(.semibold)).monospacedDigit()
                    Image(systemName: "arrow.up.right").font(.caption2).foregroundStyle(.tertiary)
                }
                if let url = URL(string: "https://www.tiktok.com/@\(v.konto)/video/\(v.video)") { Link(destination: url) { zeile }.buttonStyle(.plain) } else { zeile }
            }
            Text("Sales/GMV aus dem Partnerbestellungen-Export (nach Bestelldatum). Aufrufe, Likes, Kommentare folgen, sobald eine Quelle angebunden ist.")
                .font(.caption2).foregroundStyle(.tertiary)
        }
    }
}

struct Mini: View {
    let titel: String; let wert: String
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(titel).font(.caption2).foregroundStyle(.secondary)
            Text(wert).font(.system(.headline, design: .rounded)).monospacedDigit().lineLimit(1).minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(10)
        .background(Color.secondary.opacity(0.08), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

struct Kacheln: View {
    let k: Konto
    var body: some View {
        let z = k.kennzahlen
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
            Kachel(symbol: "building.columns.fill", farbe: .gut, titel: "Bereits ausgezahlt", wert: z.bank.map { euro($0) } ?? "–", unter: "aufs Bankkonto (ca.)")
            Kachel(symbol: "banknote.fill", farbe: .gut, titel: "Zur Auszahlung bereit", wert: z.bereit.map { euro($0) } ?? "–", unter: "Verfügbare Auszahlung")
            Kachel(symbol: "hourglass", farbe: .akzent2, titel: "Noch offen", wert: euro(z.offen), unter: "\(zahl(z.offen_anzahl)) Bestellungen")
            Kachel(symbol: "checkmark.seal.fill", farbe: .akzent, titel: "Abgerechnet gesamt", wert: euro(z.ausgezahlt), unter: "von TikTok gutgeschrieben")
            Kachel(symbol: "gift.fill", farbe: .akzent, titel: "Prämien", wert: euro(z.praemien), unter: "soweit abgelesen")
            Kachel(symbol: "xmark.octagon.fill", farbe: .schlecht, titel: "Nicht berechtigt", wert: z.quote_prozent.formatted(.number.locale(deDE)) + " %", unter: euro(z.verloren) + " entgangen")
        }
    }
}

struct Kachel: View {
    let symbol: String; let farbe: Color; let titel: String; let wert: String; var unter: String? = nil
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: symbol).font(.system(size: 14, weight: .semibold)).foregroundStyle(farbe)
                .frame(width: 30, height: 30).background(farbe.opacity(0.15), in: RoundedRectangle(cornerRadius: 9, style: .continuous))
            VStack(alignment: .leading, spacing: 2) {
                Text(titel).font(.caption).foregroundStyle(.secondary)
                Text(wert).font(.system(.title3, design: .rounded).weight(.bold)).minimumScaleFactor(0.6).lineLimit(1)
                Text(unter ?? " ").font(.caption2).foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).strokeBorder(.white.opacity(0.06)))
    }
}

struct Rangliste: View {
    let konten: [Konto]; @Binding var auswahl: String
    var body: some View {
        let max = konten.map { $0.zeitraeume.tage30.provision }.max() ?? 1
        Karte(titel: "Accounts", rechts: "voraussichtlich, letzte 30 Tage") {
            ForEach(konten) { k in
                Button { withAnimation(.snappy) { auswahl = k.name } } label: {
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
                    }.contentShape(Rectangle())
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
            Text("\(Int(anteil * 100))").font(.system(size: 10, weight: .bold, design: .rounded))
        }.frame(width: 36, height: 36)
    }
}

struct Monate: View {
    let k: Konto
    var body: some View {
        Karte(titel: "Nach Bestellmonat", rechts: "% abgeschlossen") {
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
                        Text(m.offen > 0 ? "\(euro(m.offen)) offen" : "komplett").font(.caption).foregroundStyle(.secondary)
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
        Karte(titel: "Abgerechnet", rechts: "pro Monat, nach Abrechnungsdatum") {
            Chart(k.auszahlmonate) { m in
                BarMark(x: .value("Monat", monatName(m.monat)), y: .value("€", m.betrag), width: .ratio(0.55))
                    .foregroundStyle(m.monat == laufenderMonat() ? AnyShapeStyle(Color.akzent.opacity(0.4)) : AnyShapeStyle(verlaufFarbe))
                    .opacity(gewaehlt == nil || gewaehlt == monatName(m.monat) ? 1 : 0.35)
                    .clipShape(RoundedRectangle(cornerRadius: 6, style: .continuous))
                    .annotation(position: .top) {
                        Text(gewaehlt == monatName(m.monat) ? euro(m.betrag) : euro(m.betrag, kurz: true))
                            .font(.caption2.weight(gewaehlt == monatName(m.monat) ? .bold : .medium)).foregroundStyle(gewaehlt == monatName(m.monat) ? .primary : .secondary)
                    }
            }
            .chartXSelection(value: $gewaehlt)
            .chartYAxis(.hidden)
            .frame(height: 170)
        }
    }
}

struct TopListe: View {
    let titel: String; let eintraege: [Top]; let video: Bool; let zeigeKonto: Bool
    var body: some View {
        Karte(titel: titel) {
            ForEach(Array(eintraege.prefix(8).enumerated()), id: \.offset) { i, e in
                let zeile = HStack(spacing: 12) {
                    Text("\(i + 1)").font(.system(.footnote, design: .rounded).weight(.bold)).foregroundStyle(.secondary).frame(width: 18)
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
        }
    }
}

struct OffeneListe: View {
    let k: Konto
    var body: some View {
        Karte(titel: "Offene Bestellungen", rechts: "\(zahl(k.kennzahlen.offen_anzahl)) gesamt") {
            ForEach(k.offen.prefix(10)) { o in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(o.produkt).font(.subheadline).lineLimit(1)
                        Text((k.istAlle ? (o.konto ?? "") + " · " : "") + "bestellt " + o.bestellt).font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Text(euro(o.betrag)).font(.subheadline.weight(.semibold)).monospacedDigit()
                }
            }
        }
    }
}
