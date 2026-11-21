import SwiftUI

/// Bereiche der App – unten als schwebende Leiste (Revolut-Art). Neue Bereiche hier ergänzen (Artur 21.11.: „kommt noch mehr“).
enum Bereich: String, CaseIterable, Identifiable {
    case statistik = "Statistik", ranglisten = "Ranglisten"
    var id: String { rawValue }
    var symbol: String { self == .statistik ? "chart.line.uptrend.xyaxis" : "list.number" }
}

struct Haupt: View {
    @AppStorage("bereich") private var bereich = Bereich.statistik
    @State private var besucht: Set<Bereich> = [.statistik]   // Ranglisten erst beim ersten Antippen laden, dann offen halten
    var body: some View {
        ZStack {
            ForEach(Bereich.allCases) { b in
                if besucht.contains(b) {
                    seite(b).opacity(bereich == b ? 1 : 0).allowsHitTesting(bereich == b)
                }
            }
        }
        .safeAreaInset(edge: .bottom, spacing: 0) { leiste }
        .onAppear { besucht.insert(bereich) }
    }

    @ViewBuilder func seite(_ b: Bereich) -> some View {
        switch b {
        case .statistik: Uebersicht()
        case .ranglisten: Ranglisten(eingebettet: true)
        }
    }

    var leiste: some View {
        HStack(spacing: 4) {
            ForEach(Bereich.allCases) { b in
                Button { bereich = b; besucht.insert(b) } label: {
                    VStack(spacing: 3) {
                        Image(systemName: b.symbol).font(.system(size: 18, weight: .semibold))
                        Text(b.rawValue).font(.system(size: 10, weight: .semibold))
                    }
                    .foregroundStyle(bereich == b ? Color.primary : Color.secondary)
                    .frame(maxWidth: .infinity).padding(.vertical, 8)
                    .background(bereich == b ? Color.symbolGrund : .clear, in: Capsule())
                    .contentShape(Capsule())
                }.buttonStyle(.plain)
            }
        }
        .padding(5)
        .background(.ultraThinMaterial, in: Capsule())
        .overlay(Capsule().strokeBorder(Color.linie, lineWidth: 0.5))
        .frame(maxWidth: 260)
        .padding(.bottom, 6)
    }
}
