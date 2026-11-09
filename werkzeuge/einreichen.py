#!/usr/bin/env python3
"""Fertiges Video aus dem Editing System zum Posten einreichen (legt Video + JSON in uebergabe/eingang/, Status „bereit“).

  python3 werkzeuge/einreichen.py <video.mp4> --account anduri.official --stapel 2026-11-10-a \\
      --produkt "BASIC HOSENROCK" --tts-id 1729926696937953544 --kachel "KEIN ROCK" \\
      --titel "Sieht aus wie ein Rock …" --hashtags "#hosenrock #skort #tiktokshop" \\
      --brand "Seamless Fashion" --handle seamlessfashion [--button "Wenige auf Lager"] [--social1 <link>]

--kachel  = Text, der groß auf dem Video steht (Hook-Label) – daran findet posten.py das Video in der Galerie.
--produkt = Teil des Produktnamens, wie er im Showcase steht.
--button  = fehlt er, wird einer aus Arturs Liste gemischt (ACCOUNTS.md).
Gepostet wird erst, wenn Artur den Schnitt abgenommen hat: eingang.py freigeben <stapel>, dann eingang.py posten.
"""
import argparse, json, os, pathlib, random, re, shutil, sys

PROJ = pathlib.Path(__file__).resolve().parent.parent
EIN = PROJ / "uebergabe" / "eingang"
BUTTONS = ["Wenige verfügbar", "Fast ausverkauft", "Fast vergriffen", "Wenige auf Lager", "Geringer Bestand", "Bald vergriffen"]


def name_sicher(s):
    return re.sub(r"[^A-Za-z0-9ÄÖÜäöüß._ -]+", "", s).strip()


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("video")
    for k in ("account", "stapel", "produkt", "kachel", "titel", "brand"):
        a.add_argument("--" + k, required=True)
    a.add_argument("--handle", default="", help="genauer TikTok-Nutzername des Shops; leer = Shop-Name muss eindeutig sein")
    a.add_argument("--tts-id", default="")
    a.add_argument("--social1", default="")
    a.add_argument("--hashtags", default="")
    a.add_argument("--button", default="")
    a.add_argument("--notiz", default="")
    o = a.parse_args()
    v = pathlib.Path(o.video).expanduser().resolve()
    if not v.exists():
        sys.exit(f"Video fehlt: {v}")
    if not (o.tts_id or o.social1):
        sys.exit("--tts-id oder --social1 nötig")
    button = o.button or random.choice(BUTTONS)
    if len(button) > 20:
        sys.exit("Button-Text länger als 20 Zeichen")
    EIN.mkdir(parents=True, exist_ok=True)
    ziel = EIN / name_sicher(v.name)
    try:
        os.link(v, ziel)                     # gleiche Platte: kein Platz verbraucht
    except OSError:
        shutil.copy2(v, ziel)
    d = {"version": 1, "datei": ziel.name, "account": o.account, "social1_link": o.social1,
         "tts_link": f"https://shop.tiktok.com/view/product/{o.tts_id}" if o.tts_id else "",
         "produkt": o.produkt, "titel": o.titel, "hashtags": o.hashtags.split(), "stapel": o.stapel,
         "status": "bereit", "notiz": o.notiz, "verlauf": [],
         "kachel": o.kachel, "button": button, "brand": o.brand, "handle": o.handle.lstrip("@"),
         "quelle": str(v)}
    ziel.with_suffix(".json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"eingereicht: {ziel.name} → {o.account} (Stapel {o.stapel}, wartet auf Arturs OK)")


if __name__ == "__main__":
    main()
