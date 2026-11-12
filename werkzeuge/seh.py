#!/usr/bin/env python3
"""Sehen ohne Claude: iPhone-Fenster aufnehmen + Texterkennung (bin/text, ~0,3 s).

  python3 werkzeuge/seh.py                 # alle Texte mit Fensterpunkten ausgeben
  python3 werkzeuge/seh.py "Hinzufügen"    # nur Treffer (Teilstring, Groß/klein egal)
Im Skript: import seh; seh.lesen() -> [(text, x, y)], seh.finde("…") -> (x, y) oder None,
seh.warte("…", sek) wartet, bis der Text auftaucht. Koordinaten = Punkte wie tap.py (334 x 735, Kabel und Synchronisierung gleich). Kabel wird automatisch genommen, wenn open-iphone-use läuft (kabel.py).
"""
import os, subprocess, sys, tempfile, time, pathlib

BIN = pathlib.Path(__file__).resolve().parent / "bin"
TMP = tempfile.mkdtemp(prefix="seh-")


def fenster():
    out = subprocess.run([str(BIN / "fenster")], capture_output=True, text=True).stdout.split()
    i, x, y, w, h = map(int, out[:5])
    return i, w, h


_KABEL = None


def kabel():
    """Kabel-Steuerung aktiv? (open-iphone-use läuft, iPhone liefert Bild) – einmal pro Lauf geprüft."""
    global _KABEL
    if _KABEL is None:
        import kabel as K
        _KABEL = K if K.aktiv() else False
    return _KABEL


def aufnahme(p):
    """Bild vom iPhone nach p (Kabel: verlustfreies Stream-Bild, sonst Fenster der iPhone-Synchronisierung)."""
    K = kabel()
    if K:
        K.foto(p)
        return BREITE, K.hoehe()
    wid, w, h = fenster()
    subprocess.run(["screencapture", "-x", "-o", "-l", str(wid), p], check=True)
    return w, h


BREITE = 334.0


def lesen():
    p = os.path.join(TMP, "f.png")
    w, h = aufnahme(p)
    out = subprocess.run([str(BIN / "text"), p], capture_output=True, text=True).stdout
    res = []
    for z in out.splitlines():
        kopf, _, t = z.partition("\t")
        nx, ny, _, _ = map(float, kopf.split())
        res.append((t, nx * w, ny * h))
    return res


def alle(muster, texte=None, genau=False):
    m = muster.lower()
    texte = lesen() if texte is None else texte
    return [(t, x, y) for t, x, y in texte if (t.lower().strip() == m if genau else m in t.lower())]


def finde(muster, texte=None, genau=False, unter=None, ueber=None):
    for t, x, y in alle(muster, texte, genau):
        if (unter is None or y > unter) and (ueber is None or y < ueber):
            return x, y
    return None


def aehnlich(muster, texte=None, schwelle=0.85):
    """Wie finde, aber tolerant gegen einzelne Lesefehler (z. B. „aut“ statt „auf“) → (x, y) oder None."""
    import difflib
    m = muster.lower().strip()
    texte = lesen() if texte is None else texte
    best = None
    for t, x, y in texte:
        t2 = t.lower().strip().rstrip("x×").strip()
        for kand in (t2, t2[:len(m)]):
            r = difflib.SequenceMatcher(None, m, kand).ratio()
            if r >= schwelle and (best is None or r > best[0]):
                best = (r, x, y)
    return best and (best[1], best[2])


def warte(muster, sek=6.0, genau=False, unter=None, ueber=None):
    ende = time.time() + sek
    while True:
        f = finde(muster, genau=genau, unter=unter, ueber=ueber)
        if f or time.time() > ende:
            return f
        time.sleep(0.3)


if __name__ == "__main__":
    tx = lesen()
    for t, x, y in (alle(sys.argv[1], tx) if len(sys.argv) > 1 else tx):
        print(f"{x:5.0f} {y:5.0f}  {t}")
