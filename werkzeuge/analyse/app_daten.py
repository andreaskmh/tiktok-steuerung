#!/usr/bin/env python3
"""Baut provision.json für die iPhone-App „Provision“ aus bestellungen.json + praemien.json.
Schreibt nach iCloud Drive/Provision/provision.json (App liest von dort).
  python3 werkzeuge/analyse/app_daten.py [bestellungen.json] [praemien.json]"""
import json, os, sys, datetime as D
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
B = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "bestellungen.json")
PR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "praemien.json")
ZIEL = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Provision/provision.json")
r2 = lambda x: round(x + 0.0, 2)


def konto_daten(rows, praemien):
    aus = [r for r in rows if r["status"] == "ausgezahlt"]
    off = [r for r in rows if r["status"] == "offen"]
    weg = [r for r in rows if r["status"] == "nicht berechtigt"]
    k = {"ausgezahlt": r2(sum(r["provision_tats"] for r in aus)),
         "offen": r2(sum(r["provision_vorauss"] for r in off)), "offen_anzahl": len(off),
         "verloren": r2(sum(r["provision_vorauss"] for r in weg)), "bestellungen": len(rows),
         "quote_prozent": round(100 * len(weg) / max(1, len(aus) + len(weg)), 1),
         "praemien": r2(sum(p["betrag"] for p in praemien))}
    bm = defaultdict(list)
    for r in rows:
        bm[r["bestellt"][:7]].append(r)
    bestellmonate = []
    for m in sorted(bm):
        g = bm[m]; a = sum(r["provision_tats"] for r in g if r["status"] == "ausgezahlt")
        o = sum(r["provision_vorauss"] for r in g if r["status"] == "offen")
        bestellmonate.append({"monat": m, "bestellungen": len(g),
            "fertig_prozent": round(100 * sum(r["status"] != "offen" for r in g) / len(g), 1),
            "ausgezahlt": r2(a), "offen": r2(o), "vorauss": r2(a + o),
            "verloren": r2(sum(r["provision_vorauss"] for r in g if r["status"] == "nicht berechtigt"))})
    am = defaultdict(float)
    for r in aus:
        if r["ausgezahlt_am"]:
            am[r["ausgezahlt_am"][:7]] += r["provision_tats"]
    def top(schl, name):
        t = defaultdict(lambda: {"betrag": 0.0, "n": 0, "weg": 0, "ok": 0})
        for r in rows:
            e = t[r[schl]]; e["name"] = r[name]; e["n"] += 1
            e["betrag"] += r["provision_tats"] if r["status"] == "ausgezahlt" else (r["provision_vorauss"] if r["status"] == "offen" else 0)
            e["weg"] += r["status"] == "nicht berechtigt"; e["ok"] += r["status"] == "ausgezahlt"
        out = [{"id": i, "name": e["name"], "betrag": r2(e["betrag"]), "bestellungen": e["n"],
                "quote_prozent": round(100 * e["weg"] / max(1, e["ok"] + e["weg"]), 1)} for i, e in t.items()]
        return sorted(out, key=lambda x: -x["betrag"])[:10]
    return {"kennzahlen": k, "bestellmonate": bestellmonate,
            "auszahlmonate": [{"monat": m, "betrag": r2(v)} for m, v in sorted(am.items())],
            "videos": top("video_id", "produkt"), "produkte": top("produkt_id", "produkt"),
            "offen": sorted([{"produkt": r["produkt"], "bestellt": r["bestellt"], "betrag": r["provision_vorauss"]} for r in off],
                            key=lambda x: x["bestellt"])}


rows = json.load(open(B))["rows"]; pr = json.load(open(PR))["rows"]
konten = sorted({r["konto"] for r in rows})
out = {"stand": D.datetime.now().strftime("%Y-%m-%dT%H:%M"),
       "konten": [dict(name=k, **konto_daten([r for r in rows if r["konto"] == k], [p for p in pr if p["konto"] == k])) for k in konten]}
if len(konten) > 1:
    out["konten"].insert(0, dict(name="Alle", **konto_daten(rows, pr)))
os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
json.dump(out, open(ZIEL, "w"), ensure_ascii=False, indent=1)
json.dump(out, open(os.path.join(HIER, "provision.json"), "w"), ensure_ascii=False, indent=1)
print("ok", ZIEL, [(k["name"], k["kennzahlen"]["ausgezahlt"]) for k in out["konten"]])
