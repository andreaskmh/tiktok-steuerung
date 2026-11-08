#!/usr/bin/env python3
"""Echtes Drag & Drop mit der virtuellen Maus / dem Mini-Gerät.
Aufruf: python3 werkzeuge/ziehen.py <von_x> <von_y> <nach_x> <nach_y>   (Bildschirmpunkte)
Drückt bei (von), bewegt in kleinen Schritten und korrigiert anhand der echten Zeigerposition, lässt bei (nach) los.
"""
import subprocess, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "geraet"))
from geraet import Geraet

BIN = pathlib.Path(__file__).resolve().parent / "bin"

def pos():
    out = subprocess.run([str(BIN / "info")], capture_output=True, text=True).stdout
    z = [l for l in out.splitlines() if l.startswith("mouse")][0]
    x, y = z.split("(")[1].rstrip(")").split(",")
    return float(x), float(y)

def main(a):
    vx, vy, nx, ny = map(float, a)
    subprocess.run([str(BIN / "zeiger"), str(vx), str(vy)], capture_output=True)
    g = Geraet()
    try:
        g.befehl("MOVE 1 0"); g.befehl("MOVE -1 0"); time.sleep(0.2)
        print(g.befehl("PRESS L")); time.sleep(0.4)
        # erst ein paar Pixel ziehen, damit der Finder das Ziehen startet
        for _ in range(4):
            g.befehl("MOVE 3 0"); time.sleep(0.05)
        for _ in range(200):
            x, y = pos()
            dx, dy = nx - x, ny - y
            if abs(dx) < 4 and abs(dy) < 4:
                break
            sx = max(-12, min(12, int(dx / 3) or (1 if dx > 0 else -1 if dx < 0 else 0)))
            sy = max(-12, min(12, int(dy / 3) or (1 if dy > 0 else -1 if dy < 0 else 0)))
            g.befehl(f"MOVE {sx} {sy}"); time.sleep(0.02)
        time.sleep(float(__import__("os").environ.get("HALTEN", "0.6")))  # über dem Ziel kurz halten
        g.befehl("MOVE 1 0"); time.sleep(0.3)
        print("Position beim Loslassen:", pos())
        print(g.befehl("RELEASE L"))
    finally:
        g.befehl("RELEASE L"); g.close()

if __name__ == "__main__":
    main(sys.argv[1:])
