#!/usr/bin/env python3
"""Social1-Liste am Mac (Safari, nur lesen) auslesen: welches Video gehört zu welchem Produkt.

  python3 werkzeuge/social1.py <listen-link | listenname> [--bilder]

Ergebnis: uebergabe/ausgang/social1-<listenname>.json mit pro Eintrag
  nr, produkt (voller Name), produkt_id (→ stock.py, posten), tts_link, video_id, tiktok_link, creator, vorschau
Mit --bilder werden die Vorschaubilder nach uebergabe/ausgang/social1-<listenname>/ geladen (Zuordnung per Bild).
Braucht: Safari → Entwickler → „JavaScript von Apple Events erlauben“ (auf dem Mac von Andreas an), Artur bei Social1 eingeloggt.
"""
import json, pathlib, re, subprocess, sys, time, urllib.request

PROJ = pathlib.Path(__file__).resolve().parent.parent
AUS = PROJ / "uebergabe" / "ausgang"

JS_LESEN = r"""JSON.stringify((()=>{
 const titel=(document.querySelector('h1,h2')||{}).innerText||'';
 const karten=[...document.querySelectorAll('[data-slot=card]')];
 return {titel, url: location.href, eintraege: karten.map(k=>{
   const p=k.querySelector('img[src*="/products/"]'); const v=k.querySelector('img[src*="thumbnails/"]');
   const c=[...k.querySelectorAll('button')].map(b=>b.innerText.trim()).find(t=>t.startsWith('@'))||'';
   const pid=p?(p.src.match(/products\/(\d+)/)||[])[1]:''; const vid=v?(v.src.match(/thumbnails\/(\d+)/)||[])[1]:'';
   return {produkt:p?p.alt:'', produkt_id:pid||'', video_id:vid||'', creator:c, vorschau:v?v.src:''};})};
})())"""
JS_RUNTER = "window.scrollTo(0, document.body.scrollHeight); document.querySelectorAll('[data-slot=card]').length"


def safari(js):
    esc = js.replace("\\", "\\\\").replace('"', '\\"')
    r = subprocess.run(["osascript", "-e", f'tell application "Safari" to do JavaScript "{esc}" in front document'],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"STOPP Safari: {r.stderr.strip()}")
    return r.stdout.strip()


def oeffnen(ziel):
    url = ziel if ziel.startswith("http") else "https://www.social1.ai/saved-videos"
    subprocess.run(["osascript", "-e", f'tell application "Safari" to make new document with properties {{URL:"{url}"}}'], capture_output=True)
    time.sleep(7)
    if not ziel.startswith("http"):                          # Liste per Namen in der Übersicht anklicken
        name = json.dumps(ziel)
        safari(f"(()=>{{const el=[...document.querySelectorAll('*')].find(e=>e.childElementCount==0&&e.textContent.trim()=={name});"
               f"if(!el)return 'fehlt';let c=el;while(c&&c.tagName!='A'&&c.tagName!='BUTTON'&&!c.onclick)c=c.parentElement;(c||el).click();return 'ok'}})()")
        time.sleep(7)


def main(a):
    if not a:
        sys.exit(__doc__)
    ziel, bilder = a[0], "--bilder" in a
    oeffnen(ziel)
    vorher, gleich = -1, 0
    for _ in range(60):                                      # nachladen, bis keine neuen Karten mehr kommen
        n = int(float(safari(JS_RUNTER) or 0))
        gleich = gleich + 1 if n == vorher else 0
        if gleich >= 3:
            break
        vorher = n
        time.sleep(1.2)
    d = json.loads(safari(JS_LESEN))
    if not d["eintraege"]:
        sys.exit("STOPP: keine Videos gefunden (eingeloggt? richtige Liste?)")
    name = re.sub(r"[^\w.-]+", "-", d["titel"].strip() or ziel.rstrip("/").split("/")[-1]).strip("-").lower()
    for i, e in enumerate(d["eintraege"], 1):
        e["nr"] = i
        e["tts_link"] = f"https://shop.tiktok.com/view/product/{e['produkt_id']}" if e["produkt_id"] else ""
        e["tiktok_link"] = f"https://www.tiktok.com/{e['creator']}/video/{e['video_id']}" if e["video_id"] else ""
    out = AUS / f"social1-{name}.json"
    out.write_text(json.dumps({"liste": d["titel"], "url": d["url"], "gelesen": time.strftime("%Y-%m-%d %H:%M"),
                               "eintraege": d["eintraege"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    ohne = sum(1 for e in d["eintraege"] if not e["produkt_id"])
    print(f"{len(d['eintraege'])} Videos aus „{d['titel']}“ → {out.relative_to(PROJ)}" + (f" ({ohne} ohne Produkt)" if ohne else ""))
    if bilder:
        o = AUS / f"social1-{name}"; o.mkdir(exist_ok=True)
        for e in d["eintraege"]:
            if e["vorschau"]:
                try:
                    urllib.request.urlretrieve(e["vorschau"], o / f"{e['nr']:03d}-{e['produkt_id']}.jpg")
                except Exception:
                    pass
        print(f"Vorschaubilder → {o.relative_to(PROJ)}")


if __name__ == "__main__":
    main(sys.argv[1:])
