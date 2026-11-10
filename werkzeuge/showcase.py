#!/usr/bin/env python3
"""Produkt ins Showcase des gerade aktiven TikTok-Accounts legen (Artur-Ablauf, 10.11.2026):
Safari → social1.ai/products/<id> → „View on TikTok Shop“ → Provisions-Badge „Verdiene … pro Verkauf“
→ „Zum Showcase hinzufügen“ (steht dort schon „Mehr erkunden“, ist es schon drin). Nie Kasse/Einkaufswagen.

  python3 werkzeuge/showcase.py <produkt-id> [<produkt-id> …]
"""
import subprocess, sys, time
sys.argv = sys.argv[:1] + sys.argv[1:]
import seh, stock
from posten import taps, schnell, key, Stopp, muss, log


def safari_url(url):
    stock.home()
    _, y = muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2"); schnell("Safari"); time.sleep(1.2)
    muss(seh.warte("Safari", 3, ueber=200), "Safari nicht in der Suche")
    taps(62, 145, "w2.0")
    leiste = [t for t in seh.lesen() if t[2] > 640 and ("." in t[0] or "suchen" in t[0].lower())]
    muss(leiste, "Safari-Adressleiste nicht gefunden")
    taps(167, leiste[0][2], "w1.0")
    x = [t for t in seh.lesen() if t[2] > 640 and t[0].strip() in ("×", "⊗", "®")]
    if x:
        taps(x[0][1], x[0][2], "w0.6")
    elif not seh.finde("Website suchen"):
        taps(241, 699, "w0.6")                                   # Lösch-Knopf im Adressfeld
    schnell(url); time.sleep(0.5); key(36)


def ins_showcase(pid):
    safari_url(f"social1.ai/products/{pid}")
    f = muss(seh.warte("View on TikTok Shop", 20), "Social1-Seite ohne „View on TikTok Shop“")
    taps(f[0], f[1], "w3.0")
    for _ in range(30):
        tx = seh.lesen(); o = seh.finde("Öffnen", tx, genau=True)
        if o:
            taps(o[0], o[1], "w2.5"); continue
        if seh.finde("pro Verkauf", tx) and seh.finde("Kasse", tx):
            break
        time.sleep(0.5)
    else:
        raise Stopp("TikTok-Produktseite nicht erreicht")
    time.sleep(1.0)
    for versuch in range(3):
        v = seh.warte("pro Verkauf", 4)
        muss(v, "Provisions-Badge „Verdiene … pro Verkauf“ fehlt")
        taps(v[0], v[1], "w2.5")
        tx = seh.lesen()
        if seh.finde("Mehr erkunden", tx):
            log(f"{pid}: schon im Showcase"); return "schon"
        z = seh.finde("Showcase hinzufügen", tx)
        if z:
            taps(z[0], z[1], "w2.0")
            if seh.warte("Mehr erkunden", 4) or seh.finde("hinzugefügt"):
                log(f"{pid}: ins Showcase gelegt"); return "neu"
            raise Stopp(f"{pid}: nach „Zum Showcase hinzufügen“ keine Bestätigung")
    raise Stopp(f"{pid}: „Zum Showcase hinzufügen“ nicht gefunden")


if __name__ == "__main__":
    for pid in sys.argv[1:]:
        try:
            ins_showcase(pid)
        except Stopp as e:
            sys.exit(f"STOPP: {e}")
