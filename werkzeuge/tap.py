#!/usr/bin/env python3
"""Schnelle, verlässliche Tipps im iPhone-Fenster mit der virtuellen Maus (echtes Gerät).

Aufruf (Koordinaten wie in app_screenshot: Fensterpunkte, 0..334 x 0..735):
  python3 werkzeuge/tap.py 302 387              # ein Tipp
  python3 werkzeuge/tap.py 302 387 w0.8 302 490 # Tipp, 0,8 s warten, Tipp
  python3 werkzeuge/tap.py safe                 # Zeiger an sichere Stelle (oben Mitte), kein Klick
Vor jedem Tipp: Zeiger hinsetzen + kleine echte Bewegung (weckt das Fenster, setzt den iPhone-Zeiger),
dann CLICK. Danach bleibt der Zeiger stehen – unten rechts ggf. 'safe' anhängen.
"""
import subprocess, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "geraet"))
from geraet import Geraet

BIN = pathlib.Path(__file__).resolve().parent / "bin"

def fenster():
    out = subprocess.run([str(BIN / "fenster")], capture_output=True, text=True).stdout.split()
    _, x, y, w, h = map(float, out[:5])
    return x, y, w, h

def main(args):
    subprocess.run(["open", "-b", "com.apple.ScreenContinuity"])
    time.sleep(0.25)
    fx, fy, fw, fh = fenster()
    g = Geraet()
    try:
        i = 0
        while i < len(args):
            a = args[i]
            if a.startswith("w"):
                time.sleep(float(a[1:])); i += 1; continue
            if a == "safe":
                px, py, klick = fw / 2, 60, False; i += 1
            else:
                px, py, klick = float(a), float(args[i + 1]), True; i += 2
            subprocess.run([str(BIN / "zeiger"), str(fx + px), str(fy + py)], capture_output=True)
            g.befehl("MOVE 2 0"); time.sleep(0.04); g.befehl("MOVE -2 0"); time.sleep(0.12)
            if klick:
                g.befehl("CLICK"); time.sleep(0.15)
    finally:
        g.close()

if __name__ == "__main__":
    main(sys.argv[1:])
