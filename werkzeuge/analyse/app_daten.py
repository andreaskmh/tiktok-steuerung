#!/usr/bin/env python3
"""Baut provision.json für statsKMH (iPhone, Mac, Browser) aus bestellungen.json + praemien.json + avatare/.
Schreibt nach iCloud Drive/kmhview/provision.json und hierher.  python3 werkzeuge/analyse/app_daten.py"""
import json, os, base64, datetime as D
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/statsKMH/provision.json")
r2 = lambda x: round(x + 0.0, 2)
HEUTE = D.date.today()


def wert(r):
    """Voraussichtliche Provision einer Bestellung: ausgezahlt = tatsächlich, offen = vorauss., nicht berechtigt = 0."""
    return r["provision_tats"] if r["status"] == "ausgezahlt" else r["provision_vorauss"] if r["status"] == "offen" else 0.0


def zeitraum(rows, von, bis):
    g = [r for r in rows if von <= r["bestellt"] <= bis]
    return {"provision": r2(sum(wert(r) for r in g)), "bestellungen": len(g),
            "umsatz": r2(sum(r["umsatz"] for r in g if r["status"] != "nicht berechtigt"))}


def offiziell(k):
    """Offizielle Tageswerte von TikToks Seite „Daten“ (daten_holen.py) → {tag: {...}}."""
    p = os.path.join(HIER, "exporte", k + ".tage.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def videos_aufrufe(k):
    """Top-Videos je Tag (daten_holen.py → <konto>.videotage.json) → je Video t: [[tag, aufrufe, gmv, artikel]].
    Gleiches Video = gleicher Titel (Anfang) + Postdatum; fehlt das Datum (Lesefehler), zählt der Titel allein."""
    p = os.path.join(HIER, "exporte", k + ".videotage.json")
    if not os.path.exists(p):
        return []
    vt = json.load(open(p)); vids = {}
    for tag, liste in sorted(vt.items()):
        for v in liste:
            t = v["titel"][:25]
            schl = (t, v["datum"]) if v["datum"] else next((s for s in vids if s[0] == t), (t, ""))
            if not v["datum"] and schl not in vids:
                schl = (t, "")
            e = vids.setdefault(schl, {"titel": v["titel"], "datum": v["datum"], "konto": k, "t": []})
            if v["datum"] and not e["datum"]:
                e["datum"] = v["datum"]
            e["t"].append([tag, int(v["aufrufe"] or 0), r2(v["gmv"] or 0), v["artikel"]])
    return list(vids.values())


def mische(td, off):
    """Tageszeilen [tag, provision, sales, umsatz, aufrufe, offiziell(0..1)]: TikTok-Zahl, wo abgelesen, sonst Export."""
    out = []
    for t in sorted(set(td) | set(off)):
        e = td.get(t, [0.0, 0, 0.0])
        o = off.get(t)
        if o and "provision" in o:
            ums = e[2] if ("gmv" in o.get("gerundet", []) and t in td) else o.get("gmv", e[2])
            out.append([t, r2(o["provision"]), int(o.get("artikel", e[1])), r2(ums), int(o.get("ansichten", 0)), 1])
        else:
            out.append([t, r2(e[0]), e[1], r2(e[2]), 0, 0])
    return out


def zr_aus_tage(tage_l):
    h = HEUTE.isoformat(); tag = lambda n: (HEUTE - D.timedelta(days=n)).isoformat()
    def z(von, bis):
        g = [r for r in tage_l if von <= r[0] <= bis]
        p = sum(r[1] for r in g)
        return {"provision": r2(p), "bestellungen": sum(r[2] for r in g), "umsatz": r2(sum(r[3] for r in g)),
                "aufrufe": sum(r[4] for r in g), "offiziell": round(sum(r[1] * r[5] for r in g) / p, 3) if p else 1.0}
    zr = {"heute": z(h, h), "gestern": z(tag(1), tag(1)), "tage3": z(tag(2), h), "tage7": z(tag(6), h), "tage30": z(tag(29), h)}
    m = {r[0]: r[1] for r in tage_l}
    verlauf = [{"tag": tag(n), "provision": r2(m.get(tag(n), 0))} for n in range(29, -1, -1)]
    return zr, verlauf


def konto_daten(rows, praemien, bereit=None, amtlich=None):
    aus = [r for r in rows if r["status"] == "ausgezahlt"]
    off = [r for r in rows if r["status"] == "offen"]
    weg = [r for r in rows if r["status"] == "nicht berechtigt"]
    h = HEUTE.isoformat(); tag = lambda n: (HEUTE - D.timedelta(days=n)).isoformat()
    k = {"ausgezahlt": r2(sum(r["provision_tats"] for r in aus)),
         "offen": r2(sum(r["provision_vorauss"] for r in off)), "offen_anzahl": len(off),
         "verloren": r2(sum(r["provision_vorauss"] for r in weg)), "bestellungen": len(rows),
         "quote_prozent": round(100 * len(weg) / max(1, len(aus) + len(weg)), 1),
         "praemien": r2(sum(p["betrag"] for p in praemien))}
    # Guthaben („Verfügbare Auszahlung“, abgelesen) → zur Auszahlung bereit; Rest der abgerechneten Provision (+ Prämien)
    # gilt als bereits aufs Bankkonto ausgezahlt (Näherung: Pauschalgebühren/Verstöße nicht abgezogen).
    k["bereit"] = r2(bereit) if bereit is not None else None
    k["bank"] = r2(max(0.0, k["ausgezahlt"] + k["praemien"] - bereit)) if bereit is not None else None
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
        return sorted(out, key=lambda x: -x["betrag"])[:100]
    # Tageswerte (für jeden Zeitraum inkl. eigenem): [tag, provision, bestellungen, umsatz]
    td = defaultdict(lambda: [0.0, 0, 0.0])
    for r in rows:
        e = td[r["bestellt"]]; e[1] += 1
        if r["status"] != "nicht berechtigt":
            e[0] += wert(r); e[2] += r["umsatz"]
    tage_l = mische(td, amtlich or {})
    zr, verlauf = zr_aus_tage(tage_l)
    # Videos je Tag: id → {name, konto, t: [[tag, bestellungen, gmv, provision]]}
    vt = {}
    for r in rows:
        if not r["video_id"] or r["status"] == "nicht berechtigt":
            continue
        v = vt.setdefault(r["konto"] + "/" + r["video_id"], {"id": r["video_id"], "konto": r["konto"], "name": r["produkt"], "t": {}})
        e = v["t"].setdefault(r["bestellt"], [0, 0.0, 0.0]); e[0] += 1; e[1] += r["umsatz"]; e[2] += wert(r)
    videos_tage = [{"id": v["id"], "konto": v["konto"], "name": v["name"],
                    "t": [[t, e[0], r2(e[1]), r2(e[2])] for t, e in sorted(v["t"].items())]} for v in vt.values()]
    return {"kennzahlen": k, "zeitraeume": zr, "tage": tage_l, "videos_tage": videos_tage, "verlauf": verlauf, "bestellmonate": bestellmonate,
            "auszahlmonate": [{"monat": m, "betrag": r2(v)} for m, v in sorted(am.items())],
            "videos": top("video_id"), "produkte": top("produkt_id"),
            "offen": sorted([{"produkt": r["produkt"], "konto": r["konto"], "bestellt": r["bestellt"], "betrag": r["provision_vorauss"]}
                             for r in off], key=lambda x: x["bestellt"], reverse=True)[:200]}


def avatar(k):
    p = os.path.join(HIER, "avatare", k + ".jpg")
    return base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else None


B = json.load(open(os.path.join(HIER, "bestellungen.json")))
rows = B["rows"]; pr = json.load(open(os.path.join(HIER, "praemien.json")))["rows"]
stand = {q["konto"]: q["datei_stand"] for q in B.get("quellen", [])}
konten = sorted({r["konto"] for r in rows})
def guthaben(k):
    p = os.path.join(HIER, "exporte", k + ".guthaben.json")
    return json.load(open(p))["bereit"] if os.path.exists(p) else None


liste = [dict(name=k, avatar=avatar(k), stand=stand.get(k), videos_aufrufe=videos_aufrufe(k), gelesen={t: v.get("gelesen", "") for t, v in offiziell(k).items()}, **konto_daten([r for r in rows if r["konto"] == k],
              [p for p in pr if p["konto"] == k], guthaben(k), offiziell(k))) for k in konten]
liste.sort(key=lambda x: -x["zeitraeume"]["tage30"]["provision"])
alle = dict(name="Alle Accounts", avatar=None, stand=None, **konto_daten(rows, pr))
# Alle: Tageszeilen = Summe der (gemischten) Konto-Zeilen; offiziell = Anteil der Provision aus TikTok-Zahlen
sm = defaultdict(lambda: [0.0, 0, 0.0, 0, 0.0])
for x in liste:
    for t, p, n, u, a, f in x["tage"]:
        e = sm[t]; e[0] += p; e[1] += n; e[2] += u; e[3] += a; e[4] += p * f
alle["tage"] = [[t, r2(e[0]), e[1], r2(e[2]), e[3], round(e[4] / e[0], 3) if e[0] else 1.0] for t, e in sorted(sm.items())]
alle["zeitraeume"], alle["verlauf"] = zr_aus_tage(alle["tage"])
alle["videos_aufrufe"] = [v for x in liste for v in x["videos_aufrufe"]]
gl = defaultdict(list)                       # Alle: Ablesezeit je Tag = früheste über die Accounts (konservativ)
for x in liste:
    for t, z in x["gelesen"].items():
        if z:
            gl[t].append(z)
alle["gelesen"] = {t: min(z) for t, z in gl.items()}
bek = [x["kennzahlen"] for x in liste if x["kennzahlen"]["bereit"] is not None]   # nur Konten mit abgelesenem Guthaben
alle["kennzahlen"]["bereit"] = r2(sum(x["bereit"] for x in bek)) if bek else None
alle["kennzahlen"]["bank"] = r2(sum(x["bank"] for x in bek)) if bek else None
out = {"stand": D.datetime.now().strftime("%Y-%m-%dT%H:%M"), "konten": [alle] + liste}
text = json.dumps(out, ensure_ascii=False)
open(os.path.join(HIER, "provision.json"), "w").write(text)
os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
tmp = os.path.join(os.path.dirname(ZIEL), ".provision.tmp")   # erst fertig schreiben, dann austauschen (iCloud/App lesen nie halbe Datei)
open(tmp, "w").write(text); os.replace(tmp, ZIEL)
print("ok", [(k["name"], k["zeitraeume"]["tage30"]["provision"]) for k in out["konten"]])
