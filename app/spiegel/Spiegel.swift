// iPhone-Spiegel: zeigt iPhone-Bildschirme in eigenen Fenstern – nur zuschauen. Ein Fenster pro iPhone (⌘N).
// Kabel: wie QuickTime / Mirror My Phone (CoreMediaIO gibt das iPhone als Kamera frei, AVFoundation zeigt es an).
// Ohne Kabel: Live-Bild des Kabel-Servers open-iphone-use (WLAN, http://127.0.0.1:27893), läuft eh für die Steuerung.
// Bauen: zsh app/spiegel/bauen.sh
import AppKit
import AVFoundation
import CoreMediaIO
import WebKit

let SERVER = URL(string: "http://127.0.0.1:27893/")!
let speicher = UserDefaults.standard

/// Klicks landen hier statt im Bild: Fenster lässt sich überall ziehen, Rechtsklick öffnet das Menü.
final class Deckel: NSView {
    override var mouseDownCanMoveWindow: Bool { true }
}

struct Quelle: Equatable {
    let id: String, name: String
    var kabel: AVCaptureDevice? = nil   // sonst: WLAN-Gerät des Servers (id = device_id)
}

// MARK: - App: verwaltet die Fenster und die Liste der iPhones

final class Spiegel: NSObject, NSApplicationDelegate {
    var fenster: [SpiegelFenster] = []
    var wlan: [Quelle] = []
    var ebene: String { speicher.string(forKey: "ebene") ?? "vorne" }

    func applicationDidFinishLaunching(_ n: Notification) {
        var adr = CMIOObjectPropertyAddress(mSelector: CMIOObjectPropertySelector(kCMIOHardwarePropertyAllowScreenCaptureDevices),
                                            mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
                                            mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMain))
        var an: UInt32 = 1
        CMIOObjectSetPropertyData(CMIOObjectID(kCMIOObjectSystemObject), &adr, 0, nil, UInt32(MemoryLayout<UInt32>.size), &an)
        hauptmenue()

        // Fenster vom letzten Mal wiederherstellen ("" = automatisch das nächste freie iPhone).
        let alt = speicher.stringArray(forKey: "fenster") ?? [speicher.string(forKey: "geraet") ?? ""]
        for wahl in alt.isEmpty ? [""] : alt { oeffne(wahl.isEmpty ? nil : wahl) }
        NSApp.activate(ignoringOtherApps: true)

        // Kabel-iPhones tauchen erst ein paar Sekunden nach der Freigabe auf (und nach jedem Einstecken).
        for name in [AVCaptureDevice.wasConnectedNotification, AVCaptureDevice.wasDisconnectedNotification] {
            NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { [weak self] _ in self?.alleVerbinden() }
        }
        AVCaptureDevice.requestAccess(for: .video) { _ in DispatchQueue.main.async { self.alleVerbinden() } }
        Timer.scheduledTimer(withTimeInterval: 3, repeats: true) { [weak self] _ in self?.wlanHolen() }
        wlanHolen()
    }

    func hauptmenue() {                               // ⌘Q, ⌘H, ⌘N, ⌘M, ⌘W
        let leiste = NSMenu(), app = NSMenu(), ablage = NSMenu(title: "Ablage"), fenst = NSMenu(title: "Fenster")
        app.addItem(withTitle: "iPhone-Spiegel ausblenden", action: #selector(NSApplication.hide), keyEquivalent: "h")
        app.addItem(withTitle: "iPhone-Spiegel beenden", action: #selector(NSApplication.terminate), keyEquivalent: "q")
        ablage.addItem(withTitle: "Neues Fenster (weiteres iPhone)", action: #selector(neuesFenster), keyEquivalent: "n").target = self
        fenst.addItem(withTitle: "Minimieren", action: #selector(NSWindow.performMiniaturize), keyEquivalent: "m")
        fenst.addItem(withTitle: "Schließen", action: #selector(NSWindow.performClose), keyEquivalent: "w")
        for m in [app, ablage, fenst] { leiste.addItem(withTitle: m.title, action: nil, keyEquivalent: "").submenu = m }
        NSApp.mainMenu = leiste
        NSApp.windowsMenu = fenst
    }

    // Letztes Fenster zu = App zu; Klick aufs Dock-Symbol holt minimierte Fenster zurück.
    func applicationShouldTerminateAfterLastWindowClosed(_ s: NSApplication) -> Bool { true }
    func applicationShouldHandleReopen(_ s: NSApplication, hasVisibleWindows: Bool) -> Bool {
        for f in fenster { f.fenster.deminiaturize(nil); f.fenster.orderFront(nil) }
        return true
    }

    func oeffne(_ wahl: String?) {
        // Nummer = erste freie, damit jedes Fenster seine Position behält.
        let nr = (0...).first { n in !fenster.contains { $0.nr == n } }!
        let f = SpiegelFenster(app: self, nr: nr, wahl: wahl)
        fenster.append(f)
        f.verbinde()
        merken()
    }

    @objc func neuesFenster() { oeffne(nil) }

    func geschlossen(_ f: SpiegelFenster) {
        guard fenster.count > 1 else { return }       // letztes Fenster: Liste behalten → beim nächsten Start alle wieder da
        fenster.removeAll { $0 === f }
        merken()
    }

    func merken() { speicher.set(fenster.map { $0.wahl ?? "" }, forKey: "fenster") }

    func setzeEbene(_ e: String) {
        speicher.set(e, forKey: "ebene")
        fenster.forEach { $0.ebeneAnwenden() }
    }

    func quellen() -> [Quelle] {
        let kabel = AVCaptureDevice.DiscoverySession(deviceTypes: [.external], mediaType: .muxed, position: .unspecified).devices
        return kabel.map { Quelle(id: $0.uniqueID, name: "\($0.localizedName) (Kabel)", kabel: $0) } + wlan
    }

    func wlanHolen() {
        URLSession.shared.dataTask(with: SERVER.appendingPathComponent("api/devices")) { daten, _, _ in
            let liste = (daten.flatMap { try? JSONSerialization.jsonObject(with: $0) } as? [[String: Any]]) ?? []
            let neu = liste.compactMap { d -> Quelle? in
                guard d["frame_id"] is String, let id = d["device_id"] as? String else { return nil }
                return Quelle(id: id, name: "\(d["name"] as? String ?? "iPhone") (WLAN-Server)")
            }
            DispatchQueue.main.async { if neu != self.wlan { self.wlan = neu }; self.alleVerbinden() }
        }.resume()
    }

    func alleVerbinden() { fenster.forEach { $0.verbinde() } }
}

// MARK: - Ein Fenster = ein iPhone

final class SpiegelFenster: NSObject, NSWindowDelegate, NSMenuDelegate {
    unowned let app: Spiegel
    let nr: Int
    var wahl: String?                  // fest gewähltes iPhone; nil = automatisch das nächste freie
    var aktiv: Quelle?
    let fenster = NSWindow(contentRect: NSRect(x: 200, y: 200, width: 300, height: 650),
                           styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
                           backing: .buffered, defer: false)
    let sitzung = AVCaptureSession()
    let web = WKWebView()
    let hinweis = NSTextField(labelWithString: "iPhone anstecken oder\nKabel-Server starten …")

    init(app: Spiegel, nr: Int, wahl: String?) {
        self.app = app; self.nr = nr; self.wahl = wahl
        super.init()
        let ansicht = NSView()
        ansicht.wantsLayer = true
        ansicht.layer!.backgroundColor = NSColor.black.cgColor
        ansicht.layer!.cornerRadius = 28
        ansicht.layer!.masksToBounds = true
        let vorschau = AVCaptureVideoPreviewLayer(session: sitzung)
        vorschau.videoGravity = .resizeAspect
        vorschau.frame = ansicht.bounds
        vorschau.autoresizingMask = [.layerWidthSizable, .layerHeightSizable]
        ansicht.layer!.addSublayer(vorschau)
        web.setValue(false, forKey: "drawsBackground")
        web.isHidden = true
        hinweis.alignment = .center
        hinweis.textColor = .lightGray
        let deckel = Deckel()
        deckel.menu = NSMenu()
        deckel.menu!.delegate = self
        deckel.addTrackingArea(NSTrackingArea(rect: .zero, options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect],
                                              owner: self, userInfo: nil))
        for v in [web, hinweis, deckel] as [NSView] {
            v.translatesAutoresizingMaskIntoConstraints = false
            ansicht.addSubview(v)
        }
        NSLayoutConstraint.activate([hinweis.centerXAnchor.constraint(equalTo: ansicht.centerXAnchor),
                                     hinweis.centerYAnchor.constraint(equalTo: ansicht.centerYAnchor)]
            + [web, deckel].flatMap { [$0.topAnchor.constraint(equalTo: ansicht.topAnchor),
                                       $0.bottomAnchor.constraint(equalTo: ansicht.bottomAnchor),
                                       $0.leadingAnchor.constraint(equalTo: ansicht.leadingAnchor),
                                       $0.trailingAnchor.constraint(equalTo: ansicht.trailingAnchor)] })

        fenster.contentView = ansicht
        fenster.delegate = self
        fenster.isReleasedWhenClosed = false
        fenster.titleVisibility = .hidden
        fenster.titlebarAppearsTransparent = true
        fenster.backgroundColor = .clear
        fenster.isOpaque = false
        fenster.hasShadow = true
        fenster.isMovableByWindowBackground = true
        let name = nr == 0 ? "Spiegel" : "Spiegel-\(nr)"         // 0 = Position aus der Ein-Fenster-Fassung
        if !fenster.setFrameUsingName(name),
           let rechts = app.fenster.map({ $0.fenster.frame }).max(by: { $0.maxX < $1.maxX }) {
            // neues Fenster gleich groß rechts neben das letzte
            fenster.setFrame(NSRect(x: rechts.maxX + 20, y: rechts.minY, width: rechts.width, height: rechts.height), display: false)
        }
        fenster.setFrameAutosaveName(name)
        ebeneAnwenden()
        knoepfe(0)       // Schließen/Minimieren/Vergrößern nur bei Maus über dem Fenster (sonst verdecken sie die Uhr)
        fenster.makeKeyAndOrderFront(nil)
    }

    func knoepfe(_ alpha: CGFloat) {
        for k in [NSWindow.ButtonType.closeButton, .miniaturizeButton, .zoomButton] {
            fenster.standardWindowButton(k)?.animator().alphaValue = alpha
        }
    }
    // Objective-C-Namen ausdrücklich: ohne sie heißt die Methode „mouseEnteredWith:“ und die Maus-Meldung kommt nie an.
    @objc(mouseEntered:) func mouseEntered(with e: NSEvent) { knoepfe(1) }
    @objc(mouseExited:) func mouseExited(with e: NSEvent) { knoepfe(0) }

    func windowWillClose(_ n: Notification) {
        sitzung.stopRunning()
        web.loadHTMLString("", baseURL: nil)
        app.geschlossen(self)
    }

    func ebeneAnwenden() {
        // „schreibtisch“: liegt hinter allen Fenstern direkt über dem Hintergrundbild, wie ein Widget.
        let e = app.ebene
        fenster.level = e == "vorne" ? .floating
            : e == "schreibtisch" ? NSWindow.Level(Int(CGWindowLevelForKey(.desktopIconWindow)) - 1) : .normal
    }

    func seitenverhaeltnis(_ b: Int32, _ h: Int32) {
        fenster.contentAspectRatio = NSSize(width: Int(b), height: Int(h))
        var f = fenster.frame
        f.size.width = f.height * CGFloat(b) / CGFloat(h)
        fenster.setFrame(f, display: true)
    }

    func verbinde() {
        let alle = app.quellen()
        let belegt = Set(app.fenster.filter { $0 !== self }.compactMap { $0.aktiv?.id })
        // Gewähltes iPhone; sonst das erste, das noch kein anderes Fenster zeigt (Kabel vor WLAN, schärfer).
        let ziel = alle.first { $0.id == wahl } ?? (wahl == nil ? alle.first { !belegt.contains($0.id) } : nil)
        if ziel == aktiv { return }
        aktiv = ziel
        sitzung.stopRunning()
        sitzung.inputs.forEach(sitzung.removeInput)
        web.loadHTMLString("", baseURL: nil)
        web.isHidden = ziel?.kabel != nil || ziel == nil
        hinweis.isHidden = ziel != nil
        guard let ziel else { return }
        if let geraet = ziel.kabel {
            guard let eingang = try? AVCaptureDeviceInput(device: geraet), sitzung.canAddInput(eingang) else { return }
            sitzung.addInput(eingang)
            let d = CMVideoFormatDescriptionGetDimensions(geraet.activeFormat.formatDescription)
            if d.width > 0, d.height > 0 { seitenverhaeltnis(d.width, d.height) }
            DispatchQueue.global().async { self.sitzung.startRunning() }
        } else {
            // shortcut: festes iPhone-Format 9:19,5 (iPhone X bis 17), bei iPad/iPhone SE echte Bildgröße auslesen.
            seitenverhaeltnis(9, 19)
            web.loadHTMLString("""
                <body style="margin:0;background:#000;overflow:hidden">
                <img src="api/devices/\(ziel.id)/stream" style="width:100vw;height:100vh;object-fit:contain"
                     onerror="setTimeout(()=>{this.src=this.src},1000)">
                """, baseURL: SERVER)
        }
    }

    @objc func ebeneWaehlen(_ s: NSMenuItem) { app.setzeEbene(s.representedObject as! String) }
    @objc func quelleWaehlen(_ s: NSMenuItem) {
        wahl = s.representedObject as? String
        app.merken()
        aktiv = nil
        verbinde()
    }

    func menuNeedsUpdate(_ m: NSMenu) {           // Rechtsklick-Menü
        m.removeAllItems()
        for q in app.quellen() {
            let i = m.addItem(withTitle: q.name, action: #selector(quelleWaehlen), keyEquivalent: "")
            i.target = self; i.representedObject = q.id; i.state = q.id == aktiv?.id ? .on : .off
        }
        m.addItem(withTitle: "Neues Fenster (weiteres iPhone)", action: #selector(Spiegel.neuesFenster), keyEquivalent: "n").target = app
        m.addItem(.separator())
        for (titel, wert) in [("Immer im Vordergrund", "vorne"), ("Normales Fenster", "normal"), ("Auf dem Schreibtisch (hinter allem)", "schreibtisch")] {
            let i = m.addItem(withTitle: titel, action: #selector(ebeneWaehlen), keyEquivalent: "")
            i.target = self; i.representedObject = wert; i.state = app.ebene == wert ? .on : .off
        }
        m.addItem(.separator())
        m.addItem(withTitle: "Minimieren", action: #selector(NSWindow.performMiniaturize), keyEquivalent: "m").target = fenster
        m.addItem(withTitle: "Schließen", action: #selector(NSWindow.performClose), keyEquivalent: "w").target = fenster
    }
}

let app = NSApplication.shared
let spiegel = Spiegel()
app.delegate = spiegel
app.setActivationPolicy(.regular)
app.run()
