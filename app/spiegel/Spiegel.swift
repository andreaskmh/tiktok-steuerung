// iPhone Mirroring: zeigt iPhone-Bildschirme in eigenen Fenstern – nur zuschauen. Ein Fenster pro iPhone (⌘N).
// Bedienung wie Mirror My Phone: alles in der Menüleiste (Ablage, Optionen, Gerät, Fenster).
// Kabel: wie QuickTime / Mirror My Phone (CoreMediaIO gibt das iPhone als Kamera frei, AVFoundation zeigt es an).
// Ohne Kabel: Live-Bild des Kabel-Servers open-iphone-use (WLAN, http://127.0.0.1:27893), läuft eh für die Steuerung.
// Bauen: zsh app/spiegel/bauen.sh
import AppKit
import AVFoundation
import CoreMediaIO
import WebKit

let SERVER = URL(string: "http://127.0.0.1:27893/")!
let speicher = UserDefaults.standard
let ECKE: CGFloat = 0.12        // Bildschirm-Ecke, Anteil der Bildschirmbreite (iPhone 11 ≈ 0,10, iPhone 15 ≈ 0,14)

/// Gerät ▸ Rahmen: „rahmen“ = Geräterahmen, „form“ = nur Bildschirm in iPhone-Form, „fenster“ = normales Mac-Fenster
var DARSTELLUNG: String { speicher.string(forKey: "darstellung") ?? "rahmen" }
var RAND: CGFloat { DARSTELLUNG == "rahmen" ? 0.045 : 0 }     // Rahmenbreite, Anteil der Bildschirmbreite
let FARBEN: [(String, NSColor)] = [
    ("Schwarz Titan", NSColor(srgbRed: 0.24, green: 0.24, blue: 0.25, alpha: 1)),
    ("Weiß Titan", NSColor(srgbRed: 0.87, green: 0.86, blue: 0.84, alpha: 1)),
    ("Natur Titan", NSColor(srgbRed: 0.66, green: 0.64, blue: 0.60, alpha: 1)),
    ("Wüsten Titan", NSColor(srgbRed: 0.76, green: 0.66, blue: 0.56, alpha: 1)),
    ("Blau Titan", NSColor(srgbRed: 0.27, green: 0.31, blue: 0.38, alpha: 1)),
    ("Space Grau", NSColor(srgbRed: 0.36, green: 0.36, blue: 0.38, alpha: 1)),
    ("Silber", NSColor(srgbRed: 0.86, green: 0.87, blue: 0.88, alpha: 1)),
    ("Polarstern", NSColor(srgbRed: 0.93, green: 0.90, blue: 0.85, alpha: 1)),
    ("Blau", NSColor(srgbRed: 0.55, green: 0.70, blue: 0.90, alpha: 1)),
    ("Pink", NSColor(srgbRed: 0.95, green: 0.76, blue: 0.80, alpha: 1)),
    ("Rot", NSColor(srgbRed: 0.75, green: 0.10, blue: 0.15, alpha: 1)),
    ("Orange", NSColor(srgbRed: 0.95, green: 0.50, blue: 0.20, alpha: 1))]
var FARBE: NSColor { FARBEN.first { $0.0 == speicher.string(forKey: "farbe") }?.1 ?? FARBEN[0].1 }

/// Fenster, das auch ohne Titelleiste Tastatur-Fokus bekommt (⌘W, ⌘M, Esc).
final class SpiegelNSFenster: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
    override func cancelOperation(_ s: Any?) { (delegate as? SpiegelFenster)?.vollbildAus() }   // Esc
}

/// Liegt über dem Bild: Fenster lässt sich überall ziehen, Rechtsklick öffnet das Menü.
final class Deckel: NSView {
    // Nicht macOS verschieben lassen (dann bekommt die App den Klick nie und bleibt hinten → keine Menüs),
    // sondern Klick selbst nehmen: App nach vorn, dann überall ziehen.
    override var mouseDownCanMoveWindow: Bool { false }
    override func acceptsFirstMouse(for e: NSEvent?) -> Bool { true }
    override func mouseDown(with e: NSEvent) {
        NSRunningApplication.current.activate(from: NSWorkspace.shared.frontmostApplication ?? .current, options: [])
        NSApp.activate()
        window?.makeKeyAndOrderFront(nil)
        window?.performDrag(with: e)
    }
}

/// Livebild (WLAN) ohne Maus: Klicks gehen durch auf den Deckel, nie „Bild herausziehen“.
final class StummesWeb: WKWebView {
    override func hitTest(_ p: NSPoint) -> NSView? { nil }
}

/// Das gezeichnete iPhone: Metallband in der Rahmenfarbe, schwarzer Rand, Bildschirm mit iPhone-Ecken.
final class Geraet: NSView {
    let bildschirm = NSView()
    let vorschau: AVCaptureVideoPreviewLayer

    init(sitzung: AVCaptureSession) {
        vorschau = AVCaptureVideoPreviewLayer(session: sitzung)
        super.init(frame: .zero)
        wantsLayer = true
        layer!.cornerCurve = .continuous
        bildschirm.wantsLayer = true
        bildschirm.layer!.backgroundColor = NSColor(calibratedWhite: 0.11, alpha: 1).cgColor
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
        let ecke = DARSTELLUNG == "fenster" ? 0 : bildschirm.frame.width * ECKE
        bildschirm.layer!.cornerRadius = ecke
        layer!.cornerRadius = ecke + rand
        layer!.backgroundColor = rand > 0 ? NSColor(calibratedWhite: 0.02, alpha: 1).cgColor : nil
        layer!.borderColor = FARBE.cgColor
        layer!.borderWidth = rand * 0.32                   // Metallband
        CATransaction.begin(); CATransaction.setDisableActions(true)
        vorschau.frame = bildschirm.bounds
        CATransaction.commit()
        window?.invalidateShadow()
    }
}

struct Quelle: Equatable {
    let id: String, name: String
    var udid: String? = nil             // WLAN: UDID des iPhones (für iphonespiegel://geraet/<udid>)
    var kabel: AVCaptureDevice? = nil   // sonst: WLAN-Gerät des Servers (id = device_id)
}

// MARK: - App: Menüleiste, Fenster, Liste der iPhones

final class Spiegel: NSObject, NSApplicationDelegate, NSMenuDelegate {
    var fenster: [SpiegelFenster] = []
    var wlan: [Quelle] = []
    var ebene: String { speicher.string(forKey: "ebene") ?? "normal" }

    // viewKMH öffnet beim Datencheck das gerade bediente iPhone: iphonespiegel://geraet/<UDID>
    func applicationWillFinishLaunching(_ n: Notification) {
        NSAppleEventManager.shared().setEventHandler(self, andSelector: #selector(urlOeffnen(_:_:)),
                                                     forEventClass: AEEventClass(kInternetEventClass), andEventID: AEEventID(kAEGetURL))
    }

    @objc func urlOeffnen(_ e: NSAppleEventDescriptor, _ antwort: NSAppleEventDescriptor) {
        guard let s = e.paramDescriptor(forKeyword: keyDirectObject)?.stringValue, let u = URL(string: s),
              u.host == "geraet", let udid = u.pathComponents.last, udid.count > 8 else { return }
        zeige(udid: udid, versuche: 10)
    }

    /// Fenster mit diesem iPhone nach vorn holen, sonst neues Fenster dafür öffnen (WLAN-Liste lädt evtl. erst noch).
    func zeige(udid: String, versuche: Int) {
        let rein = { (x: String) in x.lowercased().replacingOccurrences(of: "-", with: "") }
        let ziel = quellen().first { $0.udid == udid || ($0.kabel != nil && rein($0.id).contains(rein(udid))) }
        guard let ziel else {
            if versuche > 0 { wlanHolen(); DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self.zeige(udid: udid, versuche: versuche - 1) } }
            return
        }
        if let f = fenster.first(where: { $0.aktiv?.id == ziel.id || $0.wahl == ziel.id }) {
            f.fenster.deminiaturize(nil); f.fenster.orderFront(nil)
        } else {
            oeffne(ziel.id)
        }
        NSApp.activate()
    }

    func applicationDidFinishLaunching(_ n: Notification) {
        var adr = CMIOObjectPropertyAddress(mSelector: CMIOObjectPropertySelector(kCMIOHardwarePropertyAllowScreenCaptureDevices),
                                            mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
                                            mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMain))
        var an: UInt32 = 1
        CMIOObjectSetPropertyData(CMIOObjectID(kCMIOObjectSystemObject), &adr, 0, nil, UInt32(MemoryLayout<UInt32>.size), &an)
        hauptmenue()

        // Fenster vom letzten Mal wiederherstellen ("" = automatisch das nächste freie iPhone).
        let alt = speicher.stringArray(forKey: "fenster") ?? [""]
        for wahl in alt.isEmpty ? [""] : alt { oeffne(wahl.isEmpty ? nil : wahl) }
        NSApp.activate()

        // Kabel-iPhones tauchen erst ein paar Sekunden nach der Freigabe auf (und nach jedem Einstecken).
        for name in [AVCaptureDevice.wasConnectedNotification, AVCaptureDevice.wasDisconnectedNotification] {
            NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { [weak self] _ in self?.alleVerbinden() }
        }
        AVCaptureDevice.requestAccess(for: .video) { _ in DispatchQueue.main.async { self.alleVerbinden() } }
        Timer.scheduledTimer(withTimeInterval: 3, repeats: true) { [weak self] _ in self?.wlanHolen() }
        wlanHolen()
    }

    // Menüleiste wie Mirror My Phone. Ablage/Optionen/Gerät werden beim Öffnen gebaut (aktuelle iPhones, Häkchen).
    func hauptmenue() {
        let leiste = NSMenu(), app = NSMenu()
        app.addItem(withTitle: "iPhone Mirroring ausblenden", action: #selector(NSApplication.hide), keyEquivalent: "h")
        app.addItem(withTitle: "Andere ausblenden", action: #selector(NSApplication.hideOtherApplications), keyEquivalent: "h")
            .keyEquivalentModifierMask = [.command, .option]
        app.addItem(.separator())
        app.addItem(withTitle: "iPhone Mirroring beenden", action: #selector(NSApplication.terminate), keyEquivalent: "q")
        leiste.addItem(withTitle: "", action: nil, keyEquivalent: "").submenu = app
        for titel in ["Ablage", "Optionen", "Gerät", "Fenster"] {
            let m = NSMenu(title: titel)
            m.delegate = self
            menuNeedsUpdate(m)                       // gleich füllen, damit Tastenkürzel sofort gehen
            leiste.addItem(withTitle: titel, action: nil, keyEquivalent: "").submenu = m
            if titel == "Fenster" { NSApp.windowsMenu = m }
        }
        NSApp.mainMenu = leiste
    }

    func menuNeedsUpdate(_ m: NSMenu) {
        m.removeAllItems()
        let f = vorderstes
        @discardableResult
        func eintrag(_ menue: NSMenu, _ titel: String, _ aktion: Selector?, ziel: AnyObject? = nil, an: Bool = false,
                     taste: String = "", mod: NSEvent.ModifierFlags = .command, wert: Any? = nil) -> NSMenuItem {
            let i = menue.addItem(withTitle: titel, action: aktion, keyEquivalent: taste)
            i.target = ziel ?? self; i.state = an ? .on : .off; i.keyEquivalentModifierMask = mod; i.representedObject = wert
            return i
        }
        func untermenue(_ titel: String) -> NSMenu {
            let u = NSMenu(title: titel)
            m.addItem(withTitle: titel, action: nil, keyEquivalent: "").submenu = u
            return u
        }
        switch m.title {
        case "Ablage":
            eintrag(m, "Neues Gerät", #selector(neuesFenster), taste: "n")
            eintrag(m, "Alle schließen", #selector(alleSchliessen), taste: "w", mod: [.command, .option])
        case "Optionen":
            eintrag(m, "Im Vordergrund fixieren", #selector(vordergrundUmschalten), an: ebene == "vorne", taste: "t")
            eintrag(m, "Auf dem Schreibtisch (hinter allem)", #selector(schreibtischUmschalten), an: ebene == "schreibtisch")
        case "Gerät":
            let rahmen = untermenue("Rahmen")
            for (titel, wert) in [("Geräterahmen", "rahmen"), ("Geräteform", "form"), ("Fenster", "fenster")] {
                eintrag(rahmen, titel, #selector(darstellungWaehlen), an: DARSTELLUNG == wert, wert: wert)
            }
            let farbe = untermenue("Farbe")
            let aktuell = speicher.string(forKey: "farbe") ?? FARBEN[0].0
            for (name, c) in FARBEN {
                let i = eintrag(farbe, name, #selector(farbeWaehlen), an: aktuell == name, wert: name)
                i.image = NSImage(size: NSSize(width: 12, height: 12), flipped: false) { r in
                    c.setFill(); NSBezierPath(ovalIn: r.insetBy(dx: 0.5, dy: 0.5)).fill()
                    NSColor.black.withAlphaComponent(0.25).setStroke(); NSBezierPath(ovalIn: r.insetBy(dx: 0.5, dy: 0.5)).stroke()
                    return true
                }
                i.isEnabled = DARSTELLUNG == "rahmen"
            }
            let groesse = untermenue("Größe")
            for (titel, wert) in [("Gerätegröße", "geraet"), ("Punkt für Punkt", "punkt"), ("Pixel für Pixel", "pixel"),
                                  ("An Bildschirm anpassen", "fuellen")] {
                eintrag(groesse, titel, #selector(SpiegelFenster.groesseWaehlen), ziel: f, wert: wert)
            }
            m.addItem(.separator())
            m.addItem(withTitle: "iPhone", action: nil, keyEquivalent: "")
            let alle = quellen()
            if alle.isEmpty { m.addItem(withTitle: "Kein iPhone verbunden", action: nil, keyEquivalent: "") }
            for (n, q) in alle.enumerated() {
                let i = eintrag(m, q.name, #selector(SpiegelFenster.quelleWaehlen), ziel: f, an: q.id == f?.aktiv?.id,
                                taste: n < 9 ? "\(n + 1)" : "", wert: q.id)
                i.indentationLevel = 1
            }
        case "Fenster":
            eintrag(m, "Minimieren", #selector(SpiegelFenster.minimieren), ziel: f, taste: "m")
            eintrag(m, "Füllen", #selector(SpiegelFenster.fuellen), ziel: f)
            eintrag(m, "Zentrieren", #selector(SpiegelFenster.zentrieren), ziel: f)
            m.addItem(.separator())
            eintrag(m, f?.istVollbild == true ? "Vollbild beenden" : "Vollbild", #selector(SpiegelFenster.vollbild), ziel: f,
                    taste: "f", mod: [.command, .control])
            m.addItem(.separator())
            eintrag(m, "Alle nach vorne bringen", #selector(NSApplication.arrangeInFront), ziel: NSApp)
            eintrag(m, "Schließen", #selector(SpiegelFenster.schliessen), ziel: f, taste: "w")
        default: break
        }
    }

    /// Das Fenster, auf das sich Menü-Befehle beziehen: das vorderste, sonst das zuletzt geöffnete.
    var vorderstes: SpiegelFenster? { (NSApp.keyWindow?.delegate as? SpiegelFenster) ?? fenster.last }

    @objc func vordergrundUmschalten() { setzeEbene(ebene == "vorne" ? "normal" : "vorne") }
    @objc func schreibtischUmschalten() { setzeEbene(ebene == "schreibtisch" ? "normal" : "schreibtisch") }
    @objc func darstellungWaehlen(_ s: NSMenuItem) {
        speicher.set(s.representedObject as? String, forKey: "darstellung")
        fenster.forEach { $0.darstellungAnwenden() }
    }
    @objc func farbeWaehlen(_ s: NSMenuItem) {
        speicher.set(s.representedObject as? String, forKey: "farbe")
        fenster.forEach { $0.geraet.needsLayout = true }
    }
    @objc func alleSchliessen() { NSApp.terminate(nil) }    // wie Mirror My Phone: alle zu = App zu; Fenster kommen beim Start wieder

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
                return Quelle(id: id, name: "\(d["name"] as? String ?? "iPhone") (WLAN)", udid: d["udid"] as? String)
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
    let fenster = SpiegelNSFenster(contentRect: NSRect(x: 200, y: 200, width: 320, height: 680),
                                   styleMask: [.borderless], backing: .buffered, defer: false)
    let sitzung = AVCaptureSession()
    let web = StummesWeb()
    let warten = NSStackView()                    // „Warte auf iPhone …“ wie bei Mirror My Phone
    let geraet: Geraet
    let leiste = NSVisualEffectView()            // Knopf-Pille über der Dynamic Island (Geräterahmen/-form)
    var pixel = NSSize(width: 1179, height: 2556) // Bildschirm in Pixeln (fürs Seitenverhältnis und die Größen)
    var verhaeltnis: NSLayoutConstraint!
    var abstand: [NSLayoutConstraint] = []
    var vorVollbild: NSRect?
    var istVollbild: Bool { vorVollbild != nil || fenster.styleMask.contains(.fullScreen) }

    init(app: Spiegel, nr: Int, wahl: String?) {
        self.app = app; self.nr = nr; self.wahl = wahl
        geraet = Geraet(sitzung: sitzung)
        super.init()
        let flaeche = NSView()
        flaeche.wantsLayer = true
        flaeche.addTrackingArea(NSTrackingArea(rect: .zero, options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect],
                                               owner: self, userInfo: nil))
        web.setValue(false, forKey: "drawsBackground")
        web.isHidden = true
        let symbol = NSImageView(image: NSImage(systemSymbolName: "iphone", accessibilityDescription: nil)!
            .withSymbolConfiguration(.init(pointSize: 44, weight: .ultraLight))!)
        symbol.contentTintColor = NSColor(calibratedWhite: 0.85, alpha: 1)
        let text = NSTextField(labelWithString: "Warte auf iPhone …")
        text.textColor = NSColor(calibratedWhite: 0.85, alpha: 1)
        text.font = .systemFont(ofSize: 13)
        warten.orientation = .vertical
        warten.spacing = 10
        warten.addArrangedSubview(symbol)
        warten.addArrangedSubview(text)
        for v in [web, warten] as [NSView] {
            v.translatesAutoresizingMaskIntoConstraints = false
            geraet.bildschirm.addSubview(v)
        }
        let deckel = Deckel()
        deckel.menu = NSMenu()
        deckel.menu!.delegate = self

        // Ampel-Knöpfe für die randlosen Darstellungen: echte macOS-Knöpfe in einer Milchglas-Pille
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
            deckel.topAnchor.constraint(equalTo: flaeche.topAnchor), deckel.bottomAnchor.constraint(equalTo: flaeche.bottomAnchor),
            deckel.leadingAnchor.constraint(equalTo: flaeche.leadingAnchor), deckel.trailingAnchor.constraint(equalTo: flaeche.trailingAnchor),
            leiste.centerXAnchor.constraint(equalTo: geraet.centerXAnchor),
            leiste.topAnchor.constraint(equalTo: geraet.bildschirm.topAnchor),
            leiste.heightAnchor.constraint(equalToConstant: 26),
            reihe.centerXAnchor.constraint(equalTo: leiste.centerXAnchor), reihe.centerYAnchor.constraint(equalTo: leiste.centerYAnchor),
            leiste.widthAnchor.constraint(equalTo: reihe.widthAnchor, constant: 22),
            warten.centerXAnchor.constraint(equalTo: geraet.bildschirm.centerXAnchor),
            warten.centerYAnchor.constraint(equalTo: geraet.bildschirm.centerYAnchor),
            web.topAnchor.constraint(equalTo: geraet.bildschirm.topAnchor),
            web.bottomAnchor.constraint(equalTo: geraet.bildschirm.bottomAnchor),
            web.leadingAnchor.constraint(equalTo: geraet.bildschirm.leadingAnchor),
            web.trailingAnchor.constraint(equalTo: geraet.bildschirm.trailingAnchor)])

        fenster.contentView = flaeche
        fenster.delegate = self
        fenster.isReleasedWhenClosed = false
        fenster.hasShadow = true
        fenster.isMovableByWindowBackground = false   // Ziehen macht der Deckel selbst
        fenster.minSize = NSSize(width: 160, height: 330)
        darstellungAnwenden()
        let name = nr == 0 ? "Spiegel" : "Spiegel-\(nr)"
        if !fenster.setFrameUsingName(name),
           let rechts = app.fenster.map({ $0.fenster.frame }).max(by: { $0.maxX < $1.maxX }) {
            // neues Fenster gleich groß rechts neben das letzte
            fenster.setFrame(NSRect(x: rechts.maxX + 20, y: rechts.minY, width: rechts.width, height: rechts.height), display: false)
        }
        fenster.setFrameAutosaveName(name)
        fenster.makeKeyAndOrderFront(nil)
    }

    /// Gerät ▸ Rahmen anwenden. „fenster“ = normales Mac-Fenster mit Titelleiste (wie Mirror My Phone „Window“),
    /// sonst randlos und durchsichtig, nur das gezeichnete iPhone ist zu sehen.
    func darstellungAnwenden() {
        guard !istVollbild else { return }
        let alsFenster = DARSTELLUNG == "fenster"
        let rahmen = fenster.frame
        fenster.styleMask = alsFenster ? [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView]
                                       : [.borderless, .closable, .miniaturizable, .resizable]
        fenster.titlebarAppearsTransparent = true
        fenster.titleVisibility = .hidden
        fenster.isOpaque = alsFenster
        fenster.backgroundColor = alsFenster ? NSColor(calibratedWhite: 0.11, alpha: 1) : .clear
        fenster.collectionBehavior = alsFenster ? [.fullScreenPrimary] : []
        leiste.isHidden = alsFenster
        fenster.setFrame(rahmen, display: false)
        geraet.needsLayout = true
        seitenverhaeltnis()
        ebeneAnwenden()
    }

    // Objective-C-Namen ausdrücklich: ohne sie heißt die Methode „mouseEnteredWith:“ und die Maus-Meldung kommt nie an.
    @objc(mouseEntered:) func mouseEntered(with e: NSEvent) { leiste.animator().alphaValue = 1 }
    @objc(mouseExited:) func mouseExited(with e: NSEvent) { leiste.animator().alphaValue = 0 }

    @objc func schliessen() { fenster.close() }
    @objc func minimieren() { fenster.miniaturize(nil) }
    @objc func zentrieren() { fenster.center() }
    @objc func fuellen() { groesse(hoehe: (fenster.screen ?? NSScreen.main!).visibleFrame.height); zentrieren() }

    /// Gerät ▸ Größe
    @objc func groesseWaehlen(_ s: NSMenuItem) {
        let skala: CGFloat = pixel.width >= 1000 ? 3 : 2           // iPhone mit Dynamic Island/Pro: 3×, iPhone 11/XR: 2×
        switch s.representedObject as? String {
        case "punkt": groesse(hoehe: pixel.height / skala)
        case "pixel": groesse(hoehe: pixel.height / (fenster.screen?.backingScaleFactor ?? 2))
        case "geraet":
            // echte Größe: iPhone-Bildschirm in mm (Pixel / ppi) auf dem Mac-Bildschirm in mm abbilden
            let ppi: CGFloat = skala == 3 ? 460 : 326
            let mm = pixel.height / ppi * 25.4
            let schirm = fenster.screen ?? NSScreen.main!
            let id = schirm.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? CGDirectDisplayID ?? CGMainDisplayID()
            let schirmMm = CGDisplayScreenSize(id).height
            groesse(hoehe: schirmMm > 0 ? mm * schirm.frame.height / schirmMm : pixel.height / skala)
        default: fuellen()
        }
    }

    /// Fenster so groß, dass der iPhone-Bildschirm „hoehe“ Punkte hoch ist (Rahmen kommt dazu).
    func groesse(hoehe: CGFloat) {
        guard !istVollbild else { return }
        let g = geraetGroesse
        let h = min(hoehe * g.height / pixel.height, (fenster.screen ?? NSScreen.main!).visibleFrame.height)
        var f = fenster.frame
        let mitte = NSPoint(x: f.midX, y: f.maxY)
        f.size = NSSize(width: (h * g.width / g.height).rounded(), height: h.rounded())
        f.origin = NSPoint(x: mitte.x - f.width / 2, y: mitte.y - f.height)
        fenster.setFrame(f, display: true, animate: true)
    }

    @objc func vollbild() {
        if DARSTELLUNG == "fenster" { return fenster.toggleFullScreen(nil) }     // echtes macOS-Vollbild
        if vorVollbild != nil { return vollbildAus() }
        guard let schirm = fenster.screen else { return }
        vorVollbild = fenster.frame
        NSApp.presentationOptions = [.autoHideMenuBar, .autoHideDock]
        fenster.backgroundColor = .black
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
        fenster.isMovable = true
        abstand.forEach { $0.constant = 0 }
        fenster.setFrame(alt, display: true, animate: true)
        darstellungAnwenden()
    }

    // macOS-Vollbild (Darstellung „Fenster“): iPhone mittig auf Schwarz
    func windowWillEnterFullScreen(_ n: Notification) { fenster.backgroundColor = .black; abstand.forEach { $0.constant = -48 } }
    func windowDidExitFullScreen(_ n: Notification) { abstand.forEach { $0.constant = 0 }; darstellungAnwenden() }

    func windowWillClose(_ n: Notification) {
        vollbildAus()
        sitzung.stopRunning()
        web.loadHTMLString("", baseURL: nil)
        app.geschlossen(self)
    }

    func ebeneAnwenden() {
        guard !istVollbild else { return }
        // „schreibtisch“: liegt hinter allen Fenstern direkt über dem Hintergrundbild, wie ein Widget.
        let e = app.ebene
        fenster.level = e == "vorne" ? .floating
            : e == "schreibtisch" ? NSWindow.Level(Int(CGWindowLevelForKey(.desktopIconWindow)) - 1) : .normal
    }

    /// Größe des ganzen Geräts (Bildschirm + Rahmen) in Bildschirm-Pixeln
    var geraetGroesse: NSSize { NSSize(width: pixel.width * (1 + 2 * RAND), height: pixel.height + 2 * RAND * pixel.width) }

    /// Form des gezeichneten iPhones und des Fensters an Bildschirmformat und Rahmen anpassen.
    func seitenverhaeltnis(_ neu: NSSize? = nil) {
        if let neu { pixel = neu }
        let g = geraetGroesse
        verhaeltnis.isActive = false
        verhaeltnis = geraet.widthAnchor.constraint(equalTo: geraet.heightAnchor, multiplier: g.width / g.height)
        verhaeltnis.isActive = true
        guard !istVollbild else { return }
        fenster.contentAspectRatio = g
        var f = fenster.frame
        f.size.width = (f.height * g.width / g.height).rounded()
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
        warten.isHidden = ziel != nil
        guard let ziel else { return }
        if let quelle = ziel.kabel {
            guard let eingang = try? AVCaptureDeviceInput(device: quelle), sitzung.canAddInput(eingang) else { return }
            sitzung.addInput(eingang)
            let d = CMVideoFormatDescriptionGetDimensions(quelle.activeFormat.formatDescription)
            if d.width > 0, d.height > 0 { seitenverhaeltnis(NSSize(width: Int(d.width), height: Int(d.height))) }
            DispatchQueue.global().async { self.sitzung.startRunning() }
        } else {
            pixelGroesseHolen(ziel.id)
            web.loadHTMLString("""
                <body style="margin:0;background:#000;overflow:hidden;pointer-events:none;-webkit-user-select:none">
                <img draggable="false" src="api/devices/\(ziel.id)/stream"
                     style="width:100vw;height:100vh;object-fit:cover;-webkit-user-drag:none;pointer-events:none"
                     onerror="setTimeout(()=>{this.src=this.src},1000)">
                """, baseURL: SERVER)
        }
    }

    /// Echte Bildgröße des WLAN-iPhones aus dem PNG-Kopf (Breite/Höhe stehen in Byte 16–23).
    func pixelGroesseHolen(_ id: String) {
        URLSession.shared.dataTask(with: SERVER.appendingPathComponent("api/devices/\(id)/png")) { d, _, _ in
            guard let d, d.count > 24 else { return }
            let zahl = { (i: Int) in d[i..<i + 4].reduce(0) { $0 << 8 | Int($1) } }
            let (b, h) = (zahl(16), zahl(20))
            if b > 0, h > 0 { DispatchQueue.main.async { self.seitenverhaeltnis(NSSize(width: b, height: h)) } }
        }.resume()
    }

    @objc func quelleWaehlen(_ s: NSMenuItem) {
        wahl = s.representedObject as? String
        app.merken()
        aktiv = nil
        verbinde()
    }

    func menuNeedsUpdate(_ m: NSMenu) {           // Rechtsklick: dieselben Punkte wie Gerät + Fenster
        m.removeAllItems()
        for q in app.quellen() {
            let i = m.addItem(withTitle: q.name, action: #selector(quelleWaehlen), keyEquivalent: "")
            i.target = self; i.representedObject = q.id; i.state = q.id == aktiv?.id ? .on : .off
        }
        m.addItem(.separator())
        let vorne = m.addItem(withTitle: "Im Vordergrund fixieren", action: #selector(Spiegel.vordergrundUmschalten), keyEquivalent: "")
        vorne.target = app; vorne.state = app.ebene == "vorne" ? .on : .off
        m.addItem(withTitle: "Neues Gerät", action: #selector(Spiegel.neuesFenster), keyEquivalent: "").target = app
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
