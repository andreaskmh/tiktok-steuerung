#!/usr/bin/env python3
"""Tägliche Research auf Social1 (Videos, „Today“ + „Trending“, ohne Kategorie). Safari am Mac, Artur eingeloggt.

  python3 werkzeuge/research.py lesen  <de|us> [--seiten 100]  # alle Seiten lesen → research/<datum>/<land>.json
  python3 werkzeuge/research.py filtern <de|us>                # Vorfilter (Alter, Promis, Beauty, Supplements)
  python3 werkzeuge/research.py blaetter <de|us> [--pro 20]    # Sammelbilder der Kandidaten zum Sortieren
  python3 werkzeuge/research.py speichern <de|us> "<Liste>" <nr> [<nr> ...]   # Videos (Kandidaten-Nr) in Social1-Liste
  python3 werkzeuge/research.py sortieren <de|us> "<Liste>"     # Social1-Liste in Ranglisten-Reihenfolge (Platz 1 oben)
  python3 werkzeuge/research.py rangliste <de|us>              # Punkte + Platzierung der einsortierten Videos
  python3 werkzeuge/research.py de-suche <suchwort>             # gibt es das im TikTok Shop DE? (Social1-Produkte, Bestseller)
  python3 werkzeuge/research.py de-suche --datei <woerter.txt>  # viele Suchwörter auf einmal (eine Zeile pro Wort)
  python3 werkzeuge/research.py bildvergleich <land> <wuensche.json>  # {"nr":["wort",…]} → Sammelbilder US-Bild vs. TikTok-Shop-DE/Amazon-Treffer
  python3 werkzeuge/research.py amazon <suchwort>               # Amazon.es-Suche (nur lesen)
  python3 werkzeuge/research.py wagen <ASIN>                    # in den Amazon.es-Einkaufswagen (nie kaufen)
  python3 werkzeuge/research.py skripte <de|us> [--top 30]      # Transkripte Top je Liste → fremdsprachige in „SKRIPTE <datum>.md“
  python3 werkzeuge/research.py skript <de|us> <nr>             # Transkript (Social1 „Transcribe“) speichern
  python3 werkzeuge/research.py vorbilder [--min 30000]           # Slideshow-Vorbilder (klickguru …) → uebergabe/ausgang/social1-vorbilder.json
  python3 werkzeuge/research.py gemacht-abgleich               # Arturs Listen vs. letzte Momentaufnahme → Erledigtes in gemacht.json
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


# ---- Direkter Weg zu Social1 (19.11.2026): Server-Aktionen statt Klicks -------------------------------------------------
# Die Webseite ruft intern Next.js-Server-Aktionen auf (POST, Header „next-action: <id>“, Body = JSON-Array der Argumente).
# Die IDs ändern sich bei Social1-Updates → werden bei jedem Lauf aus den geladenen JS-Dateien gelesen (Name → ID).
AKTIONEN = {}
JS_AKTIONEN = r"""(()=>{window.__s1akt=null;const js=[...new Set(performance.getEntriesByType('resource').map(e=>e.name)
 .filter(n=>n.includes('/_next/static/chunks/')&&n.includes('.js')))];
 Promise.all(js.map(u=>fetch(u).then(r=>r.text()).catch(e=>''))).then(ts=>{const a={};for(const t of ts)
 for(const m of t.matchAll(/createServerReference\)?\("([0-9a-f]{40,44})"[^)]{0,60}"([A-Za-z0-9_$]+)"/g))a[m[2]]=m[1];
 window.__s1akt=JSON.stringify(a)});return js.length})()"""


def aktionen_laden(pflicht=("getTopVideos", "getVideoLists", "addVideoToList", "getVideoListDetail", "createVideoList")):
    research_fenster()
    for runde in range(2):
        safari(JS_AKTIONEN)
        for _ in range(30):
            time.sleep(0.5)
            r = safari("window.__s1akt||''")
            if r:
                AKTIONEN.update(json.loads(r))
                break
        if all(n in AKTIONEN for n in pflicht):
            return AKTIONEN
        gehe("https://www.social1.ai/?page=1")            # Videoseite lädt alle nötigen Programmteile
        time.sleep(8)
    sys.exit(f"STOPP Social1: Aktionen nicht gefunden ({[n for n in pflicht if n not in AKTIONEN]}) – Social1 umgebaut?")


def s1(name, *args, warte=45):
    """Server-Aktion im Research-Fenster aufrufen und die Antwort (Zeile „1:{…}“) als Objekt zurückgeben."""
    if name not in AKTIONEN:
        aktionen_laden()
    schluessel = f"k{time.time_ns()}"
    body = json.dumps(list(args), ensure_ascii=False)
    start = safari(f"""(()=>{{window.__s1=window.__s1||{{}};const k={json.dumps(schluessel)};window.__s1[k]=null;
fetch(location.pathname,{{method:'POST',headers:{{'Accept':'text/x-component','next-action':{json.dumps(AKTIONEN[name])},
'Content-Type':'text/plain;charset=UTF-8'}},body:{json.dumps(body)}}}).then(r=>r.text().then(t=>window.__s1[k]=JSON.stringify({{s:r.status,t}})))
.catch(e=>window.__s1[k]=JSON.stringify({{s:0,t:String(e)}}));return 1}})()""")
    if start not in ("1", "1.0"):
        raise RuntimeError(f"Social1 {name}: Befehl startete nicht in Safari ({start[:80]!r})")
    for _ in range(warte * 4):
        time.sleep(0.25)
        r = safari(f"(()=>{{const v=(window.__s1||{{}})[{json.dumps(schluessel)}];if(v)delete window.__s1[{json.dumps(schluessel)}];return v||''}})()")
        if r:
            a = json.loads(r)
            zeile = next((l for l in a["t"].split("\n") if l.startswith("1:")), None)
            if a["s"] != 200 or zeile is None:
                if a["s"] in (404, 500) and "Server action" in a["t"]:
                    AKTIONEN.clear()                         # Social1 wurde aktualisiert → IDs neu lesen, einmal wiederholen
                    return s1(name, *args, warte=warte)
                raise RuntimeError(f"Social1 {name}: Status {a['s']} {a['t'][:200]}")
            return json.loads(zeile[2:])
    raise Haenger()


def s1_viele(name, argliste, parallel=4, warte=600):
    """Dieselbe Server-Aktion für viele Argument-Listen auf einmal (im Browser, je `parallel` gleichzeitig) → Antworten in Reihenfolge."""
    if not argliste:
        return []
    if name not in AKTIONEN:
        aktionen_laden()
    schluessel = f"v{time.time_ns()}"
    start = safari(f"""(()=>{{window.__s1=window.__s1||{{}};const k={json.dumps(schluessel)};const L={json.dumps(argliste, ensure_ascii=False)};
const out=new Array(L.length);let i=0;window.__s1[k+'_n']=0;
const eins=async()=>{{while(i<L.length){{const j=i++;try{{let r,t;for(let v=0;v<6;v++){{r=await fetch(location.pathname,{{method:'POST',headers:{{'Accept':'text/x-component',
'next-action':{json.dumps(AKTIONEN[name])},'Content-Type':'text/plain;charset=UTF-8'}},body:JSON.stringify(L[j])}});t=await r.text();
if(r.status!=429&&!t.includes('Too many requests'))break;await new Promise(x=>setTimeout(x,5000*(v+1)));}}
const z=t.split(String.fromCharCode(10)).find(l=>l.startsWith('1:'));out[j]=r.status==200&&z?z.slice(2):JSON.stringify({{error:'Status '+r.status}});}}
catch(e){{out[j]=JSON.stringify({{error:String(e)}})}};window.__s1[k+'_n']++;}}}};
Promise.all(Array.from({{length:{parallel}}},eins)).then(()=>window.__s1[k]=JSON.stringify(out));return 1}})()""")
    if start not in ("1", "1.0"):
        raise RuntimeError(f"Social1 {name}: Befehl startete nicht in Safari ({start[:80]!r})")
    for _ in range(warte * 2):
        time.sleep(0.5)
        r = safari(f"(()=>{{const v=(window.__s1||{{}})[{json.dumps(schluessel)}];if(v)delete window.__s1[{json.dumps(schluessel)}];return v||''}})()")
        if r:
            return [json.loads(x) for x in json.loads(r)]
    raise Haenger()


def _kurz(x, euro=False):
    """1600000 → '1.6M', 979300 → '979.3K' (wie auf der Social1-Seite)."""
    x = float(x or 0)
    for grenze, e in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= grenze:
            t = f"{x / grenze:.1f}".rstrip("0").rstrip(".") + e
            break
    else:
        t = f"{x:.0f}"
    return ("€" if euro else "") + t


def _alter_text(ts):
    try:
        tage = (HEUTE - date.fromisoformat(ts[:10])).days
    except (TypeError, ValueError):
        return ""
    return "Today" if tage <= 0 else "Yesterday" if tage == 1 else f"{tage} days ago"


def karte_aus_api(v):
    """Ein Video aus getTopVideos in dasselbe Format wie früher JS_KARTEN (filtern/blaetter/rangliste bleiben gleich)."""
    p = v.get("product_data") or {}
    return {"rang": str(v.get("ranking", "")), "plus_views": _kurz(v.get("view_gain")), "feuer": False, "ad": bool(v.get("is_ad")),
            "produkt": p.get("name", ""), "produkt_id": str(v.get("product_id") or p.get("product_id") or ""),
            "produkt_bild": p.get("img_url", ""), "video_id": str(v.get("video_id", "")), "vorschau": v.get("thumbnail", ""),
            "creator": v.get("handle", ""), "alter": _alter_text(v.get("time_posted")), "gmv": _kurz(v.get("med_gmv_revenue"), True), "video_gmv": v.get("gmv") or 0,
            "views": _kurz(v.get("views")), "likes": _kurz(v.get("likes")), "kommentare": _kurz(v.get("comments")),
            "zuwachs": _kurz(v.get("view_gain")), "time_posted": v.get("time_posted", ""), "slideshow": bool(v.get("is_slideshow")),
            "ki": bool(v.get("is_ai")), "preis": p.get("price_display", ""), "shop": v.get("shop_name", "")}


def top_videos(land, seite):
    """Seite (ab 1) der Social1-Videoliste „Today“ + „Trending“ direkt holen → (karten, has_more)."""
    d = s1("getTopVideos", {"limit": 12, "page": seite - 1, "region": land}).get("data") or {}
    return [karte_aus_api(v) for v in d.get("results") or []], bool(d.get("has_more"))


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
    """Alle Seiten direkt über Social1 lesen (getTopVideos, kein Blättern/Klicken mehr; ~1 s pro Seite)."""
    ORDNER.mkdir(parents=True, exist_ok=True)
    ziel = ORDNER / f"{land}.json"
    alt = ORDNER / f"{land}-{time.strftime('%H%M')}.json"
    if frisch and ziel.exists():                              # weiterer Lauf am selben Tag: alten Stand aufheben, neu lesen
        ziel.rename(alt)
    daten = json.loads(ziel.read_text()) if ziel.exists() else {"land": land, "datum": HEUTE.isoformat(), "seiten": {}}
    aktionen_laden()
    offen = [s for s in range(1, seiten + 1) if str(s) not in daten["seiten"]]
    ende = False
    for i in range(0, len(offen), 20):                         # 20 Seiten auf einmal (im Browser, 4 gleichzeitig)
        teil = offen[i:i + 20]
        antworten = s1_viele("getTopVideos", [[{"limit": 12, "page": s - 1, "region": land}] for s in teil])
        for s, a in zip(teil, antworten):
            d = a.get("data") or {}
            karten = [karte_aus_api(v) for v in d.get("results") or []]
            if not karten and s == 1:                          # 20.11.: Social1-Aussetzer lieferte 0 Videos und leerte die Kandidaten
                if frisch and alt.exists() and not ziel.exists():
                    alt.rename(ziel)
                sys.exit(f"STOPP: Social1 liefert Seite 1 leer ({str(a)[:150]}) – alter Stand bleibt, später nochmal")
            if not karten:
                print(f"Seite {s}: keine Videos mehr → Ende")
                ende = True
                break
            for k in karten:
                k["seite"] = s
            daten["seiten"][str(s)] = karten
            if not d.get("has_more"):
                print(f"Seite {s}: letzte Seite")
                ende = True
                break
        ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1))
        print(f"Seiten bis {teil[-1]} gelesen", flush=True)
        if ende:
            break
    alle = [k for s in daten["seiten"].values() for k in s]
    print(f"FERTIG lesen {land.upper()}: {len(alle)} Videos auf {len(daten['seiten'])} Seiten")


def alle_videos(land):
    d = json.loads((ORDNER / f"{land}.json").read_text())
    return [k for s in sorted(d["seiten"], key=int) for k in d["seiten"][s]]


def treffer(woerter, name):
    """Erstes Wort (Leerzeichen am Ende = ganzes Wort), das am Wortanfang im Produktnamen steht (\"lash\" trifft nicht \"Flash\", \"creme\" nicht \"Kakaocreme\")."""
    return next((w for w in woerter if re.search(r"(?<![a-zäöüß])" + re.escape(w.strip()) + (r"(?![a-zäöüß])" if w.endswith(" ") else ""), name)), None)


GEMACHT = PROJ / "uebergabe" / "research" / "gemacht.json"


def gemacht():
    """Videos, die Artur schon umgesetzt hat (aus seinen Listen entfernt / abgehakt) → nie wieder in eine Liste (Artur 19.11.)."""
    return set(json.loads(GEMACHT.read_text())) if GEMACHT.exists() else set()


def gemacht_merken(ids):
    g = gemacht() | set(ids)
    GEMACHT.write_text(json.dumps(sorted(g), indent=0))
    return g


def aus_liste_entfernen(liste, ids, paeckchen=20):
    """Videos aus einer Social1-Liste nehmen – vorher Sicherung, in kleinen Päckchen (Social1 bremst sonst)."""
    lid = liste_id(liste, anlegen=False)
    if not lid:
        return 0
    videos = ((s1("getVideoListDetail", lid).get("data") or {}).get("list") or {}).get("videos") or []
    (ORDNER / f"sicherung-{liste}-{time.strftime('%H%M%S')}.json").write_text(json.dumps(videos, ensure_ascii=False, indent=1))
    weg = [v["videoId"] for v in videos if v["videoId"] in set(ids)]
    for i in range(0, len(weg), paeckchen):
        s1("removeVideosFromList", lid, weg[i:i + paeckchen])
        time.sleep(1)
    return len(weg)


ARTUR_STAND = pathlib.Path.home() / ".tiktok-research" / "artur-listen.json"
# Bis welche Social1-Seite eine Liste Videos nimmt (Artur 19.11. abends): BOF/SLIDES DE nur bis 50, Rest bis 100 (gelesen wird bis 100).
SEITEN_MAX = {"BOF DE": 50, "SLIDES DE": 50}


def seiten_max(liste):
    return next((n for p, n in SEITEN_MAX.items() if liste.startswith(p)), 100)


UNSERE = re.compile(r"^(BOF DE|SLIDES DE|Reactions DE|SLIDES USA|Quality USA) \d\d\.\d\d\.\d{4}$")


def gemacht_abgleich():
    """Artur 20.11.2026: ALLE unsere Research-Listen (BOF/SLIDES/Reactions DE, Quality/SLIDES USA): was seit der letzten
    Momentaufnahme rausgenommen = abgehakt wurde (von Hand oder nach dem Upload per post_mensch.social1_abhaken), ist erledigt
    → gemacht.json + aus unseren Listen. Nicht Abgehaktes wandert in die Liste des nächsten Tages (filtern), je Land für sich."""
    aktionen_laden()
    ls = (s1("getVideoLists").get("data") or {}).get("lists") or []
    artur = [l for l in ls if UNSERE.match(l.get("name", ""))]
    jetzt = {l["_id"]: {"name": l["name"], "videos": listen_videos(l["_id"])} for l in artur}
    alt = json.loads(ARTUR_STAND.read_text()) if ARTUR_STAND.exists() else {}
    weg = set()
    for lid, l in jetzt.items():
        if lid in alt:                                         # shortcut: zählt auch, was ein abgebrochenes `sortieren` rausnahm
            ab = set(alt[lid]["videos"]) - set(l["videos"])    # was dort rausgenommen = abgehakt wurde, ist erledigt
            print(f"{l['name']}: {len(ab)} abgehakt, {len(l['videos'])} noch drin")
            weg |= ab
    weg -= gemacht()
    if weg:
        gemacht_merken(weg)
        for l in ls:
            if UNSERE.match(l.get("name", "")):
                n = aus_liste_entfernen(l["name"], weg)
                if n:
                    print(f"{l['name']}: {n} erledigte raus")
    ARTUR_STAND.write_text(json.dumps(jetzt, ensure_ascii=False))
    print(f"FERTIG gemacht-abgleich: {len(artur)} Research-Listen, {len(weg)} neu erledigt, gemacht.json hat {len(gemacht())}")


def frueher_gespeichert():
    """{video_id: Liste-Art} aller Videos, die an früheren Tagen schon in einer Research-Liste gelandet sind.
    Artur 20.11.2026: nicht Abgehaktes wandert (DE und USA) in die heutige Liste derselben Art."""
    ids = {}
    for f in sorted((PROJ / "uebergabe" / "research").glob("*/gespeichert-*.json")):
        if f.parent.name != HEUTE.isoformat():
            art = ("REACTIONS" if "Reactions" in f.name else "SLIDES" if "SLIDES" in f.name
                   else "QUALITY" if "Quality" in f.name else "BOF")
            for v in json.loads(f.read_text()):
                if v:
                    ids[v] = "BOF+SLIDES" if {ids.get(v), art} == {"BOF", "SLIDES"} else art
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
    schon = gemacht()
    for k in alle_videos(land):
        name, cr, tage = k["produkt"].lower(), k["creator"].lower(), alter_tage(k["alter"])
        k["tage"] = tage
        grund = ""
        if k["video_id"] in gesehen:
            grund = "doppelt"
        elif k["video_id"] in schon:
            grund = "schon gemacht (gemacht.json)"
        elif tage > REGELN["max_alter_tage"][land]:
            grund = f"zu alt ({k['alter']})"
        elif any(p in cr for p in REGELN["promis"]):
            k["promi"] = True                                 # Artur 19.11.: Promis → Liste „Reactions DE <datum>“, nicht raus
        elif REGELN.get("verstoss_risiko_aktiv", True) and (w := treffer(REGELN.get("verstoss_risiko", []), name)):
            grund = f"Verstoß-Risiko ({w})"
        elif k.get("slideshow") and land == "us":
            pass                                              # Artur 19.11.: SLIDES USA = Format-Ideen, Produkt egal (auch Beauty)
        elif land in REGELN.get("supplement_filter_laender", ["de", "us"]) and (w := treffer(REGELN["supplements"], name)):
            grund = f"Supplement ({w})"
        elif land in REGELN.get("beauty_filter_laender", ["de", "us"]) and (w := treffer(REGELN["beauty"], name)):
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
    # Übernahme von früheren Tagen (DE + USA): Art von damals, nicht neu ansehen
    sort = ORDNER / f"{land}-sortiert.json"
    so = json.loads(sort.read_text()) if sort.exists() else {}
    neu = {str(k["nr"]): frueher[k["video_id"]] for k in rein
           if k["video_id"] in frueher and str(k["nr"]) not in so and frueher[k["video_id"]] != "REACTIONS"}
    if neu:
        sort.write_text(json.dumps({**so, **neu}, ensure_ascii=False, indent=1))
        print(f"Übernahme von früheren Tagen: {len(neu)} Videos → {land}-sortiert.json")
    promis = [str(k["nr"]) for k in rein if k.get("promi")]
    (ORDNER / f"{land}-promis.txt").write_text(" ".join(promis))   # → speichern <land> "Reactions DE <datum>" "$(cat …)"
    if promis:
        print(f"Promis (Reactions): {len(promis)} → {land}-promis.txt")
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
            marke = " · SLIDE" if k.get("slideshow") else " · KI" if k.get("ki") else ""   # Social1-Einstufung
            args += [str(bilder / f"{k['video_id']}.jpg"), f"{k['nr']} · {k['alter'].replace(' ago', '')}{marke}"]
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


def liste_id(name, anlegen=True):
    """ID einer Social1-Videoliste per Namen (exakt); fehlt sie, direkt anlegen."""
    def suchen():
        ls = (s1("getVideoLists").get("data") or {}).get("lists") or []
        return [l["_id"] for l in ls if l.get("name") == name]
    ids = suchen()
    if len(ids) > 1:
        sys.exit(f"STOPP: Liste „{name}“ gibt es {len(ids)}× – Artur fragen, welche")
    if ids:
        return ids[0]
    if not anlegen:
        return None
    s1("createVideoList", name)
    ids = suchen()
    if not ids:
        sys.exit(f"STOPP: Liste „{name}“ ließ sich nicht anlegen")
    print(f"Neue Liste angelegt: {name}")
    return ids[0]


def listen_videos(lid):
    return [v.get("videoId") for v in ((s1("getVideoListDetail", lid).get("data") or {}).get("list") or {}).get("videos") or []]


def video_paket(k):
    """Datenpaket für addVideoToList (wie es die Social1-Seite schickt)."""
    ts = k.get("time_posted") or ""
    if not ts:                                                 # alte Lesung ohne Datum: aus „N days ago“ schätzen
        from datetime import timedelta
        ts = (HEUTE - timedelta(days=min(alter_tage(k.get("alter")), 365))).isoformat() + " 12:00:00"
    return {"videoId": k["video_id"], "isAd": 1 if k.get("ad") else 0, "description": None, "handle": k["creator"],
            "timePosted": ts, "product": {"productId": k["produkt_id"], "name": k["produkt"], "priceDisplay": k.get("preis", ""),
                                          "imgUrl": k["produkt_bild"]}}


def speichern(land, liste, nummern):
    """Videos (Kandidaten-Nr) direkt in die Social1-Liste legen (addVideoToList). Schon enthaltene werden übersprungen
    (prüft die echte Liste in Social1, nicht nur unser Protokoll)."""
    kand = {k["nr"]: k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    log = ORDNER / f"gespeichert-{liste}.json"
    fertig = set(json.loads(log.read_text())) if log.exists() else set()
    aktionen_laden()
    lid = liste_id(liste)
    drin = set(listen_videos(lid))
    neu = 0
    grenze = seiten_max(liste)
    nummern = [nr for nr in nummern if int(nr) in kand]       # Nr aus früherem Lesen (nicht mehr auf Social1) → war schon gespeichert
    zu_weit = [nr for nr in nummern if kand[int(nr)].get("seite", 0) > grenze]
    if zu_weit:
        print(f"{len(zu_weit)} Videos von Seite > {grenze} → nicht in {liste}: {zu_weit[:10]}")
    nummern = [nr for nr in nummern if nr not in zu_weit]
    offen = [kand[int(nr)] for nr in nummern if kand[int(nr)]["video_id"] and kand[int(nr)]["video_id"] not in drin]
    for i in range(0, len(offen), 50):                         # in Päckchen zu 50, Protokoll nach jedem Päckchen
        teil = offen[i:i + 50]
        for k, r in zip(teil, s1_viele("addVideoToList", [[lid, video_paket(k)] for k in teil])):
            if r.get("error") or (isinstance(r.get("data"), dict) and r["data"].get("error")):
                print(f"Nr {k['nr']}: Fehler {str(r)[:120]}")
                continue
            drin.add(k["video_id"])
            fertig.add(k["video_id"])
            neu += 1
        log.write_text(json.dumps(sorted(fertig)))
        print(f"… {min(i + 50, len(offen))}/{len(offen)}", flush=True)
    for nr in nummern:
        if not kand[int(nr)]["video_id"]:
            print(f"Nr {nr}: ohne Video-Nummer → übersprungen")
    echt = set(listen_videos(lid))
    fehlt = [n for n in nummern if kand[int(n)]["video_id"] not in echt]
    print(f"FERTIG speichern {liste}: {neu} neu, Liste hat jetzt {len(echt)} Videos" + (f", FEHLEN {fehlt[:10]}" if fehlt else ""))


def sortieren(land, liste):
    """Social1-Liste in Ranglisten-Reihenfolge bringen (Platz 1 oben). Social1 zeigt zuerst Hinzugefügtes oben → von Platz 1
    abwärts: jedes Video einzeln raus und sofort wieder rein (landet am Ende; nie mehr als 1 Video gleichzeitig weg).
    Vorher Sicherung der Liste als Datei; am Ende Abgleich, Fehlende werden aus der Sicherung nachgelegt."""
    kand = {k["video_id"]: k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    aktionen_laden()
    lid = liste_id(liste, anlegen=False)
    if not lid:
        sys.exit(f"STOPP: Liste „{liste}“ gibt es nicht")
    videos = ((s1("getVideoListDetail", lid).get("data") or {}).get("list") or {}).get("videos") or []
    sich = ORDNER / f"sicherung-{liste}-{time.strftime('%H%M%S')}.json"
    sich.write_text(json.dumps(videos, ensure_ascii=False, indent=1))
    pakete = []
    for v in videos:
        p = {f: v.get(f) for f in ("videoId", "isAd", "description", "handle", "timePosted")}
        p["product"] = {f: (v.get("product") or {}).get(f, "") for f in ("productId", "name", "priceDisplay", "imgUrl")}
        pakete.append(p)
    # Artur 20.11.: Reihenfolge 1:1 aus <land>-rangliste.md übernehmen (Platz 1 zuerst), Videos ohne Ranglisten-Platz ans Ende
    platz = {m: i for i, m in enumerate(re.findall(r"/video/(\d+) \|", (ORDNER / f"{land}-rangliste.md").read_text()))}
    rang = lambda p: -platz.get(p["videoId"], 10 ** 6)
    # Geprüft 19.11. abends: Social1 zeigt die Liste in Hinzufüge-Reihenfolge, das ZUERST Hinzugefügte steht OBEN
    # (= Reihenfolge von getVideoListDetail). Also Platz 1 zuerst einlegen, Unbekannte (ohne Kandidat) ans Ende.
    reihe = sorted(pakete, key=rang, reverse=True)
    jetzt = [v.get("videoId") for v in videos]                 # schon richtig sortierter Anfang wird nicht angefasst
    soll = [p["videoId"] for p in reihe]
    k = 0
    while k < len(soll) and jetzt[:k + 1] == soll[:k + 1]:
        k += 1
    for n, p in enumerate(reihe[k:], 1):
        try:                                                   # 20.11.: auch remove kann mit „Load failed“ abbrechen
            s1("removeVideosFromList", lid, [p["videoId"]])
        except RuntimeError:
            time.sleep(10)
            s1("removeVideosFromList", lid, [p["videoId"]])
        try:                                                   # 20.11.: „Load failed“ brach hier ab, Video war raus
            r = s1("addVideoToList", lid, p)
        except RuntimeError as e:
            r = {"error": str(e)}
        if r.get("error"):
            time.sleep(10)
            try:
                s1("addVideoToList", lid, p)
            except RuntimeError:
                pass                                           # Rest holt die Nachkontrolle „fehlt“ unten
        time.sleep(1)                                          # 20.11.: ohne Pause verlangte Social1 nach ~280 Aufrufen ein Captcha (429)
        if n % 50 == 0:
            print(f"… {n}/{len(reihe) - k}", flush=True)
    echt = set(listen_videos(lid))
    fehlt = [p for p in reihe if p["videoId"] not in echt]
    for p in fehlt:
        s1("addVideoToList", lid, p)
    echt = listen_videos(lid)
    print(f"FERTIG sortieren {liste}: {len(echt)}/{len(pakete)} Videos, Platz 1 oben (Sicherung {sich.name})")
    return echt


def speichern_klick(land, liste, nummern):
    """ALT (bis 19.11.2026): Speichern per Klick im Dialog – nur noch Reserve."""
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


# ── Slideshow-Vorbilder (Artur 20.11.2026): erfolgreiche Slideshow-Accounts (klickguru …) auslesen → Hits als Liste
#    im social1.py-Format (uebergabe/ausgang/social1-vorbilder.json), die das Slideshow-Auto im Editing System abarbeitet.
TT = "https://www.tiktok.com/@"
VORBILD_STAND = pathlib.Path.home() / ".tiktok-research" / "vorbilder.json"
JS_TT_HAKEN = r"""(()=>{if(window.__kdcap)return 'schon';window.__kdcap=[];
const of=window.fetch;window.fetch=async(...a)=>{const r=await of(...a);try{const u=(a[0]&&a[0].url)||String(a[0]);
 if(u.includes('/api/post/item_list'))r.clone().json().then(j=>window.__kdcap.push(j))}catch(e){};return r};
const oo=XMLHttpRequest.prototype.open,os=XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open=function(m,u){this.__u=u;return oo.apply(this,arguments)};
XMLHttpRequest.prototype.send=function(){this.addEventListener('load',()=>{if(String(this.__u||'').includes('/api/post/item_list'))
 try{window.__kdcap.push(JSON.parse(this.responseText))}catch(e){}});return os.apply(this,arguments)};
const k=t=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()===t);
setTimeout(()=>{k('Aktualisieren')&&k('Aktualisieren').click()},300);   // TikTok-Fehlerseite → neu laden (läuft dann durch den Haken)
[4000,6500,9000,11500,14000,16500].forEach(z=>setTimeout(()=>window.scrollTo(0,document.body.scrollHeight),z));
setTimeout(()=>{k('Beliebt')&&k('Beliebt').click()},19000);return 'ok'})()"""
# Erste Seite (neueste 16) kommt manchmal vor dem Haken → zusätzlich aus dem Raster (ID + Aufrufe, ohne Produkt).
JS_TT_LESEN = r"""(()=>{const z=s=>{s=(s||'').replace(',','.');const m=parseFloat(s);return /M/.test(s)?m*1e6:/K/.test(s)?m*1e3:m||0};
const L=(window.__kdcap||[]).flatMap(c=>c.itemList||[]).map(it=>{let p={};
 for(const a of it.anchors||[]){try{for(const x of JSON.parse(a.extra||'[]')){const m=String(x.extra||'').match(/"product_id"\s*:\s*"?(\d+)/);   // als Text: Zahl ist zu groß für JS
  if(m){let n='';try{n=JSON.parse(x.extra).title||''}catch(e){};p={id:m[1],name:n||x.keyword||''};break}}}catch(e){}}
 return {id:it.id,a:(it.author||{}).uniqueId,ct:it.createTime,v:(it.stats||{}).playCount,teile:(it.stats||{}).shareCount,
  bilder:((it.imagePost||{}).images||[]).length,cover:(((it.imagePost||{}).cover||{}).imageURL||{}).urlList?.[0]||'',
  ki:it.aigcLabelType||0,text:it.desc||'',sound:(it.music||{}).title||'',sound_id:(it.music||{}).id||'',produkt:p}});
const da=new Set(L.map(x=>x.id)),konto=location.pathname.split('@')[1].split('/')[0];
for(const e of document.querySelectorAll('[data-e2e="user-post-item"]')){const h=(e.querySelector('a')||{}).href||'';const m=h.match(/\/(photo|video)\/(\d+)/);
 if(!m||da.has(m[2]))continue;const img=e.querySelector('img');
 L.push({id:m[2],a:konto,ct:Number(BigInt(m[2])>>32n),v:z((e.querySelector('[data-e2e="video-views"]')||{}).innerText),teile:0,
  bilder:m[1]==='photo'?1:0,cover:(img||{}).src||'',ki:0,text:'',sound:((img||{}).alt||'').split('Musik ')[1]||'',sound_id:'',produkt:{}})}
return JSON.stringify(L)})()"""


def vorbilder(min_views=30000, max_tage=7):
    regeln = REGELN
    konten = regeln.get("vorbilder", ["klickguru"])
    stand = json.loads(VORBILD_STAND.read_text()) if VORBILD_STAND.exists() else {"genommen": []}
    alle = {}
    for konto in konten:
        _doc_gehe(TT, TT + konto, warte=8)
        _doc_js(TT, JS_TT_HAKEN, TT + konto)
        time.sleep(26)
        posts = [x for x in json.loads(_doc_js(TT, JS_TT_LESEN, TT + konto) or "[]") if x["a"] == konto]
        for x in posts:
            alle[x["id"]] = x
        print(f"{konto}: {len({x['id'] for x in posts})} Posts gelesen", flush=True)
    jetzt = time.time()
    hits = sorted((x for x in alle.values() if x["bilder"] and x["v"] >= min_views and jetzt - x["ct"] <= max_tage * 86400
                   and x["id"] not in stand["genommen"]), key=lambda x: -x["v"] / max(1, (jetzt - x["ct"]) / 3600))
    sounds = {}
    for x in alle.values():                                   # Gewinner-Sounds: Sounds mit Hits > min_views
        if x["v"] >= min_views and x["sound"]:
            s = sounds.setdefault(x["sound_id"], {"sound": x["sound"], "hits": 0, "views": 0})
            s["hits"] += 1; s["views"] += x["v"]
    eintraege = [{"nr": i, "produkt": x["produkt"].get("name", ""), "produkt_id": x["produkt"].get("id", ""),
                  "video_id": x["id"], "creator": "@" + x["a"], "vorschau": x["cover"], "views": x["v"], "bilder": x["bilder"],
                  "alter_h": round((jetzt - x["ct"]) / 3600), "sound": x["sound"], "sound_id": x["sound_id"], "ki_label": x["ki"],
                  "tts_link": f"https://shop.tiktok.com/view/product/{x['produkt'].get('id')}" if x["produkt"].get("id") else "",
                  "tiktok_link": f"https://www.tiktok.com/@{x['a']}/photo/{x['id']}"} for i, x in enumerate(hits, 1)]
    ziel = PROJ / "uebergabe" / "ausgang" / "social1-vorbilder.json"
    ziel.write_text(json.dumps({"liste": "vorbilder", "url": "", "gelesen": time.strftime("%Y-%m-%d %H:%M"), "eintraege": eintraege,
                                "gewinner_sounds": sorted(sounds.values(), key=lambda s: -s["views"])[:15]},
                               ensure_ascii=False, indent=1))
    stand["genommen"] = sorted(set(stand["genommen"]) | {e["video_id"] for e in eintraege})
    VORBILD_STAND.write_text(json.dumps(stand))
    for e in eintraege[:10]:
        print(f"{e['nr']}. {e['views']:>9} {e['alter_h']:>4}h {e['bilder']} Bilder · {e['produkt'][:50]} · {e['tiktok_link']}")
    print(f"FERTIG vorbilder: {len(eintraege)} Hits → {ziel}")


S1P = "https://www.social1.ai/products"
JS_PRODUKTE = r"""JSON.stringify([...document.querySelectorAll('tr')].map(r=>{const t=r.innerText.split(/\n|\t/).map(s=>s.trim()).filter(Boolean);
 const i=r.querySelector('img[src*="/products/"]'); if(!i||t.length<6) return null;
 return {name:t[0], shop:t[1], preis:t[2], gmv:t[3], views:t[4], videos:t[5], verkauft:t[6]||'', id:(i.src.match(/products\/(\d+)/)||[])[1]||''};}).filter(Boolean))"""


def _de_treffer(roh, n):
    erg = [{"name": p.get("product_name", ""), "shop": p.get("shop_name", ""), "preis": f"€{p.get('price_value', 0):.2f}".replace(".", ","),
            "gmv": _kurz(p.get("gmv"), True), "verkauft": str(p.get("units_sold") or 0), "id": str(p.get("product_id", "")),
            "bild": p.get("product_image_url", "")}
           for p in ((roh.get("data") or {}).get("results") or [])]
    erg.sort(key=lambda p: int(p["verkauft"]), reverse=True)
    return erg[:n]


def _de_zeigen(suchwort, erg):
    print(f"== {suchwort}")
    for p in erg:
        print(f"{p['verkauft']:>6} verkauft | {p['preis']:>8} | {p['name'][:90]} | id {p['id']}")
    if not erg:
        print("NICHTS in DE gefunden")


def de_suche(suchwort, n=5):
    """Gibt es das Produkt (oder ein ähnliches) im TikTok Shop DE? Direkt über Social1 (searchProducts, Region DE), Bestseller zuerst."""
    aktionen_laden()
    erg = _de_treffer(s1("searchProducts", {"query": suchwort, "region": "de"}), n)
    _de_zeigen(suchwort, erg)
    return erg


def de_suche_viele(woerter, n=5):
    """Viele Suchwörter auf einmal (eine Zeile pro Wort in einer Datei) – für den USA-Check."""
    aktionen_laden()
    for w, roh in zip(woerter, s1_viele("searchProducts", [[{"query": w, "region": "de"}] for w in woerter])):
        _de_zeigen(w, _de_treffer(roh, n))


AMZ = "https://www.amazon.es"


def _amz_async(js_promise_body, warte=60):
    """Async-JS im Amazon-Fenster: Ergebnis (String) über window-Variable abholen. Kein Seitenwechsel, keine Klicks."""
    k = f"a{time.time_ns()}"
    start = _doc_js(AMZ, f"""(()=>{{window.__amz=window.__amz||{{}};const k={json.dumps(k)};window.__amz[k]=null;
(async()=>{{{js_promise_body}}})().then(v=>window.__amz[k]=String(v)).catch(e=>window.__amz[k]=JSON.stringify({{fehler:String(e)}}));return 1}})()""", AMZ)
    if start not in ("1", "1.0"):
        raise RuntimeError(f"Amazon: Befehl startete nicht ({start[:80]!r})")
    for _ in range(warte * 2):
        time.sleep(0.5)
        r = _doc_js(AMZ, f"(()=>{{const v=(window.__amz||{{}})[{json.dumps(k)}];if(v!==null&&v!==undefined)delete window.__amz[{json.dumps(k)}];return v===null||v===undefined?'':v}})()", AMZ)
        if r:
            return r
    raise Haenger()


JS_AMZ_CAPTCHA = r"""const cap=t=>/validateCaptcha|Introduce los caracteres|api-services-support@amazon|Type the characters/i.test(t);"""


def amazon_suche_viele(woerter, n=5):
    """Amazon.es direkt durchsuchen (nur lesen): je Suchwort die Treffer ohne Werbung – ASIN, Preis, Bewertungen, Titel."""
    js = JS_AMZ_CAPTCHA + f"""const W={json.dumps(woerter, ensure_ascii=False)};const out=[];
for(const w of W){{const t=await (await fetch('/s?k='+encodeURIComponent(w),{{credentials:'same-origin'}})).text();
 if(cap(t)) return JSON.stringify({{captcha:true}});
 const d=new DOMParser().parseFromString(t,'text/html');
 out.push([...d.querySelectorAll('div[data-component-type="s-search-result"]')].filter(x=>x.dataset.asin&&!/Patrocinado/.test(x.innerText||x.textContent))
  .slice(0,12).map(x=>({{asin:x.dataset.asin,titel:((x.querySelector('h2')||{{}}).textContent||'').trim(),
   preis:((x.querySelector('.a-price .a-offscreen')||{{}}).textContent||'').trim(),
   bewertungen:((x.querySelector('[aria-label*="valoraciones"],[aria-label*="calificaciones"],a[href*="customerReviews"] span')||{{}}).textContent||'').trim(),
   bild:((x.querySelector('img.s-image')||{{}}).src||'')}})));
 await new Promise(r=>setTimeout(r,800));}}
return JSON.stringify({{erg:out}});"""
    r = json.loads(_amz_async(js, warte=30 + 10 * len(woerter)))
    if r.get("captcha"):
        sys.exit("STOPP Amazon zeigt eine Robot-Prüfung (Captcha) – macht Artur, danach neu starten")
    if r.get("fehler"):
        sys.exit(f"STOPP Amazon: {r['fehler'][:150]}")
    alle = []
    for w, erg in zip(woerter, r["erg"]):
        print(f"== {w}")
        for p in erg[:n]:
            print(f"{p['asin']} | {p['preis']:>9} | {p['bewertungen']:>8} | {p['titel'][:90]}")
        if not erg:
            print("NICHTS auf Amazon.es gefunden")
        alle.append(erg[:n])
    return alle


def amazon_suche(suchwort, n=5):
    return amazon_suche_viele([suchwort], n)[0]


def amazon_wagen(asin, nur_pruefen=False):
    """Produkt per ASIN direkt in den Amazon.es-Einkaufswagen: Produktseite im Hintergrund laden, NUR das Formular
    „In den Einkaufswagen“ (#addToCart) absenden. Nie „Comprar ya“/Kasse. nur_pruefen=True: Formular nur lesen, nichts senden."""
    js = JS_AMZ_CAPTCHA + f"""const t=await (await fetch('/dp/{asin}',{{credentials:'same-origin'}})).text();
if(cap(t)) return JSON.stringify({{captcha:true}});
const d=new DOMParser().parseFromString(t,'text/html');
const titel=((d.querySelector('#productTitle')||{{}}).textContent||'').trim();
const f=d.querySelector('form#addToCart');
if(!f||!d.querySelector('#add-to-cart-button')) return JSON.stringify({{titel,kein_knopf:true}});
const fd=new FormData();
for(const e of f.querySelectorAll('input[name]')){{const n=e.name;
 if(/buy-now|buyNow|checkout|1-click|oneClick/i.test(n))continue;
 if((e.type=='checkbox'||e.type=='radio')&&!e.checked)continue;
 if(e.type=='submit'||e.type=='image')continue; fd.append(n,e.value);}}
fd.set('submit.add-to-cart','Añadir a la cesta');
const ziel=new URL(f.getAttribute('action')||'/cart/add-to-cart/ref=dp_start-bbf_1_glance',location.origin).href;
const pfad=new URL(ziel).pathname;if(!ziel.startsWith(location.origin)||/checkout|spc|buy-now|buynow|1-click|oneclick/i.test(ziel)||!/^\/(gp\/product\/handle-buy-box|cart\/add-to-cart|gp\/add-to-cart)/.test(pfad)) return JSON.stringify({{titel,falsches_ziel:ziel}});
if({'true' if nur_pruefen else 'false'}) return JSON.stringify({{titel,pruefen:true,ziel,felder:[...fd.keys()]}});
const a=await (await fetch(ziel,{{method:'POST',body:fd,credentials:'same-origin'}})).text();
if(cap(a)) return JSON.stringify({{captcha:true}});
const n=await (await fetch('/gp/cart/view.html',{{credentials:'same-origin'}})).text();
const drin=n.includes('{asin}');
return JSON.stringify({{titel,drin,antwort_ok:/Añadido a la cesta|Agregado a la cesta|Subtotal/i.test(a)}});"""
    r = json.loads(_amz_async(js))
    if r.get("captcha"):
        sys.exit("STOPP Amazon zeigt eine Robot-Prüfung (Captcha) – macht Artur, danach neu starten")
    if r.get("fehler"):
        sys.exit(f"STOPP Amazon: {r['fehler'][:150]}")
    if r.get("falsches_ziel"):
        sys.exit(f"STOPP Amazon: Formular zeigt nicht auf den Einkaufswagen ({r['falsches_ziel'][:80]}) – nichts gesendet")
    if r.get("kein_knopf"):
        return print(f"{asin}: kein „In den Einkaufswagen“ (nicht lieferbar/Variante wählen?) – übersprungen | {r.get('titel','')[:70]}")
    if r.get("pruefen"):
        return print(f"{asin}: Formular ok → {r['ziel'][:70]} | {len(r['felder'])} Felder: {', '.join(r['felder'][:12])} | {r['titel'][:60]}")
    print(f"{asin}: {'IM EINKAUFSWAGEN' if r.get('drin') else 'unklar – im Einkaufswagen nicht gefunden'} | {r.get('titel','')[:80]}")
    return bool(r.get("drin"))


def bildvergleich(land, datei, pro_blatt=4):
    """Bildvergleich (Artur 19.11.: Bildersuche nur bei TikTok Shop + Amazon.es, kein Google): je Kandidat mit dem kopierten
    Social1-Produktnamen (+ gekürzt) und den Zusatzwörtern aus `datei` (JSON {"nr": ["wort", …]}, darf leer sein: {"nr": []})
    im TikTok Shop DE (Social1 searchProducts) und – wenn aktiv – auf Amazon.es (voller Name) suchen,
    dann Sammelbild: Zeile = US-Produktbild + Top-Treffer (TT1… = TikTok Shop DE nach Verkäufen, AZ1… = Amazon.es).
    Claude entscheidet am Bild: gleich / ähnlich / gibt's nicht. Treffer-Liste: <land>-vergleich.json."""
    wuensche = json.loads(pathlib.Path(datei).read_text())
    kand = {str(k["nr"]): k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    aktionen_laden()

    def namens_suchen(name):
        """Artur 19.11.: Produktname von Social1 übernehmen. Social1 sucht streng (jedes Wort muss passen) → auch kürzer."""
        n = re.sub(r"【[^】]*】|\[[^\]]*\]", " ", name)
        w = n.split()
        return [x for x in dict.fromkeys([" ".join(w[:12]), " ".join(w[:4]), " ".join(w[:3]), " ".join(w[:2])]) if x]

    paare = [(nr, w) for nr, ws in wuensche.items()
             for w in dict.fromkeys(namens_suchen(kand[str(nr)]["produkt"]) if str(nr) in kand else []).keys()
             | dict.fromkeys(ws if isinstance(ws, list) else [ws]).keys()]
    antworten = s1_viele("searchProducts", [[{"query": w, "region": "de"}] for _, w in paare])
    tt = {}
    for (nr, w), roh in zip(paare, antworten):
        for p in _de_treffer(roh, 6):
            if p["id"] not in {x["id"] for x in tt.setdefault(nr, [])}:
                tt[nr].append(p)
    az = {}
    if REGELN.get("amazon_aktiv", True):
        erst = {nr: " ".join(kand[str(nr)]["produkt"].split()[:12]) for nr in wuensche if str(nr) in kand}   # kopierter Name
        for nr, erg in zip(erst, amazon_suche_viele(list(erst.values()), 3)):
            az[nr] = erg
    bilder = ORDNER / f"{land}-vergleich-bilder"
    bilder.mkdir(exist_ok=True)

    def laden(url, name):
        f = bilder / f"{name}.jpg"
        if url and not f.exists():
            try:
                f.write_bytes(urllib.request.urlopen(url, timeout=20).read())   # ohne Zeitlimit hing es 20.11. 8 h
            except Exception:
                pass
        return str(f)

    ergebnis, zeilen = {}, []
    for nr in wuensche:
        k = kand.get(str(nr))
        if not k:
            continue
        tts = sorted(tt.get(nr, []), key=lambda p: int(p["verkauft"]), reverse=True)[:4 if not az else 3]
        azs = az.get(nr, [])[:5 - 1 - len(tts)]
        zeile = [(laden(k["produkt_bild"], f"us-{nr}"), f"Nr {nr} US")]
        zeile += [(laden(p["bild"], f"tt-{p['id']}"), f"TT{i} {p['verkauft']}x") for i, p in enumerate(tts, 1)]
        zeile += [(laden(p.get("bild"), f"az-{p['asin']}"), f"AZ{i} {p['preis']}") for i, p in enumerate(azs, 1)]
        zeile += [("", "")] * (5 - len(zeile))
        zeilen.append(zeile)
        ergebnis[nr] = {"us": k["produkt"], "tiktok": {f"TT{i}": p for i, p in enumerate(tts, 1)},
                        "amazon": {f"AZ{i}": p for i, p in enumerate(azs, 1)}}
    (ORDNER / f"{land}-vergleich.json").write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1))
    if not BLATT.exists():
        subprocess.run(["zsh", str(PROJ / "werkzeuge" / "build.sh")], check=True)
    for b in range(math.ceil(len(zeilen) / pro_blatt)):
        args = [x for z in zeilen[b * pro_blatt:(b + 1) * pro_blatt] for paar in z for x in paar]
        aus = ORDNER / f"{land}-vergleich-{b + 1:02d}.jpg"
        subprocess.run([str(BLATT), str(aus), "5", *args], check=True)
        print(f"{aus.name}: Nr {', '.join(list(wuensche)[b * pro_blatt:(b + 1) * pro_blatt])}")
    print(f"FERTIG bildvergleich {land.upper()}: {len(zeilen)} Produkte → {land}-vergleich.json")


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
    """Stündlich (launchd): Seite 1 DE + US direkt lesen und protokollieren → erkennen, wann Social1 seine Zahlen erneuert."""
    if sperre_aktiv():
        return print("Research läuft gerade – Messung ausgelassen")
    sperre_setzen()
    zeile = {"zeit": time.strftime("%Y-%m-%d %H:%M")}
    aktionen_laden()
    for land in ("de", "us"):
        karten, _ = top_videos(land, 1)
        zeile[land] = [[k["video_id"], k["plus_views"], k["views"]] for k in karten]
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
    """Platzierung: Frische zählt am meisten (Today/Yesterday), dann Tempo, Video-Umsatz, Interaktion.
    Artur 20.11.: Creator-GMV und 🔥 raus (sagen nichts übers Video), dafür Umsatz genau dieses Videos."""
    frische = {0: 100, 1: 85, 2: 55, 3: 40, 4: 30, 5: 22, 6: 16, 7: 12}.get(k.get("tage", 999), max(0, 10 - k.get("tage", 999) // 7))
    tempo = min(40, 8 * math.log10(max(1, zahl(k["plus_views"]))) - 24)      # 100K → 16, 1M → 24, 10M → 32
    umsatz = min(15, 3 * math.log10(max(1, float(k.get("video_gmv") or 0))) - 3)   # €100 → 3, €1K → 6, €10K → 9, €100K → 12
    v = max(1, zahl(k["views"]))
    inter = min(15, 100 * (zahl(k["likes"]) + 3 * zahl(k["kommentare"])) / v)
    return round(frische + max(0, tempo) + max(0, umsatz) + inter, 1)


def rangliste(land):
    sort = json.loads((ORDNER / f"{land}-sortiert.json").read_text())   # {"nr": "BOF"|"SLIDES"|"QUALITY", ...}
    kand = {str(k["nr"]): k for k in json.loads((ORDNER / f"{land}-kandidaten.json").read_text())}
    gemacht = set()   # Artur 20.11.: Hinweis „Produkt schon verlinkt“ weglassen (bringt nichts); gepostete_produkte() bleibt für später
    zeilen = sorted(((punkte(kand[n]), n, art) for n, art in sort.items() if n in kand and not art.endswith("?")
                     and int(kand[n].get("seite") or 0) <= seiten_max(f"{art.split('+')[0]} {land.upper()}")),   # wie speichern
                    reverse=True)   # Gleichstand: Nr als Text absteigend – sortieren nutzt denselben Schlüssel
    # Artur 20.11.2026: jede Liste (BOF, SLIDES, REACTIONS, QUALITY) zusätzlich als eigene Datei, Platz-Nr. je Datei neu
    arten = sorted({t for z in zeilen for t in z[2].split("+")})
    for endung, zusatz, teil in [("", "", zeilen)] + [(f"-{a.lower()}", f" – {a}", [z for z in zeilen if a in z[2].split("+")])
                                                      for a in arten]:
        aus = [f"# Rangliste {land.upper()} {HEUTE.strftime('%d.%m.%Y')}{zusatz}", "",
               "| Platz | Punkte | Liste | Alter | +Views | Produkt | Creator | Link |", "|---|---|---|---|---|---|---|---|"]
        for i, (p, n, art) in enumerate(teil, 1):
            k = kand[n]
            if k["produkt_id"] in gemacht:
                art += " (Produkt schon verlinkt)"
            aus.append(f"| {i} | {p} | {art} | {k['alter']} | {k['plus_views']} | {k['produkt'][:50].replace('|', '/')} | @{k['creator']} | "
                       f"https://www.tiktok.com/@{k['creator']}/video/{k['video_id']} |")
        f = ORDNER / f"{land}-rangliste{endung}.md"
        f.write_text("\n".join(aus) + "\n")
        # Artur 20.11.2026: Rangliste als Seite mit Vorschaubildern (Social1-Vorschau, sonst <land>-bilder/)
        esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        karten = []
        for i, (p, n, art) in enumerate(teil, 1):
            k = kand[n]
            bild, lokal = k["vorschau"], f"{land}-bilder/{k['video_id']}.jpg"
            schon = " schon" if k["produkt_id"] in gemacht else ""
            karten.append(f'<a class="k{schon}" href="https://www.tiktok.com/@{esc(k["creator"])}/video/{k["video_id"]}" target="_blank">'
                          f'<img loading="lazy" src="{esc(bild)}" onerror="this.onerror=null;this.src=\'{lokal}\'" alt=""><b>{i}</b><i>{esc(art)}</i>'
                          f'<span>{esc(k["alter"])} · +{esc(k["plus_views"])}{" · Produkt schon verlinkt" if schon else ""}</span>'
                          f'<span class="p">{esc(k["produkt"][:70])}</span><span>@{esc(k["creator"])} · Seite {esc(k.get("seite", "?"))}</span></a>')
        titel = f"Rangliste {land.upper()} {HEUTE.strftime('%d.%m.%Y')}{zusatz}"
        (ORDNER / f"{land}-rangliste{endung}.html").write_text(
            f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{titel}</title><style>'
            'body{font:13px -apple-system,sans-serif;margin:16px;background:#fff;color:#111}'
            '@media(prefers-color-scheme:dark){body{background:#111;color:#eee}.k{background:#222!important}}'
            '.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}'
            '.k{position:relative;display:flex;flex-direction:column;gap:2px;background:#f3f3f3;border-radius:8px;overflow:hidden;'
            'color:inherit;text-decoration:none;padding-bottom:6px}.k span,.k i{padding:0 6px}.k.schon{opacity:.55}'
            '.k img{width:100%;aspect-ratio:9/16;object-fit:cover;background:#999}.p{font-weight:600}'
            '.k b{position:absolute;top:6px;left:6px;background:#000c;color:#fe2c55;padding:2px 7px;border-radius:6px;font-size:15px}'
            f'</style><h1>{titel}</h1><p>{len(teil)} Videos · Platz 1 = beste Punkte · blass = Produkt schon verlinkt (Video trotzdem machen) · '
            f'Klick öffnet TikTok</p><div class="g">{"".join(karten)}</div>')
        print("\n".join(aus[4:14]))
        print(f"FERTIG rangliste: {f}")
    personen_und_desktop(land, zeilen, kand, gemacht)


def pdf_machen(html, ziel):
    """Artur 20.11.: PDF in iPhone-Breite (Links funktionieren auch in der WhatsApp/AirDrop-Vorschau, HTML-Links dort nicht)."""
    chrome = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if not chrome.exists():
        return print("Hinweis: kein Google Chrome → keine PDF")
    tmp = ORDNER / "_pdf.html"
    tmp.write_text(html.replace("</style>", "@page{size:430px 932px;margin:0}th{position:static}tr.fertig td{opacity:1}</style>"))
    subprocess.run([str(chrome), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={ziel}",
                    tmp.as_uri()], capture_output=True, timeout=90)
    tmp.unlink(missing_ok=True)


PERSONEN = ("Artur", "Andreas")                               # Artur 20.11.2026: teilen sich BOF/Reactions/Quality


def personen_und_desktop(land, zeilen, kand, gemacht):
    """Alles außer SLIDES auf PERSONEN aufteilen (nur .md): abwechselnd nach Platz, gleiches Produkt immer zur selben Person.
    Personen- + SLIDES-Datei als einfache Liste (keine Tabelle – Artur 20.11.: iPhone/WhatsApp zeigen .md als reinen Text)
    → uebergabe/research/<datum>/ und ~/Documents/Ranglisten/<JJJJ-MM-TT>/."""
    skr = {}                                                   # Artur 20.11.: fremdsprachige → Badge + deutsches Skript
    sf = ORDNER / f"SKRIPTE {HEUTE.strftime('%d.%m.%Y')}.md"
    if sf.exists():
        for blk in sf.read_text().split("<!-- ")[1:]:
            v, spr = re.search(r"/video/(\d+)", blk), re.search(r"Sprache (\w+)", blk)
            if v and "**DEUTSCH:**" in blk:
                skr[v.group(1)] = ((spr.group(1) if spr else "?").upper(), blk.split("**DEUTSCH:**", 1)[1].strip())

    musik = set()                                              # Artur 20.11.: BOF nur mit Musik → Standard-Skripte
    for f in (ORDNER / f"{land}-transkripte").glob("*.json"):
        t = json.loads(f.read_text())
        if len(t.get("text", "")) < 30 and f.stem in kand:
            musik.add(kand[f.stem]["video_id"])
    for blk in (sf.read_text().split("<!-- ")[1:] if sf.exists() else []):
        if "nur Musik" in blk and (v := re.search(r"/video/(\d+)", blk)):
            musik.add(v.group(1))

    def standard(k):
        name, preis = "(Produkt)", "(Preis)"                    # Artur 20.11.: Platzhalter – Produkt und Preis schaut er selbst nach
        s = [("Normales Standard-Skript", f"TikTok Shop verschenkt einfach fast ihren {name}. Leute, den gibt's grade für {preis}, das ist kein Fake. "
             f"Ich hab selber nachgeschaut, unten links jetzt abchecken. Das muss ein Preisfehler sein, die müssen doch insolvent gehen, digga was?")]
        if HEUTE <= date(2026, 12, 1):                         # nur während Black Friday / Cyber Monday
            s.insert(0, ("Black-Friday-Skript", f"Für die nächsten 24h gibt's diesen {name} zu diesem Preis hier. Aktuell gibt es geisteskranke Angebote, "
                        f"weil die Black Friday Kampagne läuft. Deswegen seid so schnell wie möglich und klickt hier unten links auf den "
                        f"orangenen Einkaufswagen, bevor die wieder weg sind."))
        return s

    def ist_musik_bof(z):
        return "BOF" in z[2].split("+") and kand[z[1]]["video_id"] in musik and kand[z[1]]["video_id"] not in skr

    def schoen(name):                                          # Artur 20.11.: „2026-11-20 DE Artur.html“ statt „de-rangliste-artur.html“
        l, wer, endung = re.match(r"(\w+)-rangliste-(\w+)\.(\w+)$", name).groups()
        return f"{HEUTE.isoformat()} {'DE' if l == 'de' else 'USA'} {wer.upper() if wer == 'slides' else wer.capitalize()}.{endung}"

    def eintrag(i, z):
        if ist_musik_bof(z):
            return eintrag_ohne(i, z)[:-1] + ["🎵 **Nur Musik – Standard-Skripte:**", ""] + [
                x for n, t in standard(kand[z[1]]) for x in (f"> **{n}:** {t}", ">")][:-1] + [""]
        e = eintrag_ohne(i, z)
        v = kand[z[1]]["video_id"]
        if v not in skr:
            return e
        e = e[:-1] + [f"🌐 **{skr[v][0]} – Skript auf Deutsch:**", ""] + [f"> {l}  " if l else ">" for l in skr[v][1].splitlines()] + [""]
        if "nur musik" in skr[v][1].lower():                   # Artur 20.11.: bei „nur Musik“ die 2 Standard-Skripte dazu
            e += ["🎵 **Standard-Skripte:**", ""] + [x for n, t in standard(kand[z[1]]) for x in (f"> **{n}:** {t}", ">")][:-1] + [""]
        return e

    def eintrag_ohne(i, z):
        pk, n, art = z
        k = kand[n]
        schon = " · ⚠️ Produkt schon verlinkt (Video trotzdem machen)" if k["produkt_id"] in gemacht else ""
        return [f"**{i}. {k['produkt'][:60]}**  ", f"{art} · {k['alter']} · +{k['plus_views']} · @{k['creator']}{schon}  ",
                f"https://www.tiktok.com/@{k['creator']}/video/{k['video_id']}", ""]
    datum = HEUTE.strftime('%d.%m.%Y')
    aus, abschnitte = {p: [] for p in PERSONEN}, {p: [] for p in PERSONEN}
    arten = sorted({t for z in zeilen for t in z[2].split("+")} - {"SLIDES"})
    for a in arten:
        wem, teil = {}, {p: [] for p in PERSONEN}
        for z in zeilen:
            if a not in z[2].split("+"):
                continue
            pid = kand[z[1]]["produkt_id"]
            p = wem.setdefault(pid, min(PERSONEN, key=lambda x: len(teil[x])))
            teil[p].append(z)
        for p in PERSONEN:
            abschnitte[p].append((a, teil[p]))
            aus[p] += [f"## {a} ({len(teil[p])})", ""] + [x for i, z in enumerate(teil[p], 1) for x in eintrag(i, z)]
    dateien = {f"{land}-rangliste-{p.lower()}.md": f"# {land.upper()} {datum} – {p}\n\nGleiches Produkt steht immer nur bei einer Person.\n\n"
               + "\n".join(aus[p]) for p in PERSONEN}
    slides = [z for z in zeilen if "SLIDES" in z[2].split("+")]
    dateien[f"{land}-rangliste-slides.md"] = (f"# {land.upper()} {datum} – SLIDES ({len(slides)})\n\n"
                                              + "\n".join(x for i, z in enumerate(slides, 1) for x in eintrag(i, z)))
    desk = pathlib.Path.home() / "Documents" / "Ranglisten" / HEUTE.isoformat()      # Artur 20.11.: Dokumente, ein Ordner pro Tag
    desk.mkdir(parents=True, exist_ok=True)
    for name, text in dateien.items():
        (ORDNER / name).write_text(text)
        # Artur 20.11.: .md nur im Projekt – in Dokumente nur die endgültige Version (HTML + PDF)
    # Artur 20.11.: dieselben Dateien als HTML-Tabelle (iPhone-Vorschau in WhatsApp/AirDrop/Dateien), Produkt = Link
    esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    def badge(k, art=""):
        v = k["video_id"]
        knopf = lambda t: f'<span class="chip sp">{t}</span>'
        if v in skr:
            return knopf(f"🌐 {skr[v][0]} · Skript")
        return knopf("🎵 Standard-Skript") if "BOF" in art.split("+") and v in musik else ""

    def skript(k, art=""):
        if k["video_id"] in musik and k["video_id"] not in skr and "BOF" in art.split("+"):
            t = "".join(f"<p><b>{n}:</b> {esc(x)}</p>" for n, x in standard(k))
            return (f'<tr class="skr"><td></td><td colspan="3"><details id="s{k["video_id"]}"><summary>Nur Musik – Standard-Skripte</summary>'
                    f'<div>{t}</div></details></td></tr>')
        if k["video_id"] not in skr:
            return ""
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(skr[k["video_id"]][1])).replace("\n", "<br>")
        if "nur musik" in skr[k["video_id"]][1].lower():      # Artur 20.11.: bei „nur Musik“ die 2 Standard-Skripte dazu
            t += '<p style="margin-top:10px;color:#ffcc66">Standard-Skripte</p>' + "".join(
                f"<p><b>{n}:</b> {esc(x)}</p>" for n, x in standard(k))
        return (f'<tr class="skr"><td></td><td colspan="3"><details id="s{k["video_id"]}"><summary>Skript auf Deutsch</summary>'
                f'<div>{t}</div></details></td></tr>')

    def tabelle(teil):
        r = ["<table><tr><th>#</th><th>Produkt</th><th>Alter</th><th>+Views</th></tr>"]
        for i, (pk, n, art) in enumerate(teil, 1):
            k = kand[n]
            alt = {"Today": "neu", "Yesterday": "gestern"}.get(k["alter"], "alt")
            r.append(f'<tr><td><label class="hk"><input type="checkbox" data-v="{k["video_id"]}"><span class="nr">{i}</span></label></td><td><a href="https://www.tiktok.com/@{esc(k["creator"])}/video/{k["video_id"]}">'
                     f'{esc(k["produkt"][:60])}</a><div class="sub"><span class="chip">{esc(art)}</span>{badge(k, art)}'
                     f'<span class="cr">@{esc(k["creator"])}</span></div></td><td><span class="chip {alt}">{esc(k["alter"])}</span></td>'
                     f'<td class="v">{esc(k["plus_views"])}</td></tr>' + skript(k, art))
        return "".join(r) + "</table>"
    # Artur 20.11.: Daten für die Online-Seite (claude.ai, fester Link) – werkzeuge/ranglisten_seite.py veröffentlicht sie
    def roh(i, z):
        pk, n, art = z
        k, v = kand[n], kand[n]["video_id"]
        nur_musik = (v in skr and "nur musik" in skr[v][1].lower()) or ("BOF" in art.split("+") and v in musik and v not in skr)
        return {"nr": i, "v": v, "produkt": k["produkt"][:90], "art": art, "alter": k["alter"], "plus": k["plus_views"],
                "creator": k["creator"], "url": f"https://www.tiktok.com/@{k['creator']}/video/{v}",
                "sprache": skr[v][0] if v in skr else "", "skript": skr[v][1] if v in skr else "",
                "standard": [list(x) for x in standard(k)] if nur_musik else []}
    seite = PROJ / "uebergabe" / "ranglisten-seite"
    seite.mkdir(parents=True, exist_ok=True)
    (seite / f"daten-{land}.json").write_text(json.dumps({
        "land": land.upper(), "datum": datum, "stand": time.strftime("%d.%m.%Y %H:%M"),
        "listen": {**{p: [{"titel": a, "videos": [roh(i, z) for i, z in enumerate(t, 1)]} for a, t in abschnitte[p]] for p in PERSONEN},
                   "SLIDES": [{"titel": "SLIDES", "videos": [roh(i, z) for i, z in enumerate(slides, 1)]}]}}, ensure_ascii=False))
    seiten = {p: "".join(f"<h2>{a} ({len(t)})</h2>{tabelle(t)}" for a, t in abschnitte[p]) for p in PERSONEN}
    seiten["slides"] = f"<h2>SLIDES ({len(slides)})</h2>{tabelle(slides)}"
    for wer, inhalt in seiten.items():
        titel = f"{land.upper()} {datum} – {wer if wer != 'slides' else 'SLIDES'}"
        html = (f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{titel}</title>'
                # Artur 20.11.: immer dunkel – iPhone-Vorschau (WhatsApp/AirDrop) beachtet den Dunkelmodus nicht
                # Artur 20.11.: Graphit-Tabelle wie sein Dock + leichte Farben aus seiner statsKMH-App (Grün, Türkis, Blau)
                '<meta name="color-scheme" content="dark"><style>:root{--bg:#161618;--fg:#ececee;--mut:#8e8e93;--line:#2a2a2d;'
                '--kopf:#1f1f22;--chip:#2c2c2f;--glas:linear-gradient(180deg,#4a4a4e,#2a2a2d);--gruen:#4cd964;--tuerkis:#5ac8c8;--blau:#64a8ff}'
                'html{background:#161618}body{font:15px -apple-system,sans-serif;margin:0;padding:14px 12px 40px;background:var(--bg);color:var(--fg)}'
                'h1{font-size:22px;font-weight:700;margin:4px 0 2px;color:#fff}.st{color:var(--mut);font-size:13px;margin:0 0 4px}'
                'h2{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--gruen);margin:22px 0 6px}'
                'table{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed}th:nth-child(1){width:38px}input{position:absolute;opacity:0;width:0;height:0}.hk{cursor:pointer}input:checked+.nr{background:#4cd964;color:#000}tr.fertig td:not(:first-child){opacity:.35}tr.fertig a{text-decoration:line-through}th:nth-child(3){width:76px}th:nth-child(4){width:58px}td{overflow-wrap:anywhere}th{position:sticky;top:0;background:var(--kopf);color:var(--mut);font-size:11px;'
                'text-transform:uppercase;letter-spacing:.06em;text-align:left;padding:8px 6px;z-index:1;border-bottom:1px solid var(--line)}'
                'td{padding:10px 6px;border-bottom:1px solid var(--line);vertical-align:top}'
                '.nr{display:inline-block;min-width:28px;text-align:center;padding:4px 0;border-radius:9px;background:var(--glas);'
                'box-shadow:inset 0 1px 0 #ffffff26,0 1px 2px #0008;color:#fff;font-weight:700;font-size:13px}'
                'a{color:var(--fg);font-weight:600;text-decoration:none;line-height:1.3}.sub{margin-top:5px;display:flex;flex-wrap:wrap;gap:5px;align-items:center}'
                '.chip{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--chip);color:var(--blau);white-space:nowrap;font-weight:500;'
                'box-shadow:inset 0 1px 0 #ffffff12}.chip.neu{color:var(--gruen);background:#4cd96422}.chip.gestern{color:var(--tuerkis);background:#5ac8c81a}'
                '.chip.alt{color:var(--mut)}.chip.sp{color:#ffcc66;background:#ffcc661c}.cr{font-size:12px;color:var(--mut)}'
                '.v{font-weight:700;color:#fff;white-space:nowrap}tr.skr td{padding-top:0}tr:has(+tr.skr) td{border-bottom:0}'
                'details{background:#1f1f22;border-radius:12px;padding:10px 12px;font-size:14px;line-height:1.45}'
                'summary{color:#ffcc66;font-size:13px;font-weight:600}details[open] summary{margin-bottom:6px}details p{margin:0 0 8px}'
                f'</style><h1>{wer if wer != "slides" else "SLIDES"}</h1><p class="st">Rangliste {land.upper()} · {datum} · Nummer antippen = erledigt</p>{inhalt}'
                # Artur 20.11.: Haken nur für ihn/Andreas, pro Gerät gemerkt (localStorage, klappt in Safari, nicht in der WhatsApp-Vorschau)
                '<script>const K=document.title;let h={};try{h=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}'
                'document.querySelectorAll("input[data-v]").forEach(c=>{const z=c.closest("tr");c.checked=!!h[c.dataset.v];'
                'z.classList.toggle("fertig",c.checked);c.onchange=()=>{h[c.dataset.v]=c.checked;z.classList.toggle("fertig",c.checked);'
                'try{localStorage.setItem(K,JSON.stringify(h))}catch(e){}}})</script>')
        name = f"{land}-rangliste-{wer.lower()}.html"
        (ORDNER / name).write_text(html)
        (desk / schoen(name)).write_text(html)
        # Artur 20.11.: nur HTML im Ordner (pdf_machen() bleibt als Reserve)
    # Artur 20.11.: nur die aktuelle Version – überschreiben statt vorher löschen (sonst legt iCloud „… 2.html“-Kopien an),
    # danach alles vom Land weg, was diesmal nicht geschrieben wurde (alte Formate, iCloud-Kopien)
    neu = {schoen(f"{land}-rangliste-{w.lower()}.html") for w in seiten}
    for alt in desk.glob(f"{HEUTE.isoformat()} {'DE' if land == 'de' else 'USA'} *"):
        if alt.name not in neu:
            alt.unlink()
    print(f"FERTIG Aufteilung {', '.join(PERSONEN)} + Ablage: {desk}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["messen"]:
        mit_neustart(messen)
        sys.exit()
    if a[:1] == ["messung"]:
        messung_auswerten()
        sys.exit()
    if a[:1] == ["vorbilder"]:
        mit_neustart(vorbilder, int(a[a.index("--min") + 1]) if "--min" in a else 30000)
        sys.exit()
    if a[:1] == ["gemacht-abgleich"]:
        mit_neustart(gemacht_abgleich)
        sys.exit()
    if a[:2] == ["de-suche", "--datei"]:                      # eine Zeile pro Suchwort
        mit_neustart(de_suche_viele, [w.strip() for w in pathlib.Path(a[2]).read_text().splitlines() if w.strip()])
        sys.exit()
    if a[:1] == ["de-suche"]:
        mit_neustart(de_suche, " ".join(a[1:]))
        sys.exit()
    if a[:1] in (["amazon"], ["wagen"]) and not REGELN.get("amazon_aktiv", True):
        print("Amazon ist deaktiviert (Artur 19.11.2026, research_regeln.json „amazon_aktiv“) – Schritt übersprungen")
        sys.exit()
    if a[:2] == ["amazon", "--datei"]:                         # eine Zeile pro Suchwort
        mit_neustart(amazon_suche_viele, [w.strip() for w in pathlib.Path(a[2]).read_text().splitlines() if w.strip()])
        sys.exit()
    if a[:1] == ["amazon"]:
        mit_neustart(amazon_suche, " ".join(a[1:]))
        sys.exit()
    if a[:1] == ["wagen"]:
        for asin in [x for x in a[1:] if not x.startswith("--")]:
            mit_neustart(amazon_wagen, asin, "--pruefen" in a)
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
    elif befehl == "sortieren":
        sperre_setzen()
        sortieren(land, a[2])
    elif befehl == "bildvergleich":
        mit_neustart(bildvergleich, land, a[2])
    elif befehl == "skripte":
        skripte(land, int(a[a.index("--top") + 1]) if "--top" in a else 30)
    elif befehl == "skript":
        mit_neustart(skript, land, a[2])
        land_zurueck()
    elif befehl == "rangliste":
        rangliste(land)
    else:
        sys.exit(__doc__)
