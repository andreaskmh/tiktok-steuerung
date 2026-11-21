import SwiftUI
import WebKit

/// Ranglisten-Seite (Research) vom Mac im WLAN – unverändert eingebettet (Seite/Server: werkzeuge/ranglisten_server.py, Artur 21.11.)
#if os(macOS)
let ranglistenAdressen = ["http://localhost:8080"]
#else
let ranglistenAdressen = ["http://MacBook-Pro-von-Andreas.local:8080", "http://192.168.8.214:8080"]
#endif

struct Ranglisten: View {
    var eingebettet = false   // in der Leiste unten: ohne Titelzeile und „Fertig“
    @Environment(\.dismiss) var weg
    @State private var nr = 0
    @State private var fehler = false
    @State private var neu = UUID()
    var body: some View {
        if eingebettet { inhalt } else {
            NavigationStack {
                inhalt
                    .navigationTitle("Research")
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

    var inhalt: some View {
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
                    .id("\(nr)\(neu)")
                    .ignoresSafeArea(edges: eingebettet ? .bottom : [])   // Seite läuft unter der durchsichtigen Leiste weiter
                }
            }
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
        let k = WKWebViewConfiguration()
        k.userContentController.addUserScript(WKUserScript(source: ranglistenAussehen, injectionTime: .atDocumentEnd, forMainFrameOnly: true))
        let w = WKWebView(frame: .zero, configuration: k); w.navigationDelegate = c.coordinator
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

/// Nur in der App: eigenes Aussehen über die Ranglisten-Seite legen (Seite/Server bleiben unverändert, Artur 21.11.).
/// Zeichen-Icons (▶ ☺ ▤ ★, 🌐 🎵, ✓) → saubere Vektor-Symbole in Verlaufskreisen wie in „Statistik“, Today/Yesterday → Heute/Gestern.
let ranglistenAussehen = #"""
(() => {
  const css = `
  .ic{width:30px!important;height:30px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 2px 8px rgba(0,0,0,.25)}
  .ic svg{width:15px;height:15px;display:block}
  .kt b{font-weight:700!important;letter-spacing:-.01em}
  .hk{width:24px!important;height:24px!important;border-width:1.5px!important;border-color:rgba(255,255,255,.22)!important}
  .hk[aria-pressed="true"]{font-size:0!important;border-color:rgba(255,255,255,.9)!important;background:rgba(255,255,255,.9) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 12.5l4 4L18.5 8' fill='none' stroke='%23000' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/15px no-repeat!important}
  .chip{display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,.08)!important;color:var(--mut)!important;font-weight:600!important}
  .chip.skript{color:var(--gelb)!important;background:rgba(255,210,63,.12)!important}
  .chip svg{width:11px;height:11px;flex:none}
  .alt{font-weight:600}
  body{padding-bottom:120px!important}
  details summary{list-style:none}details summary::-webkit-details-marker{display:none}
  details summary::before{content:"";display:inline-block;width:0;height:0;border-left:6px solid currentColor;border-top:4px solid transparent;border-bottom:4px solid transparent;margin-right:7px;transition:transform .15s}
  details[open] summary::before{transform:rotate(90deg)}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  const w = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"';
  const SYM = {
    "▶": `<svg ${w} fill="#fff"><path d="M8 5.6v12.8c0 .8.9 1.3 1.6.9l10.2-6.4c.6-.4.6-1.3 0-1.7L9.6 4.8C8.9 4.3 8 4.8 8 5.6z"/></svg>`,
    "☺": `<svg ${w} fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round"><circle cx="12" cy="12" r="8.3"/><path d="M8.6 14a4.3 4.3 0 0 0 6.8 0"/><path d="M9.3 9.6v.4M14.7 9.6v.4" stroke-width="2.8"/></svg>`,
    "▤": `<svg ${w} fill="#fff"><rect x="3.5" y="7.5" width="12.5" height="13" rx="2.6"/><path d="M8 4.5h9.5a3 3 0 0 1 3 3V17" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/></svg>`,
    "★": `<svg ${w} fill="#fff"><path d="M12 3.6l2.5 5.2 5.7.8-4.1 4 1 5.7L12 16.6l-5.1 2.7 1-5.7-4.1-4 5.7-.8z"/></svg>`
  };
  const KLEIN = {
    "🌐": `<svg ${w} fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/></svg>`,
    "🎵": `<svg ${w} fill="currentColor"><path d="M9 17.5V6.6l10-2.1v10.9" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="6.6" cy="17.6" r="2.6"/><circle cx="16.6" cy="15.4" r="2.6"/></svg>`
  };
  // Verläufe wie das App-Logo (BOF = Türkis→Blau statt Orange, Artur 21.11.)
  // schlicht wie die Symbole in „Statistik“: eine App-Farbe mit leichtem Verlauf (Artur 21.11.)
  const f = c => `linear-gradient(180deg,color-mix(in srgb,${c} 78%,#fff),${c})`;
  const FARBE = { "▶": f("#4C8DFF"), "☺": f("#FF5C9A"), "▤": f("#B57BFF"), "★": f("#FF9F2E") };
  const ALT = { Today: "Heute", Yesterday: "Gestern" };
  function fix() {
    document.querySelectorAll(".ic:not([data-k])").forEach(e => {
      const z = e.textContent.trim(), s = SYM[z]; if (s) e.innerHTML = s; e.dataset.k = 1;
      if (FARBE[z]) e.style.setProperty("background", FARBE[z], "important");
    });
    document.querySelectorAll(".chip:not([data-k])").forEach(c => {
      c.dataset.k = 1;
      for (const [z, s] of Object.entries(KLEIN)) if (c.textContent.includes(z)) { c.innerHTML = s + c.innerHTML.replace(z, "").trim(); c.classList.add("skript"); }
    });
    const h = document.querySelector("h1"); if (h && h.textContent.trim() === "Ranglisten") h.textContent = "Research";
    document.querySelectorAll(".alt").forEach(a => { const t = ALT[a.textContent.trim()]; if (t) a.textContent = t; });
  }
  fix(); new MutationObserver(fix).observe(document.body, { childList: true, subtree: true });
})();
"""#
