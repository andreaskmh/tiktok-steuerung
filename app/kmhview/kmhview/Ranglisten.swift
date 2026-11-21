import SwiftUI
import WebKit

/// Ranglisten-Seite (Research) vom Mac im WLAN – unverändert eingebettet (Seite/Server: werkzeuge/ranglisten_server.py, Artur 21.11.)
#if os(macOS)
let ranglistenAdressen = ["http://localhost:8080"]
#else
let ranglistenAdressen = ["http://MacBook-Pro-von-Andreas.local:8080", "http://192.168.8.214:8080"]
#endif

struct Ranglisten: View {
    @Environment(\.dismiss) var weg
    @State private var nr = 0
    @State private var fehler = false
    @State private var neu = UUID()
    var body: some View {
        NavigationStack {
            ZStack {
                Color("StartFarbe").ignoresSafeArea()
                if fehler {
                    ContentUnavailableView {
                        Label("Ranglisten nicht erreichbar", systemImage: "wifi.exclamationmark")
                    } description: {
                        Text("Die Seite kommt vom Mac. Mac an und im selben WLAN?")
                    } actions: {
                        Button("Nochmal") { nr = 0; fehler = false; neu = UUID() }.buttonStyle(.borderedProminent)
                    }
                } else {
                    WebSeite(url: URL(string: ranglistenAdressen[nr])!) {   // Adresse geht nicht → nächste, dann Hinweis
                        if nr + 1 < ranglistenAdressen.count { nr += 1 } else { fehler = true }
                    }
                    .id("\(nr)\(neu)").ignoresSafeArea(edges: .bottom)
                }
            }
            .navigationTitle("Ranglisten")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Fertig") { weg() } }
                ToolbarItem(placement: .cancellationAction) { Button { neu = UUID() } label: { Image(systemName: "arrow.clockwise") } }
            }
        }
        #if os(macOS)
        .frame(minWidth: 520, minHeight: 760)
        #endif
    }
}

#if os(iOS)
typealias WebBasis = UIViewRepresentable
#else
typealias WebBasis = NSViewRepresentable
#endif

struct WebSeite: WebBasis {
    let url: URL; let beiFehler: () -> Void
    func makeCoordinator() -> Helfer { Helfer(beiFehler) }
    final class Helfer: NSObject, WKNavigationDelegate {
        let beiFehler: () -> Void
        init(_ f: @escaping () -> Void) { beiFehler = f }
        func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) { DispatchQueue.main.async(execute: beiFehler) }
        // TikTok-Links in der Seite: in TikTok/Browser öffnen statt in der kleinen Ansicht
        func webView(_ w: WKWebView, decidePolicyFor a: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if let u = a.request.url, a.navigationType == .linkActivated || a.targetFrame == nil, !["localhost", "192.168.8.214", "macbook-pro-von-andreas.local"].contains(u.host?.lowercased() ?? "") {
                #if os(iOS)
                UIApplication.shared.open(u)
                #else
                NSWorkspace.shared.open(u)
                #endif
                return decisionHandler(.cancel)
            }
            decisionHandler(.allow)
        }
    }
    func neu(_ c: Context) -> WKWebView {
        let w = WKWebView(); w.navigationDelegate = c.coordinator
        #if os(iOS)
        w.isOpaque = false; w.backgroundColor = .clear
        #endif
        w.load(URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 8))
        return w
    }
    #if os(iOS)
    func makeUIView(context: Context) -> WKWebView { neu(context) }
    func updateUIView(_ v: WKWebView, context: Context) {}
    #else
    func makeNSView(context: Context) -> WKWebView { neu(context) }
    func updateNSView(_ v: WKWebView, context: Context) {}
    #endif
}
