"""Baut faelle.json aus roh.json: je verschiedenem Bildschirm (OCR-Text) ein Fall mit Soll-Bildschirm.
Soll = Erkennung zum Zeitpunkt des Bauens, von Hand durchgesehen (15.11.2026, Claude) + HAND-Korrekturen unten.
Nur neu bauen, wenn neue Bildschirmfotos dazukommen – danach Soll-Liste wieder durchsehen!"""
import json, pathlib, sys
H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent.parent))
import bildschirm as B

HAND = {   # Datei-Anfang → Soll (von Hand am Bild geprüft)
    "20261112-164314": B.LIVE,            # TikTok schließt sich, LIVE-Event-Bereich offen
    "20261115-145050": B.PRODUKTSEITE,    # Produktblatt über Shop-Reiter („nicht vorrätig“)
    "20261115-175225": B.DLG_OK,          # Gesamtlikes-Popup über dem Profil
    "20261113-165602": B.DLG_UPLOAD,      # „Du lädst momentan ein Video hoch“
    "20261113-233345": B.VARIANTEN,       # Varianten-Blatt More („Bitte auswählen“)
    "20261113-162733": B.VORSCHAU,        # Galerie-Vorschau, „Auswählen“ oben rechts
    "20261115-152413": B.BEITRAG,         # Beitrag mit offener Tastatur („Beklagte“ = Auto-Korrektur)
    "20261115-165341": B.BEITRAG,
    "20261115-164615": B.LIVE,            # „What Live do you want to watch?“
    "20261113-164615": B.LIVE,
    "20261115-145557": B.LIVE,
    "20261115-163708": B.LIVE,            # LIVE-Stream offen
    "20261112-214404": B.TEILEN,
    "20261113-232805": B.DLG_VERSTANDEN,  # „Produkt nicht verfügbar … OK, verstanden“
    "20261115-154857": B.TIKTOK_SONST,    # Entwürfe-Liste
}

roh = json.loads((H / "roh.json").read_text())
faelle, gesehen = [], set()
for k, tx in roh.items():
    sig = " | ".join(t for t, _, _ in tx)
    if sig in gesehen:
        continue
    gesehen.add(sig)
    soll = next((v for h, v in HAND.items() if k.startswith(h)), None) or B.erkenne(tx)
    faelle.append({"datei": k, "soll": soll, "hand": any(k.startswith(h) for h in HAND), "tx": tx})
(H / "faelle.json").write_text(json.dumps(faelle, ensure_ascii=False, indent=0))
print(len(faelle), "Fälle")
