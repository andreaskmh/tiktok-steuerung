#!/usr/bin/env python3
"""Ganzer Upload in 3 Abschnitten – Claude schaut nur zwischen den Abschnitten kurz aufs Foto.

  A)  python3 werkzeuge/post.py a <kachel_x> <kachel_y>
        + → Kamera-OK → Galerie → Video → Weiter → Weiter → Link hinzufügen → Produkt (→ Showcase-Liste)
        [Foto: richtige Zeile suchen]
  B)  python3 werkzeuge/post.py b <hinzufuegen_y> "<Button-Text>" "<Beschreibung>" "<Brand-Suche>"
        Hinzufügen → Feld aktiv → löschen → Button-Text (langsam) → Hinzufügen → Beschreibung (langsam)
        → @ Erwähnung → Suche (langsam)
        [Foto: Brand-Zeile suchen, Text prüfen]
  C)  python3 werkzeuge/post.py c <brand_y>
        Brand wählen → Veröffentlichen → Profil → neuestes Video → liken + speichern → zurück
Tippen wie ein Mensch: Zeichen einzeln über die Tastatur (System Events), 70–260 ms Abstand,
ab und zu eine längere Pause. Emojis gehen so nicht – Beschreibung ohne Emojis.
"""
import random, subprocess, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tap as T

def taps(*a):
    T.main([str(x) for x in a])

def front():
    subprocess.run(["open", "-b", "com.apple.ScreenContinuity"]); time.sleep(0.25)

def key(code, n=1):
    front()
    subprocess.run(["osascript", "-e",
        f'tell application "System Events" to repeat {n} times\nkey code {code}\ndelay 0.03\nend repeat'])

def tippe(text):
    front()
    for ch in text:
        esc = ch.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{esc}"'])
        time.sleep(random.uniform(0.07, 0.26) + (random.uniform(0.3, 0.7) if random.random() < 0.06 else 0))

def main(a):
    if a[0] == "a":
        kx, ky = a[1], a[2]
        taps(167, 681, "w1.8", 167, 433, "w0.8", 30, 672, "w1.6", kx, ky, "w1.4",
             242, 680, "w2.3", 242, 680, "safe", "w3.5", 110, 428, "w1.3", 90, 520, "w2.3")
    elif a[0] == "b":
        y, button, text, brand = a[1], a[2], a[3], a[4]
        taps(282, y, "w2.0", 280, 328, "w0.3")
        key(51, 32)                      # Rücktaste ×32
        tippe(button)
        taps(167, 678, "w2.2", 110, 128, "w0.4")
        tippe(text)
        time.sleep(0.6)
        taps(176, 264, "w1.3", 160, 166, "w0.4")
        tippe(brand)
        time.sleep(1.8)
    elif a[0] == "c":
        y = a[1]
        taps(120, y, "w1.4", 242, 680, "safe", "w3.0",
             306, 681, "w1.6", 36, 320, "w1.3", 54, 480, "w1.4", 302, 387, "w0.5", 302, 490, "w0.5", 23, 92, "w0.8")
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
