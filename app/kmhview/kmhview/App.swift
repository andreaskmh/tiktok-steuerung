import SwiftUI

@main
struct KmhviewApp: App {
    @StateObject private var speicher = Speicher()
    @Environment(\.scenePhase) private var phase
    var body: some Scene {
        WindowGroup {
            Uebersicht().environmentObject(speicher)
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
