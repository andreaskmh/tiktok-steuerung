#!/usr/bin/env python3
"""Baut provision.json für kmhview (iPhone, Mac, Browser) aus bestellungen.json + praemien.json + avatare/.
Schreibt nach iCloud Drive/kmhview/provision.json und hierher.  python3 werkzeuge/analyse/app_daten.py"""
import json, os, base64, datetime as D
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/kmhview/provision.json")
r2 = lambda x: round(x + 0.0, 2)
HEUTE = D.date.today()


def wert(r):
    """Voraussichtliche Provision einer Bestellung: ausgezahlt = tatsächlich, offen = vorauss., nicht berechtigt = 0."""
    return r["provision_tats"] if r["status"] == "ausgezahlt" else r["provision_vorauss"] if r["status"] == "offen" else 0.0


def zeitraum(rows, von, bis):
    g = [r for r in rows if von <= r["bestellt"] <= bis]
    return {"provision": r2(sum(wert(r) for r in g)), "bestellungen": len(g),
            "umsatz": r2(sum(r["umsatz"] for r in g if r["status"] != "nicht berechtigt"))}


def konto_daten(rows, praemien):
    aus = [r for r in rows if r["status"] == "ausgezahlt"]
    off = [r for r in rows if r["status"] == "offen"]
    weg = [r for r in rows if r["status"] == "nicht berechtigt"]
    h = HEUTE.isoformat(); tag = lambda n: (HEUTE - D.timedelta(days=n)).isoformat()
    zr = {"heute": zeitraum(rows, h, h), "gestern": zeitraum(rows, tag(1), tag(1)),
          "tage7": zeitraum(rows, tag(6), h), "tage30": zeitraum(rows, tag(29), h)}
    tage = defaultdict(float)
    for r in rows:
        tage[r["bestellt"]] += wert(r)
    verlauf = [{"tag": tag(n), "provision": r2(tage.get(tag(n), 0))} for n in range(29, -1, -1)]
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

    def top(schl):
        t = defaultdict(lambda: {"betrag": 0.0, "n": 0, "weg": 0, "ok": 0, "konto": ""})
        for r in rows:
            e = t[r[schl]]; e["name"] = r["produkt"]; e["n"] += 1; e["konto"] = r["konto"]
            e["betrag"] += wert(r); e["weg"] += r["status"] == "nicht berechtigt"; e["ok"] += r["status"] == "ausgezahlt"
        out = [{"id": i or "", "name": e["name"], "konto": e["konto"], "betrag": r2(e["betrag"]), "bestellungen": e["n"],
                "quote_prozent": round(100 * e["weg"] / max(1, e["ok"] + e["weg"]), 1)} for i, e in t.items()]
        return sorted(out, key=lambda x: -x["betrag"])[:10]
    return {"kennzahlen": k, "zeitraeume": zr, "verlauf": verlauf, "bestellmonate": bestellmonate,
            "auszahlmonate": [{"monat": m, "betrag": r2(v)} for m, v in sorted(am.items())],
            "videos": top("video_id"), "produkte": top("produkt_id"),
            "offen": sorted([{"produkt": r["produkt"], "konto": r["konto"], "bestellt": r["bestellt"], "betrag": r["provision_vorauss"]}
                             for r in off], key=lambda x: x["bestellt"], reverse=True)[:30]}


def avatar(k):
    p = os.path.join(HIER, "avatare", k + ".jpg")
    return base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else None


B = json.load(open(os.path.join(HIER, "bestellungen.json")))
rows = B["rows"]; pr = json.load(open(os.path.join(HIER, "praemien.json")))["rows"]
stand = {q["konto"]: q["datei_stand"] for q in B.get("quellen", [])}
konten = sorted({r["konto"] for r in rows})
liste = [dict(name=k, avatar=avatar(k), stand=stand.get(k), **konto_daten([r for r in rows if r["konto"] == k],
              [p for p in pr if p["konto"] == k])) for k in konten]
liste.sort(key=lambda x: -x["zeitraeume"]["tage30"]["provision"])
alle = dict(name="Alle Accounts", avatar=None, stand=None, **konto_daten(rows, pr))
out = {"stand": D.datetime.now().strftime("%Y-%m-%dT%H:%M"), "konten": [alle] + liste}
text = json.dumps(out, ensure_ascii=False)
open(os.path.join(HIER, "provision.json"), "w").write(text)
os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
tmp = os.path.join(os.path.dirname(ZIEL), ".provision.tmp")   # erst fertig schreiben, dann austauschen (iCloud/App lesen nie halbe Datei)
open(tmp, "w").write(text); os.replace(tmp, ZIEL)
print("ok", [(k["name"], k["zeitraeume"]["tage30"]["provision"]) for k in out["konten"]])
