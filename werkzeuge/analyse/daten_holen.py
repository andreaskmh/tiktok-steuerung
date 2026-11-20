#!/usr/bin/env python3
"""Offizielle TikTok-Zahlen von der Seite „Daten“ ablesen (iPhone am Kabel), pro Account.
  TS_IPHONE_UDID=00008030-00096C8621C3402E python3 werkzeuge/analyse/daten_holen.py konto1 [konto2 …]
  --tage N   wie viele Tage rückwärts vollständig sein sollen (Standard 30)
  --neu N    die letzten N Tage immer neu lesen (Standard 6, ältere nur wenn sie fehlen)
Weg: Profil → Konto wechseln → TikTok Shop für Creator*innen → Pfeil neben „Heute | Letzte 7 Tage“ → „Daten“.
Pro Tag (Heute, Gestern = Reiter; ältere über Benutzerdefiniert → Tag; TikTok lässt dort nur Tage bis vorgestern zu):
Schlüsseldaten (GMV, Verkaufte Artikel, Produkt-Sichtkontakte, Produktklicks, Vorauss. Provisionen) + Inhalts-Performance
→ Video (GMV, Ansichten, Artikel). Dazu Video → Alle anzeigen → sortiert nach Aufrufen → Top 25 Videos je Tag (--vtage 7).
  --nur-videos  nur die Video-Listen je Tag lesen
Ergebnis: exporte/<konto>.tage.json + exporte/<konto>.videotage.json (je ein Eintrag pro Tag, wird fortgeschrieben).
Nur lesen – nie „Abheben“, „Kasse“ o. Ä. tippen. Eine Zeile pro Konto, bei Problem STOPP + Foto."""
import os, sys, re, time, json, datetime as D, pathlib
HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent)); sys.path.insert(0, str(HIER))
import kabel as K, seh
from export_holen import Stopp, rot_popup, creator_oeffnen, tipp, warte, tipp_text, tiktok_profil, konto_wechseln, EXP

MONATE = {"jan": 1, "feb": 2, "mär": 3, "mar": 3, "apr": 4, "mai": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10,
          "oct": 10, "nov": 11, "dez": 12, "dec": 12}
SCHLUESSEL = [("GMV", "gmv"), ("Verkaufte Artikel", "artikel"), ("Produkt-Sichtkontakte", "sichtkontakte"),
              ("Produktklicks", "klicks"), ("Vorauss. Provision", "provision")]


def zahl(t):
    """„958,76 €“, „219,5K“, „2,4K €“, „1,2 Mio.“ → (wert, gerundet?)"""
    s = t.replace("€", "").replace(" ", "").replace("O", "0").strip()
    m = re.match(r"^-?([\d.]*\d(?:,\d+)?)(K|Mio\.?|M)?$", s)
    if not m:
        return None
    w = float(m.group(1).replace(".", "").replace(",", "."))
    f = {"K": 1e3, "M": 1e6}.get((m.group(2) or "")[:1], 1)
    return round(w * f, 2), f != 1


def wert_unter(tx, label, xl, yl, spalte=165):
    """Zahl direkt unter einem Label in derselben Spalte."""
    links = xl < spalte
    for t, x, y in sorted(tx, key=lambda e: e[2]):
        if 8 < y - yl < 40 and (x < spalte) == links:
            z = zahl(t)
            if z:
                return z
    return None


def lies_schluessel():
    """Schlüsseldaten oben auf „Daten“ (Seite steht oben)."""
    for _ in range(2):
        tx = seh.lesen()
        out, grob = {}, []
        for label, k in SCHLUESSEL:
            p = seh.finde(label, tx, genau=(label == "GMV"))
            if not p:
                continue
            z = wert_unter(tx, label, *p)
            if z:
                out[k] = z[0]
                if z[1]:
                    grob.append(k)
        if "provision" in out and "gmv" in out:
            if grob:
                out["gerundet"] = grob
            return out
        time.sleep(2)
    raise Stopp("Schlüsseldaten nicht lesbar")


def lies_video():
    """Inhalts-Performance → Video (eine Bildschirmhöhe tiefer), danach wieder nach oben."""
    K.ziehe(167, 600, 167, 250, 0.4); time.sleep(1.8)
    tx = seh.lesen()
    out = {}
    ip = seh.finde("Inhalts-Performance", tx)
    if ip:
        unten = [e for e in tx if e[2] > ip[1]]
        for label, k in (("GMV", "video_gmv"), ("Ansichten", "ansichten"), ("Verkaufte Artikel", "video_artikel")):
            p = seh.finde(label, unten, genau=True)
            if p:
                for t, x, y in sorted(unten, key=lambda e: e[2]):
                    if 8 < y - p[1] < 30 and abs(x - p[0]) < 45:
                        z = zahl(t)
                        if z:
                            out[k] = z[0]; break
    nach_oben()
    return out


def nach_oben():
    for _ in range(2):
        K.ziehe(167, 300, 167, 650, 0.3); time.sleep(0.8)
    time.sleep(0.7)


def datumszeile():
    for t, x, y in seh.lesen():
        if "GMT" in t:
            return t
    return ""


def reiter(name, erwartet=None):
    """Reiter Heute/Gestern/7 Tage oben antippen und warten, bis die Datumszeile passt."""
    p = seh.finde(name, genau=True, ueber=300)
    if not p:
        raise Stopp(f"Reiter „{name}“ fehlt")
    tipp(*p, 2.5)
    pruefe_datum(erwartet)


def pruefe_datum(erwartet):
    if not erwartet:
        return
    for _ in range(8):
        z = datumszeile()
        if tag_passt(z, erwartet):
            time.sleep(0.8)
            return
        time.sleep(0.8)
    raise Stopp(f"Datum {erwartet} nicht übernommen (steht: „{datumszeile()}“)")


def tag_passt(text, d):
    """Steht Tag d am Anfang von text („13. Nov. 2026“)? Erkennung verwechselt in der kleinen Schrift 3 und 5."""
    m = re.match(r"^0?(\d{1,2})\.", text.strip())
    if not m:
        return False
    norm = lambda z: str(z).replace("5", "3")
    return norm(int(m.group(1))) == norm(d.day)


def kalender_tage(tx):
    """Kalender im Blatt lesen → {date: (x, y)}. Tage gehören zum Monatskopf darüber."""
    koepfe = []
    for t, x, y in tx:
        m = re.match(r"^([A-Za-zÄäÖöÜü]{3})[a-zä]*\.? (20\d\d)$", t.strip())
        if m and m.group(1).lower() in MONATE:
            koepfe.append((y, int(m.group(2)), MONATE[m.group(1).lower()]))
    koepfe.sort()
    if not koepfe:
        return {}
    mo = next((y for t, x, y in tx if t.strip() == "Mo"), 0)
    fuss = next((y for t, x, y in tx if "auswählen" in t and y > 450), 9999)
    tage = {}
    for t, x, y in tx:
        if not re.match(r"^\d{1,2}$", t.strip()) or not mo < y < fuss - 15:
            continue
        ueber = [k for k in koepfe if k[0] < y]
        if ueber:
            _, j, m = ueber[-1]
        else:
            _, j, m = koepfe[0]
            j, m = (j, m - 1) if m > 1 else (j - 1, 12)
        try:
            tage[D.date(j, m, int(t))] = (x, y)
        except ValueError:
            pass
    return tage


def tag_waehlen(d):
    """Benutzerdefiniert → Tag → Datum d → Fertig."""
    p = seh.finde("Benutzerdefiniert", ueber=300)
    if not p:
        raise Stopp("„Benutzerdefiniert“ fehlt")
    tipp(*p, 2)
    warte("Datumsbereich", 6)
    tx = seh.lesen()
    q = [(x, y) for t, x, y in tx if t.strip().startswith("Ta") and len(t.strip()) <= 4 and y > 150]   # OCR liest auch „Taд“
    if q:
        tipp(*q[0], 1.5)
    elif not kalender_tage(tx):   # rot markiertes „Tag“ (schon gewählt) liest die Erkennung im Dunkelmodus nicht
        raise Stopp("Auswahl „Tag“ fehlt")
    for _ in range(16):
        tx = seh.lesen()
        if any(tag_passt(t, d) and str(d.year) in t for t, x, y in tx if y > 560):
            break                                             # schon gewählt (rot markierte Zahl liest die Erkennung oft nicht)
        kal = kalender_tage(tx)
        if d in kal:
            time.sleep(0.6)                                   # Kalender steht still? (Nachlauf nach dem Ziehen)
            kal2 = kalender_tage(seh.lesen())
            if kal2.get(d) != kal[d] and d in kal2 and abs(kal2[d][1] - kal[d][1]) > 3:
                continue
            tipp(*kal2.get(d, kal[d]), 1.2)
            tx = seh.lesen()                                  # unten steht der gewählte Tag, z. B. „25. Okt. 2026“
            if any(tag_passt(t, d) and str(d.year) in t for t, x, y in tx if y > 560):
                break
            continue
        mitte = 520
        if kal and d < min(kal):
            K.ziehe(167, mitte - 80, 167, mitte + 80, 0.4)   # weiter zurück
        else:
            K.ziehe(167, mitte + 80, 167, mitte - 80, 0.4)
        time.sleep(1.2)
    else:
        raise Stopp(f"Tag {d} im Kalender nicht gefunden")
    tipp_text("Fertig", w=2.5, genau=True)
    pruefe_datum(d)


def oeffne_daten():
    creator_oeffnen()
    for _ in range(3):                # Werbe-Popup (Artur 20.11.: auf Rot tippen, dann zurück)
        tx = seh.lesen()
        rot = rot_popup(tx) or seh.finde("Aufgaben anzeigen", tx)
        if not rot:
            break
        tipp(*rot, 3); tipp(22, 58, 3)
    warte("Hallo", 15)
    for _ in range(5):
        p = seh.finde("Letzte 7 Tage", ueber=600, unter=110)
        if p:
            break
        K.ziehe(167, 500, 167, 380, 0.4); time.sleep(1.5)
    else:
        raise Stopp("„Letzte 7 Tage“ nicht gefunden")
    tipp(314, p[1], 3)
    warte("Schlüsseldaten", 30)


def lies_tag():
    e = lies_schluessel()
    e.update(lies_video())
    e["gelesen"] = time.strftime("%Y-%m-%d %H:%M")
    return e


def video_liste_oeffnen():
    """Daten → Inhalts-Performance → Video → Alle anzeigen → Filter: Sortieren nach Aufrufe."""
    nach_oben()
    K.ziehe(167, 600, 167, 250, 0.4); time.sleep(1.8)
    tipp_text("Alle anzeigen", w=4)
    warte("Videoanzahl", 12)
    tx = seh.lesen()
    filt = [(x, y) for t, x, y in tx if "Suchen" in t and x > 200]
    tipp(297, filt[0][1] if filt else 429, 2)
    tipp_text("Aufrufe", w=1, genau=True, unter=500)
    tipp_text("Ergebnisse anzeigen", w=4)


def lies_liste(n=25):
    """Video-Liste (Seite „Video“, sortiert nach Aufrufen) von oben lesen → bis n Videos."""
    nach_oben()
    for _ in range(10):                                       # warten, bis die Liste geladen ist
        if not seh.finde("Daten werden geladen"):
            break
        time.sleep(1)
    videos, gesehen = [], set()
    leer = 0
    for _ in range(16):
        tx = sorted(seh.lesen(), key=lambda e: e[2])
        vorher = len(videos)
        for t, x, y in tx:
            m = re.search(r"GMV ?(.+?€).*Aufrufe ?([\d.,]+ ?[KM]?)\s.*Artikel ?(\d+)", t)
            if not m:
                continue
            titel = next((a for a, b, c in reversed(tx) if c < y and y - c < 30 and b > 110), "")
            datum = next((a for a, b, c in tx if b < 75 and -10 < c - y < 60 and re.match(r"^[A-Z][a-z]{2} \d{1,2}$", a.strip())), "")
            g, a = zahl(m.group(1)), zahl(m.group(2))
            schl = (titel[:25], g and g[0], a and a[0])
            if not titel or schl in gesehen:
                if datum:
                    for v in videos:
                        if (v["titel"][:25], v["gmv"], v["aufrufe"]) == schl and not v["datum"]:
                            v["datum"] = datum
                continue
            gesehen.add(schl)
            videos.append({"titel": titel.rstrip(". "), "datum": datum, "gmv": g and g[0], "aufrufe": a and a[0],
                           "artikel": int(m.group(3))})
        if len(videos) >= n:
            break
        leer = leer + 1 if len(videos) == vorher else 0
        if leer >= 2:                                         # Ende der Liste
            break
        K.ziehe(167, 620, 167, 300, 0.4); time.sleep(2)
    return videos[:n]


def videos_pro_tag(k, vtage, neu_n):
    """Pro Tag die Top-Videos nach Aufrufen → exporte/<konto>.videotage.json {tag: [videos]} (fortgeschrieben)."""
    pfad = EXP / f"{k}.videotage.json"
    alt = json.load(open(pfad)) if pfad.exists() else {}
    heute = D.date.today()
    video_liste_oeffnen()
    for n in range(vtage):
        d = heute - D.timedelta(n)
        if n > neu_n and d.isoformat() in alt:
            continue
        nach_oben()
        if n == 0:
            reiter("Heute", d)
        elif n == 1:
            reiter("Gestern", d)
        else:
            tag_waehlen(d)
        alt[d.isoformat()] = lies_liste()
        json.dump(alt, open(pfad, "w"), ensure_ascii=False, indent=0, sort_keys=True)
    return alt


def konto(k, tage_n, neu_n, vtage=7, nur_videos=False):
    pfad = EXP / f"{k}.tage.json"
    alt = json.load(open(pfad)) if pfad.exists() else {}
    heute = D.date.today()
    oeffne_daten()
    if nur_videos:
        vt = videos_pro_tag(k, vtage, min(neu_n, 2))
        print(f"{k}: ok – Videos für {len(vt)} Tage", flush=True)
        return
    reiter("Heute", heute); alt[heute.isoformat()] = dict(lies_tag(), unvollstaendig=True)
    reiter("Gestern", heute - D.timedelta(1)); alt[(heute - D.timedelta(1)).isoformat()] = lies_tag()
    for n in range(2, tage_n):
        d = heute - D.timedelta(n)
        if n > neu_n and d.isoformat() in alt:
            continue
        tag_waehlen(d)
        alt[d.isoformat()] = lies_tag()
        json.dump(alt, open(pfad, "w"), ensure_ascii=False, indent=0, sort_keys=True)
    json.dump(alt, open(pfad, "w"), ensure_ascii=False, indent=0, sort_keys=True)
    vt = videos_pro_tag(k, vtage, 2) if vtage else {}   # --vtage 0 = ohne Video-Listen (Schnell-Aktualisierung)
    g = alt[(heute - D.timedelta(1)).isoformat()]
    print(f"{k}: ok – gestern {g['provision']:.2f} € Provision, {g.get('ansichten', 0):.0f} Aufrufe; "
          f"heute {alt[heute.isoformat()]['provision']:.2f} €; Videos für {len(vt)} Tage", flush=True)


def main(args):
    EXP.mkdir(exist_ok=True)
    tage_n = int(args[args.index("--tage") + 1]) if "--tage" in args else 30
    neu_n = int(args[args.index("--neu") + 1]) if "--neu" in args else 6
    vtage = int(args[args.index("--vtage") + 1]) if "--vtage" in args else 7
    nur_v = "--nur-videos" in args
    konten = [a for i, a in enumerate(args) if not a.startswith("--") and not (i and args[i - 1] in ("--tage", "--neu", "--vtage"))]
    fehler = 0
    for k in konten:
        for versuch in (1, 2):                                # 2. Versuch (TikTok schließt sich manchmal, Tippen geht daneben)
            try:
                tiktok_profil(); konto_wechseln(k)
                konto(k, tage_n, neu_n, vtage, nur_v)
                break
            except (Stopp, K.KabelFehler) as e:
                K.foto(f"/tmp/daten-stopp-{k}.png")
                if versuch == 2:
                    print(f"STOPP {k}: {e} (Foto /tmp/daten-stopp-{k}.png)", flush=True)
                    fehler += 1
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
