#!/usr/bin/env python3
"""Tägliche Research auf Social1 (Videos, „Today“ + „Trending“, ohne Kategorie). Safari am Mac, Artur eingeloggt.

  python3 werkzeuge/research.py lesen  <de|us> [--seiten 50]   # alle Seiten lesen → research/<datum>/<land>.json
  python3 werkzeuge/research.py filtern <de|us>                # Vorfilter (Alter, Promis, Beauty, Supplements)
  python3 werkzeuge/research.py blaetter <de|us> [--pro 20]    # Sammelbilder der Kandidaten zum Sortieren
  python3 werkzeuge/research.py speichern <de|us> "<Liste>" <nr> [<nr> ...]   # Videos (Kandidaten-Nr) in Social1-Liste
  python3 werkzeuge/research.py rangliste <de|us>              # Punkte + Platzierung der einsortierten Videos

Fortsetzbar: `lesen` überspringt fertige Seiten, `speichern` merkt sich Gespeichertes.
Ablage: uebergabe/research/<JJJJ-MM-TT>/ (de.json, de-kandidaten.json, de-blatt-01.jpg, de-sortiert.json …)
"""
import json, math, pathlib, re, subprocess, sys, time, urllib.request
from datetime import date

PROJ = pathlib.Path(__file__).resolve().parent.parent
HEUTE = date.today()
ORDNER = PROJ / "uebergabe" / "research" / HEUTE.isoformat()
REGELN = json.loads((PROJ / "werkzeuge" / "research_regeln.json").read_text())
BLATT = PROJ / "werkzeuge" / "bin" / "blatt"

JS_KARTEN = r"""JSON.stringify((()=>{
 const zahl=t=>t||'';
 return [...document.querySelectorAll('[data-slot=card]')].map(k=>{
  const t=k.parentElement.innerText.split('\n').map(s=>s.trim()).filter(Boolean);
  const p=k.querySelector('img[src*="/products/"]'); const v=k.querySelector('img[src*="thumbnails/"]');
  const st={}; k.querySelectorAll('svg').forEach(s=>{const n=((s.getAttribute('class')||'').match(/lucide-(eye|heart|message-circle|trending-up)\b/)||[])[1];
     if(n){const sp=s.parentElement.querySelector('span'); if(sp) st[n]=sp.innerText.trim();}});
  const creator=t.find(s=>s.startsWith('@'))||''; const ci=t.indexOf(creator);
  const gi=t.indexOf('Creator GMV (30D)');
  return {rang:(t.find(s=>/^#\d+$/.test(s))||'').slice(1), plus_views:(t.find(s=>/^\+.*Views$/.test(s))||'').replace(/^\+| Views$/g,''),
   feuer:t.includes('🔥'), ad:t.includes('Ad'), produkt:p?p.alt:'', produkt_id:p?((p.src.match(/products\/(\d+)/)||[])[1]||''):'',
   produkt_bild:p?p.src:'', video_id:v?((v.src.match(/thumbnails\/(\d+)/)||[])[1]||''):'', vorschau:v?v.src:'',
   creator:creator.slice(1), alter:ci>=0?(t.slice(ci+1).find(s=>s!=='•')||''):'', gmv:gi>=0?t[gi+1]:'',
   views:st['eye']||'', likes:st['heart']||'', kommentare:st['message-circle']||'', zuwachs:st['trending-up']||''};});
})())"""


class Haenger(Exception):
    """Social1-Tab antwortet nicht mehr (AppleEvent-Zeitüberschreitung) → Tab neu, Schritt wiederholen."""


def safari(js):
    r = subprocess.run(["osascript", "-e", "on run argv", "-e", "with timeout of 25 seconds", "-e",
                        'tell application "Safari" to do JavaScript (item 1 of argv) in front document', "-e", "end timeout",
                        "-e", "end run", js], capture_output=True, text=True)
    if r.returncode:
        if "-1712" in r.stderr:
            raise Haenger()
        sys.exit(f"STOPP Safari: {r.stderr.strip()}")
    return r.stdout.strip()


def tab_neu():
    """Eingefrorenen Social1-Tab schließen (nur wenn vorne wirklich Social1 ist) und frisch öffnen."""
    url = subprocess.run(["osascript", "-e", "with timeout of 10 seconds", "-e",
                          'tell application "Safari" to get URL of front document', "-e", "end timeout"],
                         capture_output=True, text=True).stdout.strip()
    if "social1.ai" not in url:
        sys.exit(f"STOPP Safari hängt, vorne ist aber nicht Social1 ({url[:60]}) – nichts geschlossen")
    subprocess.run(["osascript", "-e", "with timeout of 15 seconds", "-e", 'tell application "Safari" to close front window',
                    "-e", "end timeout"], capture_output=True)
    time.sleep(2)
    subprocess.run(["osascript", "-e", 'tell application "Safari" to make new document with properties {URL:"https://www.social1.ai/"}'],
                   capture_output=True)
    time.sleep(9)
    print("Safari-Tab hing → neu geöffnet", flush=True)


def mit_neustart(f, *args):
    """Fortsetzbare Abläufe bei hängendem Tab bis zu 6× neu starten (Gespeichertes/Gelesenes wird übersprungen)."""
    for _ in range(6):
        try:
            return f(*args)
        except Haenger:
            tab_neu()
    sys.exit("STOPP Safari hängt immer wieder")


def gehe(url):
    subprocess.run(["osascript", "-e", "on run argv", "-e", 'tell application "Safari" to set URL of front document to (item 1 of argv)',
                    "-e", "end run", url], capture_output=True)


def zahl(s):
    """'3.5M' → 3500000, '€6.8K' → 6800"""
    m = re.search(r"([\d.,]+)\s*([KMB]?)", s or "")
    if not m:
        return 0
    return int(float(m.group(1).replace(",", "")) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)])


def alter_tage(s):
    s = (s or "").lower()
    if "today" in s or "hour" in s or "minute" in s or "just" in s:
        return 0
    if "yesterday" in s:
        return 1
    m = re.search(r"(\d+|an?)\s+(day|week|month|year)", s)
    if not m:
        return 999
    n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
    return n * {"day": 1, "week": 7, "month": 30, "year": 365}[m.group(2)]


def land_setzen(land):
    gehe("https://www.social1.ai/")
    time.sleep(4)
    safari(f"localStorage.setItem('selectedRegion','{land}');1")
    gehe("https://www.social1.ai/?page=1")
    time.sleep(6)
    knopf = safari("[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).find(t=>/^(DE|US|UK|FR|ES|IT)$/.test(t))||''")
    if knopf.lower() != land:
        sys.exit(f"STOPP Land: Social1 zeigt '{knopf}' statt {land.upper()}")


def lesen(land, seiten):
    ORDNER.mkdir(parents=True, exist_ok=True)
    ziel = ORDNER / f"{land}.json"
    daten = json.loads(ziel.read_text()) if ziel.exists() else {"land": land, "datum": HEUTE.isoformat(), "seiten": {}}
    land_setzen(land)
    for s in range(1, seiten + 1):
        if str(s) in daten["seiten"]:
            continue
        gehe(f"https://www.social1.ai/?page={s}")
        karten, erwartet = [], str((s - 1) * 12 + 1)
        for _ in range(30):
            time.sleep(1)
            try:
                karten = json.loads(safari(JS_KARTEN) or "[]")
            except json.JSONDecodeError:
                karten = []
            if karten and karten[0]["rang"] == erwartet and all(k["video_id"] for k in karten):
                break
        if not karten or karten[0]["rang"] != erwartet:
            print(f"Seite {s}: keine Videos mehr → Ende")
            break
        for k in karten:
            k["seite"] = s
        daten["seiten"][str(s)] = karten
        ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1))
        print(f"Seite {s}: {len(karten)} Videos (#{karten[0]['rang']}–#{karten[-1]['rang']})", flush=True)
    alle = [k for s in daten["seiten"].values() for k in s]
    print(f"FERTIG lesen {land.upper()}: {len(alle)} Videos auf {len(daten['seiten'])} Seiten")


def alle_videos(land):
    d = json.loads((ORDNER / f"{land}.json").read_text())
    return [k for s in sorted(d["seiten"], key=int) for k in d["seiten"][s]]


def treffer(woerter, name):
    """Erstes Wort (Leerzeichen am Ende = ganzes Wort), das am Wortanfang im Produktnamen steht (\"lash\" trifft nicht \"Flash\", \"creme\" nicht \"Kakaocreme\")."""
    return next((w for w in woerter if re.search(r"(?<![a-zäöüß])" + re.escape(w.strip()) + (r"(?![a-zäöüß])" if w.endswith(" ") else ""), name)), None)


def filtern(land):
    raus, rein, gesehen = [], [], set()
    for k in alle_videos(land):
        name, cr, tage = k["produkt"].lower(), k["creator"].lower(), alter_tage(k["alter"])
        k["tage"] = tage
        grund = ""
        if k["video_id"] in gesehen:
            grund = "doppelt"
        elif tage > REGELN["max_alter_tage"][land]:
            grund = f"zu alt ({k['alter']})"
        elif any(p in cr for p in REGELN["promis"]):
            grund = "Promi"
        elif w := treffer(REGELN["supplements"], name):
            grund = f"Supplement ({w})"
        elif w := treffer(REGELN["beauty"], name):
            grund = f"Beauty ({w})"
        gesehen.add(k["video_id"])
        (raus if grund else rein).append({**k, "grund": grund} if grund else k)
    for i, k in enumerate(rein, 1):
        k["nr"] = i
    (ORDNER / f"{land}-kandidaten.json").write_text(json.dumps(rein, ensure_ascii=False, indent=1))
    (ORDNER / f"{land}-raus.json").write_text(json.dumps(raus, ensure_ascii=False, indent=1))
    gruende = {}
    for k in raus:
        g = k["grund"].split(" (")[0]
        gruende[g] = gruende.get(g, 0) + 1
    print(f"FERTIG filtern {land.upper()}: {len(rein)} Kandidaten, {len(raus)} raus {gruende}")


def blaetter(land, pro):
    if not BLATT.exists():
        subprocess.run(["zsh", str(PROJ / "werkzeuge" / "build.sh")], check=True)
    kand = json.loads((ORDNER / f"{land}-kandidaten.json").read_text())
    bilder = ORDNER / f"{land}-bilder"
    bilder.mkdir(exist_ok=True)
    for k in kand:
        f = bilder / f"{k['video_id']}.jpg"
        if not f.exists():
            try:
                urllib.request.urlretrieve(k["vorschau"], f)
            except Exception:
                pass
    for b in range(math.ceil(len(kand) / pro)):
        teil = kand[b * pro:(b + 1) * pro]
        args = []
        for k in teil:
            args += [str(bilder / f"{k['video_id']}.jpg"), f"{k['nr']} · {k['alter'].replace(' ago', '')}"]
        aus = ORDNER / f"{land}-blatt-{b + 1:02d}.jpg"
        subprocess.run([str(BLATT), str(aus), "5", *args], check=True)
        print(f"{aus.name}: Nr {teil[0]['nr']}–{teil[-1]['nr']}")


DLG = "document.querySelector('[data-slot=dialog-content]')"


def _haken(liste):
    """Checkbox der Liste im offenen Dialog anhaken: 'ok' | 'fehlt' | 'kein-dialog'."""
    name = json.dumps(liste)
    return safari(f"""(()=>{{const d={DLG}; if(!d) return 'kein-dialog';
const c=[...d.querySelectorAll('button[role=checkbox]')].find(c=>c.nextElementSibling&&c.nextElementSibling.innerText.trim()=={name});
if(!c) return 'fehlt'; if(c.getAttribute('aria-checked')!='true') setTimeout(()=>c.click(),0); return 'ok'}})()""")


def _dialog_zu(knopf):
    safari(f"(()=>{{const d={DLG}; const b=d&&[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='{knopf}'); if(b) setTimeout(()=>b.click(),0); return 1}})()")


def speichern(land, liste, nummern):
    kand = {k["nr"]: k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    log = ORDNER / f"gespeichert-{liste}.json"
    fertig = set(json.loads(log.read_text())) if log.exists() else set()
    land_setzen(land)
    seite = None
    for nr in nummern:
        k = kand[int(nr)]
        vid = k["video_id"]
        if vid in fertig:
            continue
        if seite != k["seite"]:
            gehe(f"https://www.social1.ai/?page={k['seite']}")
            seite = k["seite"]
            time.sleep(6)
        klick = f"""(()=>{{const c=[...document.querySelectorAll('[data-slot=card]')].find(c=>c.querySelector('img[src*="thumbnails/{vid}"]'));
if(!c) return 'fehlt'; const b=c.querySelector('button[title="Save to list"]'); setTimeout(()=>b.click(),0); return 'ok'}})()"""
        r = safari(klick)
        for nachbar in (k["seite"] + 1, k["seite"] - 1, k["seite"] + 2, k["seite"] + 3):   # Ränge verschieben sich im Lauf des Tages
            if r == "ok" or nachbar < 1:
                continue
            gehe(f"https://www.social1.ai/?page={nachbar}")
            seite = nachbar
            time.sleep(6)
            r = safari(klick)
        if r != "ok":
            print(f"Nr {nr}: Video nicht mehr in der Nähe von Seite {k['seite']} → übersprungen")
            continue
        anz = "0"                                    # warten, bis die Listen im Dialog geladen sind (nie leer anlegen)
        for _ in range(16):
            time.sleep(0.5)
            anz = safari(f"(()=>{{const d={DLG}; return d?String(d.querySelectorAll('button[role=checkbox]').length):'kein-dialog'}})()")
            if anz.isdigit() and int(anz) > 0:
                break
        if not (anz.isdigit() and int(anz) > 0):
            _dialog_zu("Close")
            sys.exit(f"STOPP speichern Nr {nr}: Dialog ohne Listen")
        r = _haken(liste)
        if r == "fehlt":                             # Liste anlegen (React-Feld per nativem Setter)
            safari(f"(()=>{{const d={DLG};const b=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()=='Create new list');setTimeout(()=>b.click(),0);return 1}})()")
            time.sleep(1.5)
            safari(f"""(()=>{{const i={DLG}.querySelector('input[placeholder="Enter list name..."]');
Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(liste)});i.dispatchEvent(new Event('input',{{bubbles:true}}));return 1}})()""")
            time.sleep(1.0)
            safari(f"(()=>{{const b=[...{DLG}.querySelectorAll('button[type=submit]')].find(b=>b.innerText.trim()=='Create');if(b&&!b.disabled)setTimeout(()=>b.click(),0);return 1}})()")
            for _ in range(8):
                time.sleep(1.0)
                r = _haken(liste)
                if r == "ok":
                    break
            print(f"Neue Liste angelegt: {liste}")
        time.sleep(0.6)
        ok = safari(f"""(()=>{{const d={DLG};const c=d&&[...d.querySelectorAll('button[role=checkbox]')].find(c=>c.nextElementSibling&&c.nextElementSibling.innerText.trim()=={json.dumps(liste)});
return c&&c.getAttribute('aria-checked')=='true'?'ja':'nein'}})()""")
        if r != "ok" or ok != "ja":
            _dialog_zu("Close")
            sys.exit(f"STOPP speichern Nr {nr}: Haken nicht gesetzt ({r})")
        _dialog_zu("Done")
        time.sleep(0.8)
        fertig.add(vid)
        log.write_text(json.dumps(sorted(fertig)))
        print(f"Nr {nr} → {liste} ({k['produkt'][:45]})", flush=True)
    print(f"FERTIG speichern {liste}: {len(fertig)} Videos")


def punkte(k):
    """Platzierung: Frische zählt am meisten (Today/Yesterday), dann Tempo, Verkaufskraft, Interaktion."""
    frische = {0: 100, 1: 85, 2: 55, 3: 40, 4: 30, 5: 22, 6: 16, 7: 12}.get(k.get("tage", 999), max(0, 10 - k.get("tage", 999) // 7))
    tempo = min(40, 8 * math.log10(max(1, zahl(k["plus_views"]))) - 24)      # 100K → 16, 1M → 24, 10M → 32
    gmv = min(15, 3 * math.log10(max(1, zahl(k["gmv"]))) - 6)                # €10K → 6, €100K → 9
    v = max(1, zahl(k["views"]))
    inter = min(15, 100 * (zahl(k["likes"]) + 3 * zahl(k["kommentare"])) / v)
    return round(frische + max(0, tempo) + max(0, gmv) + inter + (5 if k.get("feuer") else 0), 1)


def rangliste(land):
    sort = json.loads((ORDNER / f"{land}-sortiert.json").read_text())   # {"nr": "BOF"|"SLIDES"|"QUALITY", ...}
    kand = {str(k["nr"]): k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    zeilen = sorted(((punkte(kand[n]), n, art) for n, art in sort.items() if n in kand), reverse=True)
    aus = [f"# Rangliste {land.upper()} {HEUTE.strftime('%d.%m.%Y')}", "",
           "| Platz | Punkte | Liste | Alter | +Views | Produkt | Creator | Link |", "|---|---|---|---|---|---|---|---|"]
    for i, (p, n, art) in enumerate(zeilen, 1):
        k = kand[n]
        aus.append(f"| {i} | {p} | {art} | {k['alter']} | {k['plus_views']} | {k['produkt'][:50]} | @{k['creator']} | "
                   f"https://www.tiktok.com/@{k['creator']}/video/{k['video_id']} |")
    f = ORDNER / f"{land}-rangliste.md"
    f.write_text("\n".join(aus) + "\n")
    print("\n".join(aus[4:14]))
    print(f"FERTIG rangliste: {f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2 or a[1] not in ("de", "us"):
        sys.exit(__doc__)
    befehl, land = a[0], a[1]
    if befehl == "lesen":
        mit_neustart(lesen, land, int(a[a.index("--seiten") + 1]) if "--seiten" in a else 50)
    elif befehl == "filtern":
        filtern(land)
    elif befehl == "blaetter":
        blaetter(land, int(a[a.index("--pro") + 1]) if "--pro" in a else 20)
    elif befehl == "speichern":
        mit_neustart(speichern, land, a[2], " ".join(a[3:]).split())
    elif befehl == "rangliste":
        rangliste(land)
    else:
        sys.exit(__doc__)
