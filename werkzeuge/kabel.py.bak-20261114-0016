#!/usr/bin/env python3
"""iPhone-Steuerung per Kabel (open-iphone-use, Xcode-CoreDevice) – ersetzt iPhone-Synchronisierung + virtuelle Maus.

  python3 werkzeuge/kabel.py status            # verbunden? USB/WLAN?
  python3 werkzeuge/kabel.py foto [ziel.png]   # verlustfreies Bild vom iPhone
  python3 werkzeuge/kabel.py tipp x y          # Tipp (Punkte wie seh.py: Breite 334)
  python3 werkzeuge/kabel.py taste home        # home, lock, return, backspace, cmd+v …
  python3 werkzeuge/kabel.py text "Hallo Ä #x" # tippen (deutsches Layout)

Koordinaten: „Punkte“ wie das alte Fenster (334 × 735), damit seh.py, tap.py und posten.py unverändert rechnen. Jeder Befehl wartet, bis der Server ihn ausgeführt hat (der Server prüft, dass das Bild
nach der letzten Eingabe entstanden ist). Server starten: open-iphone-use serve (siehe docs/KABEL.md).
"""
import json, os, pathlib, random, subprocess, sys, time, urllib.request, urllib.error

URL = os.environ.get("OIU_URL", "http://127.0.0.1:27893")
UDID = os.environ.get("TS_IPHONE_UDID", "00008030-00096C8621C3402E")   # iPhone 11 von Artur
BREITE = 334.0
_dev = None
_frame = None          # frameID, gültig für die nächste Eingabe
_groesse = None        # (breite, höhe) in Pixeln


class KabelFehler(Exception):
    pass


def _get(pfad, roh=False, timeout=10):
    with urllib.request.urlopen(URL + pfad, timeout=timeout) as r:
        d = r.read()
    return d if roh else json.loads(d)


def _post(pfad, daten, timeout=30):
    req = urllib.request.Request(URL + pfad, json.dumps(daten).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}") | {"ok": False}


def aktiv(starten=True):
    """True, wenn der Server läuft und das iPhone ein Live-Bild liefert (dann nutzen alle Werkzeuge das Kabel).
    Läuft der Server nicht (z. B. nach Mac-Neustart), startet ihn der Wächter einmal und es wird bis 60 s gewartet."""
    if os.environ.get("TS_MODUS") == "sync":
        return False
    try:
        if geraet(nur_pruefen=True):
            return True
    except Exception:
        pass
    if not starten:
        return False
    w = pathlib.Path(__file__).resolve().parent / "kabel" / "waechter.py"
    print("iPhone-Server läuft nicht → starte ihn (bis 60 s) …", file=sys.stderr, flush=True)
    subprocess.run([sys.executable, str(w), "einmal"], capture_output=True, timeout=120)
    for _ in range(30):
        try:
            if geraet(nur_pruefen=True):
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def geraet(nur_pruefen=False):
    global _dev
    if _dev and not nur_pruefen:
        return _dev
    for d in _get("/api/devices", timeout=3):
        if d.get("udid") == UDID and d.get("capture_active"):
            _dev = d["device_id"]
            return _dev
    if nur_pruefen:
        return None
    raise KabelFehler("iPhone nicht verbunden (open-iphone-use serve? Kabel? entsperrt?) – docs/KABEL.md")


def _p(pfad=""):
    return f"/api/devices/{geraet()}{pfad}"


def _frisch():
    """frameID eines Bilds nach der letzten Eingabe holen."""
    global _frame, _groesse
    for _ in range(20):
        d = _get(_p("/snapshot"))
        f = d["frame"]
        _groesse = (f["width"], f["height"])
        if f["frameID"] != _frame or _frame is None:
            _frame = f["frameID"]
            return _frame
        time.sleep(0.05)
    _frame = f["frameID"]
    return _frame


def groesse():
    if not _groesse:
        _frisch()
    return _groesse


HOEHE = 735.0   # wie das alte Fenster der iPhone-Synchronisierung → alle festen Koordinaten in posten.py passen weiter
                # (Bild 832×1808 wird auf 334×735 abgebildet; 681 = untere Leiste, getestet 12.11.2026)


def hoehe():
    return HOEHE


def aktion(op, **args):
    global _frame, _groesse
    for versuch in range(3):
        if _frame is None or versuch:
            _frisch()
        r = _post(_p("/action"), {"operation": op, "arguments": dict(args, expectedFrameID=_frame)})
        f = r.get("frame") or {}
        if r.get("ok"):
            _frame = f.get("frameID")
            if f.get("width"):
                _groesse = (f["width"], f["height"])
            return r
        msg = r.get("message") or r.get("error") or str(r)
        if "frame" not in msg.lower() and "Frame" not in msg:
            raise KabelFehler(f"{op}: {msg}")
        _frame = None
        time.sleep(0.15)
    raise KabelFehler(f"{op}: {msg}")


# ---------------------------------------------------------------- Eingaben (Punkte)

def _anteil(x, y):
    return min(1.0, max(0.0, x / BREITE)), min(1.0, max(0.0, y / hoehe()))


def tipp(x, y):
    fx, fy = _anteil(x, y)
    aktion("pointer_tap", x=fx, y=fy)


def ziehe(x1, y1, x2, y2, dauer=0.3):
    a, b = _anteil(x1, y1)
    c, d = _anteil(x2, y2)
    aktion("drag", x1=a, y1=b, x2=c, y2=d, dauer=dauer)


def taste(name):
    """home, lock, volume_up … oder Tastenkürzel: return, backspace, escape, cmd+a, cmd+v …"""
    aktion("send_key", key=name)


# Deutsches Hardware-Tastaturlayout am iPhone (QWERTZ, Mac-Belegung): Zeichen → (modifier, HID-usage)
_SHIFT, _ALT = 2, 4
_DE = {" ": (0, 0x2c), "\n": (0, 0x28), "\t": (0, 0x2b),
       "ß": (0, 0x2d), "?": (_SHIFT, 0x2d), "´": (0, 0x2e), "`": (_SHIFT, 0x2e),
       "ü": (0, 0x2f), "Ü": (_SHIFT, 0x2f), "+": (0, 0x30), "*": (_SHIFT, 0x30), "~": (_ALT, 0x30),
       "#": (0, 0x32), "'": (_SHIFT, 0x32),
       "ö": (0, 0x33), "Ö": (_SHIFT, 0x33), "ä": (0, 0x34), "Ä": (_SHIFT, 0x34),
       "^": (0, 0x35), "°": (_SHIFT, 0x35),
       ",": (0, 0x36), ";": (_SHIFT, 0x36), ".": (0, 0x37), ":": (_SHIFT, 0x37),
       "-": (0, 0x38), "_": (_SHIFT, 0x38), "<": (0, 0x64), ">": (_SHIFT, 0x64),
       "!": (_SHIFT, 0x1e), '"': (_SHIFT, 0x1f), "§": (_SHIFT, 0x20), "$": (_SHIFT, 0x21), "%": (_SHIFT, 0x22),
       "&": (_SHIFT, 0x23), "/": (_SHIFT, 0x24), "(": (_SHIFT, 0x25), ")": (_SHIFT, 0x26), "=": (_SHIFT, 0x27),
       "@": (_ALT, 0x0f), "€": (_ALT, 0x08), "[": (_ALT, 0x22), "]": (_ALT, 0x23), "{": (_ALT, 0x25), "}": (_ALT, 0x26),
       "|": (_ALT, 0x24), "\\": (_ALT | _SHIFT, 0x24), "0": (0, 0x27)}
_LAYOUT = os.environ.get("TS_LAYOUT", "de")


def _code(ch):
    if _LAYOUT == "de":
        if ch in _DE:
            return _DE[ch]
        lo = ch.lower()
        if "a" <= lo <= "z":
            if lo == "y": lo = "z"
            elif lo == "z": lo = "y"
            return (_SHIFT if ch.isupper() else 0), ord(lo) - 93
        if "1" <= ch <= "9":
            return 0, ord(ch) - 19
    else:
        if "a" <= ch <= "z": return 0, ord(ch) - 93
        if "A" <= ch <= "Z": return _SHIFT, ord(ch) - 61
        if "1" <= ch <= "9": return 0, ord(ch) - 19
    raise KabelFehler(f"Zeichen „{ch}“ lässt sich nicht tippen (Emoji?) – einfuegen() nehmen")


def text(t, menschlich=False):
    """Tippt über die Hardware-Tastatur. menschlich=True: einzeln mit 45–140 ms (TikTok-Regel)."""
    codes = [_code(c) for c in t]
    if not menschlich:
        for i in range(0, len(codes), 200):
            aktion("hid", keys=codes[i:i + 200])
        return
    i = 0                                                       # Artur 12.11.: schneller, aber menschlich →
    while i < len(codes):                                       # kleine Häppchen (2–5 Zeichen) mit 25–70 ms Abstand,
        n = random.randint(2, 5)                                # dazwischen kurze, selten längere Pausen
        aktion("hid", keys=codes[i:i + n], pause=round(random.uniform(0.025, 0.07), 3))
        i += n
        time.sleep(random.uniform(0.01, 0.06) + (random.uniform(0.15, 0.35) if random.random() < 0.05 else 0))


def schreibe(t, menschlich=False):
    """Tippen, wo möglich; nur bei Zeichen ohne Taste (Emojis) über die Zwischenablage (dann länger warten)."""
    try:
        [_code(c) for c in t]
    except KabelFehler:
        return einfuegen(t, warte=3.5)
    text(t, menschlich=menschlich)


def einfuegen(t, warte=1.5):
    """Über die gemeinsame Zwischenablage (Mac → iPhone, gleiche Apple-ID) + ⌘V. Geht auch mit Emojis."""
    subprocess.run(["pbcopy"], input=t.encode("utf-8"))
    time.sleep(warte)
    taste("cmd+v")


def loeschen(n):
    aktion("hid", keys=[[0, 0x2a]] * n)


# ---------------------------------------------------------------- Bilder

def foto(ziel=None, png=True):
    """Aktuelles Bild (nach der letzten Eingabe). png=True verlustfrei. Gibt Pfad oder Bytes zurück."""
    _frisch()
    daten = _get(_p("/png" if png else "/frame"), roh=True)
    if ziel:
        pathlib.Path(ziel).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(ziel).write_bytes(daten)
        return ziel
    return daten


def status():
    d = _get(_p("/status"))
    return d["backend"]["status"]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    try:
        if a[0] == "status":
            s = status(); print(f"{s['connection']}  verbunden={s['connected']}  bild={s['captureActive']}  {s.get('error','')}")
        elif a[0] == "foto":
            print(foto(a[1] if len(a) > 1 else "/tmp/iphone.png"))
        elif a[0] == "tipp":
            tipp(float(a[1]), float(a[2]))
        elif a[0] == "taste":
            taste(a[1])
        elif a[0] == "text":
            text(a[1])
        elif a[0] == "einfuegen":
            einfuegen(a[1])
        else:
            sys.exit(__doc__)
    except KabelFehler as e:
        sys.exit(f"STOPP: {e}")
