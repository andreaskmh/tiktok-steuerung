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
let RAND: CGFloat = 0.04        // iPhone-Rahmen, Anteil der Bildschirmbreite
let ECKE: CGFloat = 0.12        // Bildschirm-Ecke, Anteil der Bildschirmbreite (iPhone 11 ≈ 0,10, iPhone 15 ≈ 0,14)

/// Randloses Fenster, das trotzdem Tastatur-Fokus bekommt (⌘W, ⌘M, Esc).
final class RandlosFenster: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
    override func cancelOperation(_ s: Any?) { (delegate as? SpiegelFenster)?.vollbildAus() }   // Esc
}

/// Klicks landen hier statt im Bild: Fenster lässt sich überall ziehen, Rechtsklick öffnet das Menü.
final class Deckel: NSView {
    override var mouseDownCanMoveWindow: Bool { true }
    override func acceptsFirstMouse(for e: NSEvent?) -> Bool { true }       // auch im Hintergrund sofort ziehen
    override func mouseDown(with e: NSEvent) { window?.performDrag(with: e) }  // ausdrücklich verschieben, nie Bild herausziehen
}

/// Livebild (WLAN) ohne Maus: Klicks gehen durch auf den Deckel.
final class StummesWeb: WKWebView {
    override func hitTest(_ p: NSPoint) -> NSView? { nil }
}

/// Das gezeichnete iPhone: schmaler dunkler Rahmen mit feiner Kante, darin der Bildschirm mit iPhone-Ecken.
final class Geraet: NSView {
    let bildschirm = NSView()
    let vorschau: AVCaptureVideoPreviewLayer

    init(sitzung: AVCaptureSession) {
        vorschau = AVCaptureVideoPreviewLayer(session: sitzung)
        super.init(frame: .zero)
        wantsLayer = true
        layer!.backgroundColor = NSColor(calibratedWhite: 0.07, alpha: 1).cgColor
        layer!.borderColor = NSColor(calibratedWhite: 0.38, alpha: 1).cgColor     // Metallkante
        layer!.cornerCurve = .continuous
        bildschirm.wantsLayer = true
        bildschirm.layer!.backgroundColor = NSColor.black.cgColor
        bildschirm.layer!.cornerCurve = .continuous
        bildschirm.layer!.masksToBounds = true
        vorschau.videoGravity = .resizeAspectFill
        bildschirm.layer!.addSublayer(vorschau)
        addSubview(bildschirm)
    }
    required init?(coder: NSCoder) { nil }

    override func layout() {
        super.layout()
        let rand = bounds.width * RAND / (1 + 2 * RAND)
        bildschirm.frame = bounds.insetBy(dx: rand, dy: rand)
        let ecke = bildschirm.frame.width * ECKE
        bildschirm.layer!.cornerRadius = ecke
        layer!.cornerRadius = ecke + rand
        layer!.borderWidth = max(1, rand * 0.18)
        CATransaction.begin(); CATransaction.setDisableActions(true)
        vorschau.frame = bildschirm.bounds
        CATransaction.commit()
        window?.invalidateShadow()
    }
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

    func hauptmenue() {          // Fenster-Befehle ohne Ziel: gehen an das vorderste Spiegel-Fenster
        let leiste = NSMenu(), app = NSMenu(), ablage = NSMenu(title: "Ablage"), fenst = NSMenu(title: "Fenster")
        app.addItem(withTitle: "iPhone-Spiegel ausblenden", action: #selector(NSApplication.hide), keyEquivalent: "h")
        app.addItem(withTitle: "iPhone-Spiegel beenden", action: #selector(NSApplication.terminate), keyEquivalent: "q")
        ablage.addItem(withTitle: "Neues Fenster (weiteres iPhone)", action: #selector(neuesFenster), keyEquivalent: "n").target = self
        fenst.addItem(withTitle: "Minimieren", action: #selector(SpiegelFenster.minimieren), keyEquivalent: "m")
        fenst.addItem(withTitle: "Vollbild", action: #selector(SpiegelFenster.vollbild), keyEquivalent: "f")
            .keyEquivalentModifierMask = [.command, .control]
        fenst.addItem(withTitle: "Schließen", action: #selector(SpiegelFenster.schliessen), keyEquivalent: "w")
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
                return Quelle(id: id, name: "\(d["name"] as? String ?? "iPhone") (WLAN)")
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
    let fenster = RandlosFenster(contentRect: NSRect(x: 200, y: 200, width: 320, height: 680),
                                 styleMask: [.borderless, .resizable, .miniaturizable, .closable],
                                 backing: .buffered, defer: false)
    let sitzung = AVCaptureSession()
    let web = StummesWeb()
    let hinweis = NSTextField(labelWithString: "iPhone anstecken oder\nKabel-Server starten …")
    let geraet: Geraet
    let leiste = NSVisualEffectView()            // Knopf-Pille über der Dynamic Island
    var format = NSSize(width: 9, height: 19.5)   // Bildschirm-Seitenverhältnis
    var verhaeltnis: NSLayoutConstraint!
    var abstand: [NSLayoutConstraint] = []
    var vorVollbild: NSRect?

    init(app: Spiegel, nr: Int, wahl: String?) {
        self.app = app; self.nr = nr; self.wahl = wahl
        geraet = Geraet(sitzung: sitzung)
        super.init()
        let flaeche = NSView()                  // Fensterinhalt: durchsichtig, im Vollbild schwarz
        flaeche.wantsLayer = true
        flaeche.addTrackingArea(NSTrackingArea(rect: .zero, options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect],
                                               owner: self, userInfo: nil))
        web.setValue(false, forKey: "drawsBackground")
        web.isHidden = true
        hinweis.alignment = .center
        hinweis.textColor = .secondaryLabelColor
        hinweis.font = .systemFont(ofSize: 13, weight: .medium)
        for v in [web, hinweis] as [NSView] {
            v.translatesAutoresizingMaskIntoConstraints = false
            geraet.bildschirm.addSubview(v)
        }
        let deckel = Deckel()
        deckel.menu = NSMenu()
        deckel.menu!.delegate = self

        // Knöpfe: echte macOS-Ampel, in einer Milchglas-Pille
        leiste.material = .hudWindow
        leiste.blendingMode = .withinWindow
        leiste.state = .active
        leiste.wantsLayer = true
        leiste.layer!.cornerRadius = 13
        leiste.alphaValue = 0
        let knoepfe = [(NSWindow.ButtonType.closeButton, #selector(schliessen)),
                       (.miniaturizeButton, #selector(minimieren)), (.zoomButton, #selector(vollbild))]
            .compactMap { typ, aktion -> NSButton? in
                let k = NSWindow.standardWindowButton(typ, for: [.titled, .closable, .miniaturizable, .resizable])
                k?.target = self; k?.action = aktion
                return k
            }
        let reihe = NSStackView(views: knoepfe)
        reihe.spacing = 8
        reihe.translatesAutoresizingMaskIntoConstraints = false
        leiste.addSubview(reihe)

        for v in [geraet, deckel, leiste] as [NSView] {
            v.translatesAutoresizingMaskIntoConstraints = false
            flaeche.addSubview(v)
        }
        verhaeltnis = geraet.widthAnchor.constraint(equalTo: geraet.heightAnchor, multiplier: 9 / 19.5)
        abstand = [geraet.heightAnchor.constraint(lessThanOrEqualTo: flaeche.heightAnchor),
                   geraet.widthAnchor.constraint(lessThanOrEqualTo: flaeche.widthAnchor),
                   geraet.heightAnchor.constraint(equalTo: flaeche.heightAnchor)]
        abstand[2].priority = .defaultHigh          // so groß wie möglich, Seitenverhältnis bleibt
        NSLayoutConstraint.activate(abstand + [verhaeltnis,
            geraet.centerXAnchor.constraint(equalTo: flaeche.centerXAnchor),
            geraet.centerYAnchor.constraint(equalTo: flaeche.centerYAnchor),
            deckel.topAnchor.constraint(equalTo: geraet.topAnchor), deckel.bottomAnchor.constraint(equalTo: geraet.bottomAnchor),
            deckel.leadingAnchor.constraint(equalTo: geraet.leadingAnchor), deckel.trailingAnchor.constraint(equalTo: geraet.trailingAnchor),
            leiste.centerXAnchor.constraint(equalTo: geraet.centerXAnchor),
            leiste.topAnchor.constraint(equalTo: geraet.bildschirm.topAnchor, constant: 0),
            leiste.heightAnchor.constraint(equalToConstant: 26),
            reihe.centerXAnchor.constraint(equalTo: leiste.centerXAnchor), reihe.centerYAnchor.constraint(equalTo: leiste.centerYAnchor),
            leiste.widthAnchor.constraint(equalTo: reihe.widthAnchor, constant: 22),
            hinweis.centerXAnchor.constraint(equalTo: geraet.bildschirm.centerXAnchor),
            hinweis.centerYAnchor.constraint(equalTo: geraet.bildschirm.centerYAnchor)]
            + [web.topAnchor.constraint(equalTo: geraet.bildschirm.topAnchor),
               web.bottomAnchor.constraint(equalTo: geraet.bildschirm.bottomAnchor),
               web.leadingAnchor.constraint(equalTo: geraet.bildschirm.leadingAnchor),
               web.trailingAnchor.constraint(equalTo: geraet.bildschirm.trailingAnchor)])

        fenster.contentView = flaeche
        fenster.delegate = self
        fenster.isReleasedWhenClosed = false
        fenster.backgroundColor = .clear
        fenster.isOpaque = false
        fenster.hasShadow = true
        fenster.isMovableByWindowBackground = true
        fenster.minSize = NSSize(width: 160, height: 330)
        let name = nr == 0 ? "Spiegel" : "Spiegel-\(nr)"         // 0 = Position aus der Ein-Fenster-Fassung
        if !fenster.setFrameUsingName(name),
           let rechts = app.fenster.map({ $0.fenster.frame }).max(by: { $0.maxX < $1.maxX }) {
            // neues Fenster gleich groß rechts neben das letzte
            fenster.setFrame(NSRect(x: rechts.maxX + 20, y: rechts.minY, width: rechts.width, height: rechts.height), display: false)
        }
        fenster.setFrameAutosaveName(name)
        ebeneAnwenden()
        fenster.makeKeyAndOrderFront(nil)
    }

    // Objective-C-Namen ausdrücklich: ohne sie heißt die Methode „mouseEnteredWith:“ und die Maus-Meldung kommt nie an.
    @objc(mouseEntered:) func mouseEntered(with e: NSEvent) { leiste.animator().alphaValue = 1 }
    @objc(mouseExited:) func mouseExited(with e: NSEvent) { leiste.animator().alphaValue = 0 }

    @objc func schliessen() { fenster.close() }
    @objc func minimieren() { fenster.miniaturize(nil) }

    @objc func vollbild() {
        if vorVollbild != nil { return vollbildAus() }
        guard let schirm = fenster.screen else { return }
        vorVollbild = fenster.frame
        NSApp.presentationOptions = [.autoHideMenuBar, .autoHideDock]
        fenster.contentView!.layer!.backgroundColor = NSColor.black.cgColor
        fenster.contentAspectRatio = .zero
        fenster.isMovable = false
        fenster.level = .floating
        abstand.forEach { $0.constant = -48 }       // etwas Luft um das iPhone
        fenster.setFrame(schirm.frame, display: true, animate: true)
    }

    func vollbildAus() {
        guard let alt = vorVollbild else { return }
        vorVollbild = nil
        NSApp.presentationOptions = []
        fenster.contentView!.layer!.backgroundColor = nil
        fenster.isMovable = true
        abstand.forEach { $0.constant = 0 }
        fenster.setFrame(alt, display: true, animate: true)
        seitenverhaeltnis(format)
        ebeneAnwenden()
    }

    func windowWillClose(_ n: Notification) {
        vollbildAus()
        sitzung.stopRunning()
        web.loadHTMLString("", baseURL: nil)
        app.geschlossen(self)
    }

    func ebeneAnwenden() {
        guard vorVollbild == nil else { return }
        // „schreibtisch“: liegt hinter allen Fenstern direkt über dem Hintergrundbild, wie ein Widget.
        let e = app.ebene
        fenster.level = e == "vorne" ? .floating
            : e == "schreibtisch" ? NSWindow.Level(Int(CGWindowLevelForKey(.desktopIconWindow)) - 1) : .normal
    }

    /// Bildschirmformat → Form des gezeichneten iPhones und des Fensters.
    func seitenverhaeltnis(_ bild: NSSize) {
        format = bild
        let geraetGroesse = NSSize(width: bild.width * (1 + 2 * RAND), height: bild.height + 2 * RAND * bild.width)
        verhaeltnis.isActive = false
        verhaeltnis = geraet.widthAnchor.constraint(equalTo: geraet.heightAnchor,
                                                    multiplier: geraetGroesse.width / geraetGroesse.height)
        verhaeltnis.isActive = true
        guard vorVollbild == nil else { return }
        fenster.contentAspectRatio = geraetGroesse
        var f = fenster.frame
        f.size.width = (f.height * geraetGroesse.width / geraetGroesse.height).rounded()
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
        guard let ziel else { return seitenverhaeltnis(NSSize(width: 9, height: 19.5)) }
        if let quelle = ziel.kabel {
            guard let eingang = try? AVCaptureDeviceInput(device: quelle), sitzung.canAddInput(eingang) else { return }
            sitzung.addInput(eingang)
            let d = CMVideoFormatDescriptionGetDimensions(quelle.activeFormat.formatDescription)
            if d.width > 0, d.height > 0 { seitenverhaeltnis(NSSize(width: Int(d.width), height: Int(d.height))) }
            DispatchQueue.global().async { self.sitzung.startRunning() }
        } else {
            // shortcut: festes iPhone-Format 9:19,5 (iPhone X bis 17), bei iPad/iPhone SE echte Bildgröße auslesen.
            seitenverhaeltnis(NSSize(width: 9, height: 19.5))
            web.loadHTMLString("""
                <body style="margin:0;background:#000;overflow:hidden;pointer-events:none;-webkit-user-select:none">
                <img draggable="false" src="api/devices/\(ziel.id)/stream"
                     style="width:100vw;height:100vh;object-fit:cover;-webkit-user-drag:none;pointer-events:none"
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
        for (titel, aktion) in [("Vollbild", #selector(vollbild)), ("Minimieren", #selector(minimieren)), ("Schließen", #selector(schliessen))] {
            m.addItem(withTitle: titel, action: aktion, keyEquivalent: "").target = self
        }
    }
}

let app = NSApplication.shared
let spiegel = Spiegel()
app.delegate = spiegel
app.setActivationPolicy(.regular)
app.run()
