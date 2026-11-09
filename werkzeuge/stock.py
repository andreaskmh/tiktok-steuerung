#!/usr/bin/env python3
"""Stock-Bilder eines TikTok-Shop-Produkts vollautomatisch holen (über Social1, nie über die TikTok-Suche).

  python3 werkzeuge/stock.py <produkt-id> <ordnername> ["Produktname"] [zielordner]

Ablauf am iPhone: Home → Safari → social1.ai/products/<id> → „View on TikTok Shop“ → Produktbild antippen
→ Vollbild-Galerie → galerie.sh holt alle Bilder nach uebergabe/ausgang/<ordnername>/.
Mit [zielordner] (z. B. „…/Editing System 1.1/Videos/Video 140/Belege/<produkt>“) werden die Bilder zusätzlich
dorthin kopiert. Bei Unklarem: STOPP, nichts blind antippen (nie in die Nähe von Kasse/Jetzt kaufen/Einkaufswagen).
"""
import pathlib, shutil, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh
from posten import taps, schnell, key, Stopp, muss, log

PROJ = HIER.parent
GEFAHR = ("kasse", "jetzt kaufen", "einkaufswagen", "kaufen")


def home():
    subprocess.run(["osascript", "-e", 'tell application "System Events" to tell (first process whose bundle identifier '
                    'is "com.apple.ScreenContinuity") to click menu item "Home-Bildschirm" of menu "Darstellung" of menu bar 1'],
                   capture_output=True)
    time.sleep(1.0)


def sicher_tippen(x, y, abstand=45):
    """Nur tippen, wenn kein Kauf-Knopf in der Nähe steht."""
    for t, tx, ty in seh.lesen():
        if abs(ty - y) < abstand and any(g in t.lower() for g in GEFAHR):
            raise Stopp(f"„{t}“ liegt zu nah am Tipp-Punkt ({x:.0f},{y:.0f})")
    taps(x, y)


def zur_galerie(pid):
    home()
    _, y = muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2")
    schnell("Safari")
    time.sleep(1.2)
    muss(seh.warte("Safari", 3, ueber=200), "Safari nicht in der Suche")
    taps(62, 145, "w2.0")                                        # Toptreffer
    # Adressleiste unten antippen
    tx = seh.lesen()
    leiste = [t for t in tx if t[2] > 640 and ("." in t[0] or "suchen" in t[0].lower())]
    muss(leiste, "Safari-Adressleiste nicht gefunden")
    taps(167, leiste[0][2], "w1.0")
                                                                 # iOS markiert die alte Adresse selbst
    schnell(f"social1.ai/products/{pid}")
    key(36)                                                      # Return
    f = muss(seh.warte("View on TikTok Shop", 15), "Social1-Seite ohne „View on TikTok Shop“ (Login? Artur)")
    taps(f[0], f[1], "w3.0")
    for _ in range(12):                                          # evtl. „In TikTok öffnen?“
        tx = seh.lesen()
        o = seh.finde("Öffnen", tx, genau=True)
        if o:
            taps(o[0], o[1], "w2.5"); continue
        if any(g in t.lower() for t, _, _ in tx for g in ("kasse", "jetzt kaufen", "verdiene")):
            break
        time.sleep(0.5)
    else:
        raise Stopp("TikTok-Produktseite nicht erreicht")
    time.sleep(1.5)
    ziehe_hoch(450, 110)                                         # Vorschaukarte zur vollen Seite hochziehen
    time.sleep(1.5)
    for versuch in range(2):                                     # Tipp kommt oft erst beim 2. Mal an
        sicher_tippen(167, 300)                                  # Produktbild
        time.sleep(1.8)
        zz = subprocess.run(["zsh", "-c", f'zsh {HIER}/aufnahme.sh "{seh.TMP}/z.png" >/dev/null && {HIER}/bin/zaehler "{seh.TMP}/z.png"'],
                            capture_output=True, text=True)
        if zz.returncode == 0:
            log(f"Galerie offen: {zz.stdout.strip()}"); return
    raise Stopp("Vollbild-Galerie nicht offen (kein Zähler)")


def ziehe_hoch(von_y, nach_y, x=167):
    """Echter Wisch nach oben mit der virtuellen Maus (Fensterpunkte)."""
    out = subprocess.run([str(HIER / "bin" / "fenster")], capture_output=True, text=True).stdout.split()
    fx, fy = int(out[1]), int(out[2])
    subprocess.run([sys.executable, str(HIER / "ziehen.py"), str(fx + x), str(fy + von_y), str(fx + x), str(fy + nach_y)],
                   capture_output=True)


def main(a):
    if len(a) < 2:
        sys.exit(__doc__)
    pid, name = a[0], a[1]
    produkt = a[2] if len(a) > 2 else name
    ziel = pathlib.Path(a[3]) if len(a) > 3 else None
    try:
        zur_galerie(pid)
    except Stopp as e:
        sys.exit(f"STOPP: {e}")
    tts = f"https://shop.tiktok.com/view/product/{pid}"
    r = subprocess.run(["zsh", str(HIER / "galerie.sh"), name, produkt, f"https://www.social1.ai/products/{pid}", tts])
    if r.returncode:
        sys.exit("STOPP: galerie.sh abgebrochen")
    quelle = PROJ / "uebergabe" / "ausgang" / name
    if ziel:
        ziel.mkdir(parents=True, exist_ok=True)
        for f in quelle.iterdir():
            shutil.copy2(f, ziel / f.name)
        log(f"kopiert nach {ziel}")
    taps(23, 92, "w0.5")                                         # Galerie schließen (oben links)


if __name__ == "__main__":
    main(sys.argv[1:])
