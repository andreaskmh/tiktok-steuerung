import SwiftUI

@main
struct ProvisionApp: App {
    @StateObject private var speicher = Speicher()
    @Environment(\.scenePhase) private var phase
    var body: some Scene {
        WindowGroup {
            Uebersicht().environmentObject(speicher)
                .onChange(of: phase) { _, p in if p == .active { speicher.laden() } }
        }
    }
}
