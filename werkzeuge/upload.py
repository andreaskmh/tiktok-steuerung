#!/usr/bin/env python3
"""Feste Upload-Abschnitte am Stück (virtuelle Maus über tap.py). Texte tippt Claude danach selbst.

  python3 werkzeuge/upload.py start <kachel_x> <kachel_y>
      + → „Kamera nicht verfügbar“ OK → Galerie → Video-Kachel → Weiter (Vorschau) → Weiter (Editor) → Zeiger sicher.
      Danach IMMER Foto prüfen: Beitragsseite? (Veröffentlichen liegt dort, wo Weiter war!)
  python3 werkzeuge/upload.py link <hinzufuegen_y> [ok]
      Link hinzufügen → Produkt → (ok = Hinweis „OK, verstanden“ wegtippen) → „Hinzufügen“ in der Showcase-Zeile
      → Seite „Produkt umbenennen“ → ins Feld tippen. Danach sofort Rücktaste + Text (Claude).
  python3 werkzeuge/upload.py publish        Veröffentlichen → Zeiger sicher.
  python3 werkzeuge/upload.py like <kachel_x> <kachel_y>
      Profil → Video-Reiter → Kachel → Herz → Lesezeichen → zurück.
Koordinaten = Fensterpunkte wie in app_screenshot (334 x 735).
"""
import sys, pathlib, subprocess
T = [sys.executable, str(pathlib.Path(__file__).resolve().parent / "tap.py")]

def tap(*a):
    subprocess.run(T + [str(x) for x in a], check=True)

def main(a):
    cmd = a[0]
    if cmd == "start":
        kx, ky = a[1], a[2]
        tap(167, 681, "w1.6", 167, 433, "w0.8", 30, 672, "w1.5", kx, ky, "w1.3", 242, 680, "w2.2", 242, 680, "safe", "w2.5")
    elif cmd == "link":
        y = a[1]
        seq = [110, 428, "w1.2", 90, 520, "w2.2"]
        if len(a) > 2 and a[2] == "ok":
            seq += [167, 672, "w1.2"]
        seq += [282, y, "w1.8", 280, 345, "w0.3"]
        tap(*seq)
    elif cmd == "publish":
        tap(242, 680, "safe", "w2.5")
    elif cmd == "like":
        kx, ky = a[1], a[2]
        tap(306, 681, "w1.5", 36, 320, "w1.2", kx, ky, "w1.3", 302, 387, "w0.5", 302, 490, "w0.5", 23, 92, "w0.8")
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
