#!/usr/bin/env python3
"""Tägliche Research auf Social1 (Videos, „Today“ + „Trending“, ohne Kategorie). Safari am Mac, Artur eingeloggt.

  python3 werkzeuge/research.py lesen  <de|us> [--seiten 100]  # alle Seiten lesen → research/<datum>/<land>.json
  python3 werkzeuge/research.py filtern <de|us>                # Vorfilter (Alter, Promis, Beauty, Supplements)
  python3 werkzeuge/research.py blaetter <de|us> [--pro 20]    # Sammelbilder der Kandidaten zum Sortieren
  python3 werkzeuge/research.py speichern <de|us> "<Liste>" <nr> [<nr> ...]   # Videos (Kandidaten-Nr) in Social1-Liste
  python3 werkzeuge/research.py rangliste <de|us>              # Punkte + Platzierung der einsortierten Videos
  python3 werkzeuge/research.py de-suche <suchwort>             # gibt es das im TikTok Shop DE? (Social1-Produkte, Bestseller)
  python3 werkzeuge/research.py amazon <suchwort>               # Amazon.es-Suche (nur lesen)
  python3 werkzeuge/research.py wagen <ASIN>                    # in den Amazon.es-Einkaufswagen (nie kaufen)
  python3 werkzeuge/research.py skripte <de|us> [--top 30]      # Transkripte Top je Liste → fremdsprachige in „SKRIPTE <datum>.md“
  python3 werkzeuge/research.py skript <de|us> <nr>             # Transkript (Social1 „Transcribe“) speichern
  python3 werkzeuge/research.py messen                         # stündlich (launchd): Seite 1 DE+US protokollieren
  python3 werkzeuge/research.py messung                        # Auswertung: wann aktualisiert Social1?

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


# Research arbeitet nur im eigenen Social1-Fenster (Video-Seite, nie die Listen-Tabs von post_mensch „saved-videos/…“).
AS_DOC = (['-e', 'on run argv', '-e', 'tell application "Safari"', '-e', 'set ziel to missing value', '-e', 'repeat with d in documents',
           '-e', 'set u to URL of d', '-e', 'if u is "https://www.social1.ai/" or u starts with "https://www.social1.ai/?" then',
           '-e', 'set ziel to d', '-e', 'exit repeat', '-e', 'end if', '-e', 'end repeat'])


def research_fenster():
    """Sorgt dafür, dass es ein eigenes Research-Fenster gibt (Social1-Videoseite)."""
    r = subprocess.run(["osascript", *AS_DOC, "-e", 'if ziel is missing value then', "-e",
                        'make new document with properties {URL:"https://www.social1.ai/?page=1"}', "-e", 'return "neu"', "-e",
                        'end if', "-e", 'return "da"', "-e", "end tell", "-e", "end run"], capture_output=True, text=True)
    if r.stdout.strip() == "neu":
        time.sleep(9)


def safari(js):
    r = subprocess.run(["osascript", *AS_DOC, "-e", 'if ziel is missing value then return "kein-fenster"', "-e",
                        "with timeout of 25 seconds", "-e", "return do JavaScript (item 1 of argv) in ziel", "-e", "end timeout",
                        "-e", "end tell", "-e", "end run", js], capture_output=True, text=True)
    if r.stdout.strip() == "kein-fenster":
        research_fenster()
        return safari(js)
    if r.returncode:
        if "-1712" in r.stderr:
            raise Haenger()
        sys.exit(f"STOPP Safari: {r.stderr.strip()}")
    return r.stdout.strip()


def tab_neu():
    """Eingefrorenen Social1-Tab schließen (nur wenn vorne wirklich Social1 ist) und frisch öffnen."""
    subprocess.run(["osascript", *AS_DOC, "-e", "if ziel is not missing value then", "-e", "with timeout of 15 seconds", "-e",
                    "close ziel", "-e", "end timeout", "-e", "end if", "-e", "end tell", "-e", "end run", "x"], capture_output=True)
    time.sleep(2)
    research_fenster()
    print("Safari-Tab hing → neu geöffnet", flush=True)


def mit_neustart(f, *args):
    """Beim Neustart nach Hänger wird --frisch nicht wiederholt (sonst ginge Gelesenes verloren).
    Fortsetzbare Abläufe bei hängendem Tab bis zu 6× neu starten (Gespeichertes/Gelesenes wird übersprungen)."""
    for _ in range(6):
        try:
            return f(*args)
        except Haenger:
            tab_neu()
            if f is lesen:
                args = args[:2] + (False,)
    sys.exit("STOPP Safari hängt immer wieder")


def land_zurueck():
    """Land für die anderen Social1-Tabs (post_mensch) wieder auf DE stellen."""
    try:
        safari("localStorage.setItem('selectedRegion','de');1")
    except (Haenger, SystemExit):
        pass


def gehe(url):
    research_fenster()
    subprocess.run(["osascript", *AS_DOC, "-e", "set URL of ziel to (item 1 of argv)", "-e", "end tell", "-e", "end run", url],
                   capture_output=True)


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


def lesen(land, seiten, frisch=False):
    ORDNER.mkdir(parents=True, exist_ok=True)
    ziel = ORDNER / f"{land}.json"
    if frisch and ziel.exists():                              # weiterer Lauf am selben Tag: alten Stand aufheben, neu lesen
        ziel.rename(ORDNER / f"{land}-{time.strftime('%H%M')}.json")
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


def frueher_gespeichert():
    """Alle Videos, die an früheren Tagen schon in einer Research-Liste gelandet sind (egal ob inzwischen nachgemacht und
    aus der Liste entfernt) → kommen nie ein zweites Mal rein. Gleiches Produkt mit anderem Video (neue Hook) bleibt erlaubt."""
    ids = set()
    for f in (PROJ / "uebergabe" / "research").glob("*/gespeichert-*.json"):
        if f.parent.name != HEUTE.isoformat():
            ids |= set(json.loads(f.read_text()))
    return ids


def gepostete_produkte():
    """Produkt-IDs, die Artur schon gepostet hat (posts-*.json) → in der Rangliste als „schon gemacht“ markiert."""
    ids = set()
    for f in (PROJ / "uebergabe" / "ausgang").glob("posts-*.json"):
        try:
            for p in json.loads(f.read_text()).get("posts", []):
                m = re.search(r"product/(\d+)", p.get("tts_link", ""))
                if m:
                    ids.add(m.group(1))
        except (json.JSONDecodeError, AttributeError):
            pass
    return ids


def filtern(land):
    raus, rein, gesehen = [], [], set()
    frueher = frueher_gespeichert()
    for k in alle_videos(land):
        name, cr, tage = k["produkt"].lower(), k["creator"].lower(), alter_tage(k["alter"])
        k["tage"] = tage
        grund = ""
        if k["video_id"] in gesehen:
            grund = "doppelt"
        elif k["video_id"] in frueher:
            grund = "schon an früherem Tag in einer Liste"
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
    alt = ORDNER / f"{land}-kandidaten.json"                  # Nummern bleiben über mehrere Läufe am Tag gleich
    nummer = {k["video_id"]: k["nr"] for k in json.loads(alt.read_text())} if alt.exists() else {}
    naechste = max(nummer.values(), default=0) + 1
    for k in rein:
        if k["video_id"] in nummer:
            k["nr"] = nummer[k["video_id"]]
        else:
            k["nr"], naechste = naechste, naechste + 1
            k["neu"] = True
    rein.sort(key=lambda k: k["nr"])
    (ORDNER / f"{land}-kandidaten.json").write_text(json.dumps(rein, ensure_ascii=False, indent=1))
    (ORDNER / f"{land}-raus.json").write_text(json.dumps(raus, ensure_ascii=False, indent=1))
    gruende = {}
    for k in raus:
        g = k["grund"].split(" (")[0]
        gruende[g] = gruende.get(g, 0) + 1
    print(f"FERTIG filtern {land.upper()}: {len(rein)} Kandidaten, {len(raus)} raus {gruende}")


def blaetter(land, pro, nur_neu=False):
    if not BLATT.exists():
        subprocess.run(["zsh", str(PROJ / "werkzeuge" / "build.sh")], check=True)
    kand = json.loads((ORDNER / f"{land}-kandidaten.json").read_text())
    if nur_neu:                                               # nur noch nicht einsortierte Kandidaten
        sort = ORDNER / f"{land}-sortiert.json"
        fertig = set(json.loads(sort.read_text()) if sort.exists() else []) | set(json.loads((ORDNER / f"{land}-nein.json").read_text())
                                                      if (ORDNER / f"{land}-nein.json").exists() else [])
        kand = [k for k in kand if str(k["nr"]) not in fertig] if sort.exists() else kand
    if not kand:
        return print("Keine neuen Kandidaten")
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
        aus = ORDNER / f"{land}-blatt-{'neu-' if nur_neu else ''}{b + 1:02d}.jpg"
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
    weg_log = ORDNER / f"nicht-gefunden-{liste}.json"         # nach Neustart nicht nochmal suchen
    weg = set(json.loads(weg_log.read_text())) if weg_log.exists() else set()
    fertig |= weg
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
            weg.add(vid)
            weg_log.write_text(json.dumps(sorted(weg)))
            continue
        anz = "0"                                    # warten, bis die Listen im Dialog geladen sind (nie leer anlegen)
        for _ in range(40):
            time.sleep(0.5)
            anz = safari(f"(()=>{{const d={DLG}; return d?String(d.querySelectorAll('button[role=checkbox]').length):'kein-dialog'}})()")
            if anz.isdigit() and int(anz) > 0:
                break
        if not (anz.isdigit() and int(anz) > 0):
            _dialog_zu("Close")
            print(f"Nr {nr}: Dialog ohne Listen → 30 s Pause, Tab neu", flush=True)
            time.sleep(30)
            raise Haenger()
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
    print(f"FERTIG speichern {liste}: {len(fertig - weg)} Videos ({len(weg)} nicht mehr gefunden)")


def _doc_js(prefix, js, start_url, warte=9):
    """JS in einem eigenen Safari-Fenster ausführen, dessen URL mit prefix beginnt (sonst neu öffnen)."""
    r = subprocess.run(["osascript", "-e", "on run argv", "-e", 'tell application "Safari"', "-e", "repeat with d in documents",
                        "-e", "if URL of d starts with (item 2 of argv) then", "-e", "with timeout of 25 seconds", "-e",
                        "return do JavaScript (item 1 of argv) in d", "-e", "end timeout", "-e", "end if", "-e", "end repeat",
                        "-e", 'return "kein-fenster"', "-e", "end tell", "-e", "end run", js, prefix], capture_output=True, text=True)
    if r.stdout.strip() == "kein-fenster":
        subprocess.run(["osascript", "-e", "on run argv", "-e", 'tell application "Safari" to make new document with properties {URL:(item 1 of argv)}',
                        "-e", "end run", start_url], capture_output=True)
        time.sleep(warte)
        return _doc_js(prefix, js, start_url, warte)
    if r.returncode:
        if "-1712" in r.stderr:
            raise Haenger()
        sys.exit(f"STOPP Safari: {r.stderr.strip()}")
    return r.stdout.strip()


def _doc_gehe(prefix, url, warte=7):
    _doc_js(prefix, "1", url)
    subprocess.run(["osascript", "-e", "on run argv", "-e", 'tell application "Safari"', "-e", "repeat with d in documents",
                    "-e", "if URL of d starts with (item 2 of argv) then", "-e", "set URL of d to (item 1 of argv)", "-e", "exit repeat",
                    "-e", "end if", "-e", "end repeat", "-e", "end tell", "-e", "end run", url, prefix], capture_output=True)
    time.sleep(warte)


S1P = "https://www.social1.ai/products"
JS_PRODUKTE = r"""JSON.stringify([...document.querySelectorAll('tr')].map(r=>{const t=r.innerText.split(/\n|\t/).map(s=>s.trim()).filter(Boolean);
 const i=r.querySelector('img[src*="/products/"]'); if(!i||t.length<6) return null;
 return {name:t[0], shop:t[1], preis:t[2], gmv:t[3], views:t[4], videos:t[5], verkauft:t[6]||'', id:(i.src.match(/products\/(\d+)/)||[])[1]||''};}).filter(Boolean))"""


def de_suche(suchwort, n=5):
    """Gibt es das Produkt (oder ein ähnliches) im TikTok Shop DE? Social1-Produktsuche mit Land DE, Bestseller zuerst."""
    import urllib.parse
    _doc_js(S1P, "localStorage.setItem('selectedRegion','de');1", S1P)
    _doc_gehe(S1P, f"{S1P}?q={urllib.parse.quote_plus(suchwort)}", 8)
    erg = []
    for _ in range(10):
        try:
            erg = json.loads(_doc_js(S1P, JS_PRODUKTE, S1P) or "[]")
        except json.JSONDecodeError:
            erg = []
        if erg:
            break
        time.sleep(1)
    erg.sort(key=lambda p: zahl(p["verkauft"]), reverse=True)
    for p in erg[:n]:
        print(f"{p['verkauft']:>6} verkauft | {p['preis']:>8} | {p['name'][:90]} | id {p['id']}")
    if not erg:
        print("NICHTS in DE gefunden")
    return erg[:n]


AMZ = "https://www.amazon.es"


def amazon_suche(suchwort, n=5):
    """Amazon.es durchsuchen (nur lesen): ASIN, Preis, Bewertungen, Titel."""
    import urllib.parse
    _doc_gehe(AMZ, f"{AMZ}/s?k={urllib.parse.quote_plus(suchwort)}", 7)
    js = r"""JSON.stringify([...document.querySelectorAll('div[data-component-type="s-search-result"]')].filter(d=>d.dataset.asin&&!d.innerText.includes('Patrocinado')).slice(0,12).map(d=>({asin:d.dataset.asin,
      titel:(d.querySelector('h2')||{}).innerText||'', preis:(d.querySelector('.a-price .a-offscreen')||{}).innerText||'',
      bewertungen:((d.querySelector('[aria-label*="valoraciones"],[aria-label*="calificaciones"], a[href*="customerReviews"] span')||{}).innerText||'').trim()})))"""
    erg = json.loads(_doc_js(AMZ, js, AMZ) or "[]")
    for p in erg[:n]:
        print(f"{p['asin']} | {p['preis']:>9} | {p['bewertungen']:>8} | {p['titel'][:90]}")
    if not erg:
        print("NICHTS auf Amazon.es gefunden")
    return erg[:n]


def amazon_wagen(asin):
    """Produkt per ASIN in den Amazon.es-Einkaufswagen legen. Klickt NUR #add-to-cart-button, nie „Comprar ya“/Kasse."""
    _doc_gehe(AMZ, f"{AMZ}/dp/{asin}", 7)
    info = json.loads(_doc_js(AMZ, r"""JSON.stringify({titel:((document.querySelector('#productTitle')||{}).innerText||'').trim(),
       knopf:!!document.querySelector('#add-to-cart-button'), login:!!document.querySelector('#nav-link-accountList')&&
       !/Hola, identifícate/i.test((document.querySelector('#nav-link-accountList')||{}).innerText||''),
       captcha:/captcha|robot/i.test(document.title+document.body.innerText.slice(0,500))})""", AMZ))
    if info["captcha"]:
        sys.exit("STOPP Amazon zeigt Captcha/Robot-Prüfung – macht Artur")
    if not info["knopf"]:
        return print(f"{asin}: kein „In den Einkaufswagen“-Knopf (nicht lieferbar/Variante wählen?) – übersprungen")
    _doc_js(AMZ, "(()=>{const b=document.querySelector('#add-to-cart-button'); setTimeout(()=>b.click(),0); return 1})()", AMZ)
    time.sleep(5)
    ok = _doc_js(AMZ, r"""(()=>{const t=document.body.innerText; return /Añadido a la cesta|Agregado a la cesta|Añadido al carrito|Subtotal de la cesta/i.test(t)?'ja':'nein'})()""", AMZ)
    print(f"{asin}: {'IN DEN WAGEN' if ok == 'ja' else 'unklar (kein Bestätigungstext)'} | {'eingeloggt' if info['login'] else 'NICHT eingeloggt'} | {info['titel'][:80]}")
    return ok == "ja"


def skript(land, nr, land_schon=False):
    """ACHTUNG: verbraucht Social1-Credits – nur auf Arturs ausdrücklichen Wunsch benutzen.
    „Transcribe“ von Social1 für ein Video holen → research/<datum>/<land>-skripte/<nr>-original.txt (Claude schreibt daraus Deutsch)."""
    kand = {k["nr"]: k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    k = kand[int(nr)]
    if not land_schon:
        land_setzen(land)
    for s in (k["seite"], k["seite"] + 1, k["seite"] - 1, k["seite"] + 2):
        if s < 1:
            continue
        gehe(f"https://www.social1.ai/?page={s}")
        time.sleep(6)
        r = safari(f"""(()=>{{const c=[...document.querySelectorAll('[data-slot=card]')].find(c=>c.querySelector('img[src*="thumbnails/{k['video_id']}"]'));
if(!c) return 'fehlt'; const b=[...c.querySelectorAll('button')].find(b=>b.innerText.trim()=='Transcribe'); if(!b) return 'kein knopf';
setTimeout(()=>b.click(),0); return 'ok'}})()""")
        if r == "ok":
            break
    else:
        return print(f"Nr {nr}: Video nicht gefunden")
    text = ""
    for _ in range(30):
        time.sleep(1.5)
        text = safari(f"(()=>{{const d={DLG}; return d? d.innerText : ''}})()")
        if text and not re.search(r"Transcribing|Loading|Generating", text, re.I) and len(text) > 40:
            break
    _dialog_zu("Close")
    ziel = ORDNER / f"{land}-skripte"
    ziel.mkdir(exist_ok=True)
    (ziel / f"{nr}-original.txt").write_text(text)
    print(f"Nr {nr}: Transkript {len(text)} Zeichen → {ziel.name}/{nr}-original.txt")


DEUTSCH = set("""der die das und ist nicht ich du er sie wir ihr es ein eine einen dem den des mit für auf zu von im in ist sind war hab habe hast hat
noch nur auch aber oder wie was wenn dann so ja nein mal schon jetzt hier da kann kannst muss müsst gibt euch mir dich dir mein dein sein
ihr unser einfach wirklich heute alle diese dieser dieses gerade richtig kostet euro cent""".split())


def ist_deutsch(text):
    w = re.findall(r"[a-zäöüß]+", text.lower())
    return len(w) >= 8 and sum(x in DEUTSCH for x in w) / len(w) >= 0.12


def skripte(land, top=30):
    """Lokale Transkripte (werkzeuge/transkript.py: yt-dlp + Whisper, KEINE Social1-Credits) für die Top-Videos jeder Liste.
    Fremdsprachige (alles außer Deutsch, auch Englisch) → Tagesdatei „SKRIPTE <datum>.md“ mit Original + Platzhalter „DEUTSCH:“,
    den Claude danach ausfüllt. Deutsch gesprochene und Videos ohne Sprache: kein Skript."""
    sort = json.loads((ORDNER / f"{land}-sortiert.json").read_text())
    kand = {str(k["nr"]): k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    gesp = set()
    for f in ORDNER.glob("gespeichert-*.json"):
        gesp |= set(json.loads(f.read_text()))
    ordner = ORDNER / f"{land}-transkripte"
    auswahl = []
    for art in sorted({a for a in sort.values() if not a.endswith("?")}):
        nrn = [n for n, a in sort.items() if a == art and n in kand and kand[n]["video_id"] in gesp]
        auswahl += sorted(nrn, key=lambda n: punkte(kand[n]), reverse=True)[:top]
    link = lambda k: f"https://www.tiktok.com/@{k['creator']}/video/{k['video_id']}"
    fehlen = [x for n in auswahl if not (ordner / f"{n}.json").exists() for x in (n, link(kand[n]))]
    if fehlen:
        venv = pathlib.Path.home() / ".tiktok-research" / "venv" / "bin" / "python"
        subprocess.run([str(venv), str(PROJ / "werkzeuge" / "transkript.py"), str(ordner), *fehlen])
    datei = ORDNER / f"SKRIPTE {HEUTE.strftime('%d.%m.%Y')}.md"
    text = datei.read_text() if datei.exists() else f"# Skripte {HEUTE.strftime('%d.%m.%Y')} – nur fremdsprachige Videos\n"
    neu, deutsch = 0, 0
    for n in sorted(auswahl, key=lambda n: punkte(kand[n]), reverse=True):
        f = ordner / f"{n}.json"
        if not f.exists():
            continue
        t = json.loads(f.read_text())
        orig, sprache = t.get("text", ""), t.get("sprache", "")
        k, marke = kand[n], f"<!-- {land}-{n} -->"
        if sprache == "de":
            deutsch += 1
        if len(orig) < 30 or sprache in ("de", "") or marke in text:
            continue
        text += (f"\n{marke}\n## {land.upper()} {sort[n]} Nr {n} · {k['alter']} · +{k['plus_views']} Views · Sprache {sprache} · {k['produkt'][:70]}\n"
                 f"{link(k)}\n\n**Original:**\n> {orig[:1500]}\n\n**DEUTSCH:** _(Claude schreibt: Hook + Skript)_\n")
        neu += 1
    datei.write_text(text)
    print(f"FERTIG skripte {land.upper()}: {len(auswahl)} geprüft, {deutsch} deutsch, {neu} neue fremdsprachige → {datei.name}")


# Sperre + Messung liegen außerhalb von ~/Documents: die stündliche Messung (launchd) darf dort nicht lesen/schreiben (macOS-Schutz)
# und läuft aus einer Kopie in ~/.tiktok-research/ (werkzeuge/research-messen-installieren.sh nach Änderungen erneut ausführen).
HEIM = pathlib.Path.home() / ".tiktok-research"
SPERRE = HEIM / ".laeuft"
MESSUNG = HEIM / "messung.jsonl"


def sperre_setzen():
    import atexit, os
    SPERRE.parent.mkdir(parents=True, exist_ok=True)
    SPERRE.write_text(str(os.getpid()))
    atexit.register(lambda: SPERRE.unlink(missing_ok=True))


def sperre_aktiv():
    import os
    try:
        os.kill(int(SPERRE.read_text()), 0)
        return True
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return False


def messen():
    """Stündlich (launchd): Seite 1 DE + US lesen und protokollieren → erkennen, wann Social1 seine Zahlen erneuert."""
    if sperre_aktiv():
        return print("Research läuft gerade – Messung ausgelassen")
    sperre_setzen()
    zeile = {"zeit": time.strftime("%Y-%m-%d %H:%M")}
    try:
        for land in ("de", "us"):
            land_setzen(land)
            karten = []
            for _ in range(20):
                time.sleep(1)
                try:
                    karten = json.loads(safari(JS_KARTEN) or "[]")
                except json.JSONDecodeError:
                    karten = []
                if karten and karten[0]["rang"] == "1" and all(k["video_id"] for k in karten):
                    break
            zeile[land] = [[k["video_id"], k["plus_views"], k["views"]] for k in karten]
    finally:
        land_zurueck()
    with MESSUNG.open("a") as f:
        f.write(json.dumps(zeile) + "\n")
    print(f"Messung {zeile['zeit']}: DE {len(zeile.get('de', []))}, US {len(zeile.get('us', []))}")


def messung_auswerten():
    """Zeigt pro Stunde, ob sich Top 12 / +Views geändert haben (Änderung = Social1 hat aktualisiert)."""
    z = [json.loads(l) for l in MESSUNG.read_text().splitlines() if l.strip()]
    for a, b in zip(z, z[1:]):
        for land in ("de", "us"):
            va, vb = a.get(land, []), b.get(land, [])
            neu_ids = len({x[0] for x in vb} - {x[0] for x in va})
            gleich = sum(1 for x in vb for y in va if x[0] == y[0] and x[1] == y[1])
            print(f"{b['zeit']} {land.upper()}: {neu_ids:2d} neue Videos in Top 12, {gleich:2d} mit unveränderten +Views")


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
    gemacht = gepostete_produkte()
    zeilen = sorted(((punkte(kand[n]), n, art) for n, art in sort.items() if n in kand and not art.endswith("?")), reverse=True)
    aus = [f"# Rangliste {land.upper()} {HEUTE.strftime('%d.%m.%Y')}", "",
           "| Platz | Punkte | Liste | Alter | +Views | Produkt | Creator | Link |", "|---|---|---|---|---|---|---|---|"]
    for i, (p, n, art) in enumerate(zeilen, 1):
        k = kand[n]
        if k["produkt_id"] in gemacht:
            art += " (Produkt schon gepostet)"
        aus.append(f"| {i} | {p} | {art} | {k['alter']} | {k['plus_views']} | {k['produkt'][:50]} | @{k['creator']} | "
                   f"https://www.tiktok.com/@{k['creator']}/video/{k['video_id']} |")
    f = ORDNER / f"{land}-rangliste.md"
    f.write_text("\n".join(aus) + "\n")
    print("\n".join(aus[4:14]))
    print(f"FERTIG rangliste: {f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["messen"]:
        mit_neustart(messen)
        sys.exit()
    if a[:1] == ["messung"]:
        messung_auswerten()
        sys.exit()
    if a[:1] == ["de-suche"]:
        mit_neustart(de_suche, " ".join(a[1:]))
        sys.exit()
    if a[:1] == ["amazon"]:
        mit_neustart(amazon_suche, " ".join(a[1:]))
        sys.exit()
    if a[:1] == ["wagen"]:
        mit_neustart(amazon_wagen, a[1])
        sys.exit()
    if a[:1] in (["lesen"], ["speichern"]):
        sperre_setzen()
    if len(a) < 2 or a[1] not in ("de", "us"):
        sys.exit(__doc__)
    befehl, land = a[0], a[1]
    if befehl == "lesen":
        frisch = "--frisch" in a
        mit_neustart(lesen, land, int(a[a.index("--seiten") + 1]) if "--seiten" in a else 100, frisch)
        land_zurueck()
    elif befehl == "filtern":
        filtern(land)
    elif befehl == "blaetter":
        blaetter(land, int(a[a.index("--pro") + 1]) if "--pro" in a else 20, "--neu" in a)
    elif befehl == "speichern":
        mit_neustart(speichern, land, a[2], " ".join(a[3:]).split())
        land_zurueck()
    elif befehl == "skripte":
        skripte(land, int(a[a.index("--top") + 1]) if "--top" in a else 30)
    elif befehl == "skript":
        mit_neustart(skript, land, a[2])
        land_zurueck()
    elif befehl == "rangliste":
        rangliste(land)
    else:
        sys.exit(__doc__)
