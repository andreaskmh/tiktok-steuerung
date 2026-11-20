import SwiftUI

@main
struct KmhviewApp: App {
    @StateObject private var speicher = Speicher()
    @Environment(\.scenePhase) private var phase
    var body: some Scene {
        WindowGroup {
            StartBild { Uebersicht().environmentObject(speicher) }
                .onChange(of: phase) { _, p in if p == .active { speicher.laden() } }
                #if os(macOS)
                .frame(minWidth: 420, idealWidth: 520, minHeight: 640)
                #endif
        }
        #if os(macOS)
        .defaultSize(width: 560, height: 900)
        .commands { CommandGroup(after: .newItem) { Button("Neu laden") { speicher.laden() }.keyboardShortcut("r") } }
        #endif
    }
}

/// Startbild: gleicher Hintergrund wie der Systemstart (StartFarbe) → kein Flackern; Logo federt rein, Schriftzug gleitet nach,
/// dann zoomt das Logo groß und blendet in die App über (Artur 20.11.: „flüssiger, moderner“)
struct StartBild<C: View>: View {
    @ViewBuilder let inhalt: C
    @State private var schritt = 0   // 0 = Start, 1 = Logo da, 2 = weg
    var body: some View {
        ZStack {
            inhalt
                .scaleEffect(schritt >= 2 ? 1 : 0.94).opacity(schritt >= 2 ? 1 : 0)
            if schritt < 3 {
                ZStack {
                    Color("StartFarbe").ignoresSafeArea()
                    HStack(spacing: 14) {
                        Image("Logo").resizable().frame(width: 64, height: 64)
                            .scaleEffect(schritt == 0 ? 0.5 : schritt == 2 ? 1.6 : 1)
                        HStack(spacing: 0) {
                            Text("stats").fontWeight(.regular).foregroundStyle(.secondary)
                            Text("KMH").fontWeight(.heavy)
                        }
                        .font(.system(size: 38)).tracking(-0.8)
                        .offset(x: schritt == 0 ? -16 : 0).opacity(schritt == 1 ? 1 : 0)
                    }
                    .opacity(schritt == 0 ? 0 : 1)
                }
                .opacity(schritt == 2 ? 0 : 1)
                .allowsHitTesting(schritt < 2)
            }
        }
        .task {
            withAnimation(.spring(response: 0.45, dampingFraction: 0.72)) { schritt = 1 }
            try? await Task.sleep(for: .seconds(0.85))
            withAnimation(.easeInOut(duration: 0.4)) { schritt = 2 }
            try? await Task.sleep(for: .seconds(0.45))
            schritt = 3
        }
    }
}
