#!/usr/bin/env python3
"""Prüft die JSON-Dateien im Übergabe-Ordner (Format: docs/UEBERGABE.md).
Aufruf: python3 werkzeuge/pruefe_uebergabe.py [ordner …]   (Standard: uebergabe/eingang uebergabe/ausgang)
"""
import json, pathlib, sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
STATUS = {"entwurf", "bereit", "freigegeben", "gepostet", "fehler"}


def pruefe_post(p, d):
    f = []
    for k in ("version", "datei", "account", "produkt", "titel", "stapel", "status"):
        if not d.get(k) and d.get(k) != 0:
            f.append(f"Feld fehlt: {k}")
    if not (d.get("social1_link") or d.get("tts_link")):
        f.append("social1_link oder tts_link nötig")
    if d.get("status") not in STATUS:
        f.append(f"unbekannter status: {d.get('status')}")
    if d.get("datei") and not (p.parent / d["datei"]).exists() and "beispiel" not in p.parts:
        f.append(f"Video fehlt: {d['datei']}")
    for h in d.get("hashtags", []):
        if not str(h).startswith("#"):
            f.append(f"Hashtag ohne #: {h}")
    if d.get("status") == "gepostet" and not d.get("post_link"):
        f.append("gepostet, aber kein post_link")
    return f


def pruefe_produkt(p, d):
    f = [f"Feld fehlt: {k}" for k in ("version", "produkt", "bilder") if k not in d]
    for b in d.get("bilder", []):
        if not (p.parent / b).exists():
            f.append(f"Bild fehlt: {b}")
    return f


def main(args):
    ordner = [pathlib.Path(a) for a in args] or [WURZEL / "uebergabe/eingang", WURZEL / "uebergabe/ausgang"]
    fehler = anzahl = 0
    for o in ordner:
        for p in sorted(o.rglob("*.json")):
            anzahl += 1
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"✗ {p}: kein gültiges JSON ({e})"); fehler += 1; continue
            f = pruefe_produkt(p, d) if p.name == "produkt.json" else pruefe_post(p, d)
            print(("✗ " if f else "✓ ") + str(p.relative_to(WURZEL) if p.is_relative_to(WURZEL) else p))
            for x in f:
                print("   -", x)
            fehler += bool(f)
    print(f"{anzahl} Dateien, {fehler} mit Fehlern")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
