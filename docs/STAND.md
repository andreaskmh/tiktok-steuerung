# Stand & nächste Schritte (zuletzt 08.11.2026, 22:05)

**Zuerst lesen:** `CLAUDE.md` → `docs/ABLAUF.md` (Upload-Ablauf + Zeiger-Regel) → `docs/ACCOUNTS.md` (Verteilung, Button-Texte).

## Was läuft
- iPhone 11 über iPhone-Synchronisierung, Bedienung per Computer-Use (`app_*`, Bundle `com.apple.ScreenContinuity`).
- Virtuelle Maus `vmaus` (Karabiner-Treiber) ist eingerichtet, Dienste starten automatisch. `python3 geraet/geraet.py STATUS`.
- Videos aufs iPhone: Fotos-App am iPhone öffnen, `werkzeuge/ziehen.py` (Datei am **Namen** greifen).
- Produkt ins Showcase: Safari am iPhone → `social1.ai/products/<id>` → View on TikTok Shop → Provisions-Badge →
  Zum Showcase hinzufügen. **Pro Account.** Social1-Liste am Mac im eingebauten Browser (angemeldet).
- Erledigt: Schokoellsen → artur.official, Powerbank → anduri.official (Log: `uebergabe/ausgang/posts-2026-11-08.json`).
- andreas.testet ist für den 08.11. voll.

## Bekannte Stolpersteine
- **Erster Tipp landet am alten Zeiger** → vor jedem Tipp `app_scroll` (dy 0) ans Ziel; nach Tipps unten rechts
  Zeiger sofort nach oben. Sonst Gefahr: versehentlich „Veröffentlichen“.
- Claude-Fenster liegt oft über dem iPhone-Fenster → für die virtuelle Maus vorher `open -b com.apple.ScreenContinuity`.
- **Feld „Produktname“** reagiert nicht auf unsere Tipps → bisher tippt Artur einmal mit dem Trackpad rein.
  Nächster Schritt: Klick mit Touch-Kennung nachbauen (CGEvent-Feld 7 = 3, Druck 255, Feld 108 = 1;
  Aufnahme-Werkzeug `werkzeuge/test/rec2.swift`), per `postToPid` an die iPhone-Synchronisierung schicken.
- Brand-@: bei mehreren Accounts mit Logo unsicher (Powerbank → `@voltiva_de` geschätzt) – Artur fragen bzw. Shop-Profil prüfen.
- Video-Feed: roter Promote-Balken „… Aufrufe für … €“ nie antippen.

## Nächste Uploads
Artur schickt Videos + Social1-Liste. Plan (Video → Account, Text, Hashtags, Brand) einmal zeigen, nach „passt“ ohne
weitere Rückfrage posten; 2–3 Min Abstand; Account komplett abarbeiten, dann wechseln; danach liken, speichern,
Profil neu laden und orangenen Button prüfen.
