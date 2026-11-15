#!/usr/bin/env python3
"""Eingereichte Videos (uebergabe/eingang/) verwalten und posten.

  python3 werkzeuge/eingang.py liste                  # was liegt da, mit Status
  python3 werkzeuge/eingang.py freigeben <stapel>     # NUR nach Arturs OK im Chat („Schnitt geprüft, passt“)
  python3 werkzeuge/eingang.py posten <stapel> [--ohne-airdrop] [--entwurf]
                                                      # = post_mensch.py --stapel (Arturs Ablauf, seit 12.11.2026 abends)
                                                      # alter Weg: TS_ALT=1 … post_wagen.ein_post
                                                      # (ausverkauft → posten.py: Entwurf ohne Link)
                                                      # (ein Account nach dem anderen, kein Abstand)
Status/Verlauf werden in jede JSON zurückgeschrieben (gepostet / entwurf / fehler).
"""
import datetime, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh, posten
from posten import Stopp, taps, schnell, log

PROJ = HIER.parent
EIN = PROJ / "uebergabe" / "eingang"
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")
REIHENFOLGE = ["anduri.official", "ella_robinson2", "andreas.testet", "artur.official", "andreasfastlane"]


def alle():
    for p in sorted(EIN.glob("*.json")):
        yield p, json.loads(p.read_text(encoding="utf-8"))


def schreibe(p, d, status, info=""):
    d["status"] = status
    d.setdefault("verlauf", []).append({"zeit": datetime.datetime.now().isoformat(timespec="seconds"),
                                        "status": status, "info": info})
    if status == "gepostet":
        d["gepostet_um"] = d["verlauf"][-1]["zeit"]
        d.setdefault("post_link", f"https://www.tiktok.com/@{d['account']}")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def text_von(d):
    t = EMOJI.sub("", d["titel"]).strip()                        # Emojis gehen beim Tippen nicht
    tags = " ".join(h for h in d.get("hashtags", []) if h not in t)
    return re.sub(r"\s+", " ", f"{t} {tags}").strip() + " "


def aufs_iphone(videos):
    """Videos in die Fotos-App am iPhone. Kabel: per AirDrop (airdrop.py, ~11 s), sonst echtes Drag & Drop
    in die iPhone-Synchronisierung (eigener Ordner → Zeile 1 liegt immer gleich)."""
    if os.environ.get("TS_OHNE_AIRDROP"):                        # 12.11.2026: Videos sind schon am iPhone (AirDrop kam an, Erkennung nicht)
        log("TS_OHNE_AIRDROP: Videos schon am iPhone"); return
    if seh.kabel():
        import airdrop
        try:
            airdrop.senden([str(v) for v in videos])
        except airdrop.Stopp as e:
            raise Stopp(str(e))
        seh.kabel().taste("home"); time.sleep(0.8)
        log(f"{len(videos)} Video(s) per AirDrop aufs iPhone")
        return
    ordner = pathlib.Path(tempfile.mkdtemp(prefix="iphone-upload-"))
    for v in videos:
        try:
            os.link(v, ordner / v.name)
        except OSError:
            shutil.copy2(v, ordner / v.name)
    from stock import home
    home()
    _, y = posten.muss(seh.finde("Suchen", unter=550), "Home-Bildschirm nicht erreicht")
    taps(167, y, "w1.2"); schnell("Fotos"); time.sleep(1.2)
    taps(62, 145, "w2.5")                                        # Toptreffer Fotos
    posten.muss(seh.warte("Mediathek", 4), "Fotos-App nicht offen")
    subprocess.run(["osascript", "-e", f'''
tell application "Finder"
  set w to make new Finder window to (POSIX file "{ordner}/" as alias)
  set current view of w to list view
  set bounds of w to {{40, 80, 640, 700}}
  select every item of w
  activate
end tell'''], check=True)
    time.sleep(1.2)
    subprocess.run([sys.executable, str(HIER / "ziehen.py"), "330", "175", "867", "480"], check=True)
    time.sleep(3 + 2 * len(videos))
    subprocess.run(["osascript", "-e", 'tell application "Finder" to close front window'])
    log(f"{len(videos)} Video(s) aufs iPhone gezogen")


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "liste":
        for p, d in alle():
            print(f"{d['status']:11} {d['stapel']:14} {d['account']:16} {d['datei']}")
    elif cmd == "freigeben":
        st = a[1]
        n = 0
        for p, d in alle():
            if d["stapel"] == st and d["status"] == "bereit":
                schreibe(p, d, "freigegeben", "Artur: Schnitt geprüft, OK im Chat"); n += 1
        print(f"{n} Video(s) freigegeben")
    elif cmd == "posten" and not os.environ.get("TS_ALT"):     # seit 12.11.2026 abends: Arturs Ablauf (post_mensch.py)
        if len(a) < 2:
            sys.exit("posten <stapel>")
        os.execv(sys.executable, [sys.executable, str(HIER / "post_mensch.py"), "--stapel", *a[1:]])
    elif cmd == "posten":                                        # alter Weg (post_wagen) nur mit TS_ALT=1
        st = a[1] if len(a) > 1 else None
        liste = [(p, d) for p, d in alle() if d["status"] == "freigegeben" and (st is None or d["stapel"] == st)]
        if not liste:
            sys.exit("nichts freigegeben")
        liste.sort(key=lambda x: REIHENFOLGE.index(x[1]["account"]) if x[1]["account"] in REIHENFOLGE else 99)
        aufs_iphone([EIN / d["datei"] for _, d in liste])
        import post_wagen                                         # 12.11.2026: getesteter Weg (Showcase zuerst, sonst Wagen)
        for p, d in liste:
            if not d.get("ausverkauft"):
                log(f"── {d['datei']} → {d['account']}")
                try:
                    post_wagen.ein_post(p, d)                     # schreibt Status + gepostet.txt selbst
                except Stopp as e:
                    schreibe(p, d, "fehler", str(e))
                    sys.exit(f"STOPP bei {d['datei']}: {e}")
                continue
            v = {"datei": str(EIN / d["datei"]), "kachel": d["kachel"], "produkt": d["produkt"],
                 "tts_id": d.get("tts_link", "").rstrip("/").split("/")[-1], "button": d["button"],
                 "text": text_von(d), "brand": d["brand"], "handle": d.get("handle", ""),
                 "ausverkauft": d.get("ausverkauft", False)}
            log(f"── {d['datei']} → {d['account']}")
            try:
                erg = posten.ein_post(d["account"], v)
                schreibe(p, d, "gepostet" if erg == "gepostet" else "entwurf",
                         "" if erg == "gepostet" else "ausverkauft – als Entwurf ohne Link gespeichert")
            except Stopp as e:
                schreibe(p, d, "fehler", str(e))
                sys.exit(f"STOPP bei {d['datei']}: {e}")
        subprocess.run(["zsh", str(HIER / "sync.sh"), "sichern", "Posts"])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
