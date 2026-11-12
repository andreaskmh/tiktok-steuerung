#!/usr/bin/env python3
"""Probelauf eines ganzen Posts per Kabel – endet als ENTWURF, nie veröffentlicht (12.11.2026).

  python3 werkzeuge/test/kabel_posttest.py "<eingang-json>"

Wie post_wagen.ein_post, aber: kein Doppel-Schutz, kein Eintrag in gepostet.txt/Status, statt Veröffentlichen
„Entwürfe“. Video kommt per AirDrop aufs iPhone.
"""
import json, pathlib, sys, time

HIER = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HIER))
import seh, posten as P, post_wagen as W, eingang as EG, airdrop
from posten import Stopp, log


def main(pfad):
    p = pathlib.Path(pfad)
    d = json.loads(p.read_text())
    assert seh.kabel(), "Kabel nicht aktiv"
    start = time.time()
    v = {"datei": str(EG.EIN / d["datei"]), "kachel": d["kachel"], "produkt": d["produkt"],
         "tts_id": d.get("tts_link", "").rstrip("/").split("/")[-1], "button": d["button"],
         "text": EG.text_von(d), "brand": d["brand"], "handle": d.get("handle", "")}
    import os
    if not os.environ.get("OHNE_AIRDROP"):
        EG.aufs_iphone([pathlib.Path(v["datei"])]);          log("Video auf dem iPhone")
    W.tiktok_auf(); W.zu_tabs(); W.profil(d["account"]);    log("Account ok")
    weg = W.in_wagen(v["tts_id"]);                          log(f"Produkt-Weg: {weg}")
    W.zu_tabs(); W.profil(d["account"])
    W.hochladen(v["kachel"]);                               log("Beitragsseite")
    if weg == "showcase":
        W.verlinken_showcase(v["produkt"], v["button"]);    log("Produkt verlinkt (Showcase)")
    else:
        W.verlinken_wagen(v["produkt"], v["button"]);       log("Produkt verlinkt (Einkaufswagen)")
    W.beschreiben_oder_ohne_brand(v)
    P.entwurf_speichern();                                  log("ALS ENTWURF GESPEICHERT (Probelauf, nicht veröffentlicht)")
    log(f"fertig in {time.time() - start:.0f} s")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except (Stopp, airdrop.Stopp) as e:
        sys.exit(f"STOPP: {e}")
