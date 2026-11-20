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

/// Kurz der Schriftzug auf Schwarz beim Öffnen (wie bei Revolut), dann die App
struct StartBild<C: View>: View {
    @ViewBuilder let inhalt: C
    @State private var weg = false
    var body: some View {
        ZStack {
            inhalt
            if !weg {
                ZStack {
                    Color.black.ignoresSafeArea()
                    Text("statsKMH").font(.system(size: 52, weight: .semibold)).tracking(-1.5).foregroundStyle(.white)
                }
                .transition(.opacity)
            }
        }
        .task { try? await Task.sleep(for: .seconds(0.9)); withAnimation(.easeOut(duration: 0.35)) { weg = true } }
    }
}
