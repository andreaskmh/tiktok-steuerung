#!/usr/bin/env python3
"""Foto-Slideshow posten (Artur 17.11.2026) – nutzt den Video-Ablauf aus post_mensch.py, nur die Galerie ist anders.

  python3 werkzeuge/post_slideshow.py "<slideshow-ordner>" --account andreasfastlane [--entwurf] [--ohne-airdrop]

Der Ordner (Editing System, Videos/Slideshows/Auto …/NN Name/) braucht:
  fertig/S_Bild1.jpg …   die fertigen Slides (Reihenfolge = Nummer)
  plan.json              produkt, produkt_id, bilder[0].text (Hook auf Bild 1), optional hashtags, titel, button, brand
Ablauf: Slides mit festem Aufnahmedatum (jpg_datum) per AirDrop → Konto → Produkt in Showcase/Einkaufswagen (wie Video)
→ „+“ → Galerie, Tab „Fotos“, „Mehrere auswählen“ an → die letzten N Kacheln der Reihe nach (Kreise) → „Weiter (N)“
→ Editor (TikTok wählt den Sound selbst, Artur 17.11.) → Weiter → Beschreibung → Link → Entwurf/Veröffentlichen.
Sound: nichts speichern/auswählen (Artur 17.11.2026: „TikTok bestimmt die Musik selbst“).
"""
import json, os, pathlib, random, re, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import post_mensch as M
import bildschirm as B
import seh

BUTTONS = ["Wenige verfügbar", "Fast ausverkauft", "Fast vergriffen", "Wenige auf Lager", "Geringer Bestand"]  # wie einreichen.py; Artur 18.11.: nicht immer „Geringer Bestand“
SLIDES_LISTE = "6afb1c73204ef09999b7948c"          # Social1-Liste „slides“
SPALTEN = (55, 167, 279)                            # Kachel-Mitten (334er Raster)
ZEILE = 112.7                                       # Kachelhöhe inkl. Fuge
KREIS = (42, -37)                                   # Auswahlkreis oben rechts relativ zur Kachelmitte
HOOK = {"text": "", "ok": False}
BIS_EDITOR = "--bis-editor" in sys.argv
FORMAT = {"ok": False}
NEU_GESENDET = {"ja": False}
SENDEN = {"f": lambda *_: None}
ABDRUECKE = []                                      # Bild-Abdrücke der Slides (Reihenfolge = Slide-Nummer)                    # Hook auf Bild 1 – im Editor geprüft (Cover bei Fotos zu klein)


def weiss(c):
    return min(c) >= 248


def kachel_leer(x, yc):
    pts = [(x + dx, yc + dy) for dx in (-35, 0, 35) for dy in (-35, 0, 35)]
    return all(weiss(c) for c in M.farben(*pts))


def letzte_kacheln(n, unten_max):
    """Mitten der letzten n Kacheln (älteste zuerst) im zuletzt gelesenen Bild. unten_max = unterste sichtbare y."""
    ys = list(range(120, int(unten_max), 2))
    spalte = M.farben(*[(SPALTEN[0], y) for y in ys])
    belegt = [y for y, c in zip(ys, spalte) if not weiss(c)]
    if not belegt:
        raise M.Stopp("Galerie: keine Kacheln gefunden")
    unten = belegt[-1]                               # Unterkante der letzten Zeile (Spalte 1 ist dort immer belegt)
    yc = unten - ZEILE / 2 + 1
    in_letzter = 1 + sum(1 for x in SPALTEN[1:] if not kachel_leer(x, yc))
    pos = []
    zeile, spalten = yc, in_letzter
    while len(pos) < n:
        for x in reversed(SPALTEN[:spalten]):
            pos.append((x, zeile))
            if len(pos) == n:
                break
        zeile -= ZEILE; spalten = 3
        if zeile < 130:
            raise M.Stopp("Galerie: nicht genug Kacheln sichtbar")
    return list(reversed(pos))


FF = str(pathlib.Path.home() / "Documents/Coding/Editing System 1.1/tools/bin/ffmpeg")
GR = 20                                              # Vergleichsraster (GR×GR Graustufen)


def _grau(png, vf):
    r = subprocess.run([FF, "-v", "error", "-i", str(png), "-vf", vf + f",scale={GR}:{GR},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    return r.stdout


def slide_abdruck(jpg):
    """Mittleres Quadrat des Slides (so zeigt die Galerie die Kachel) als GR×GR Graustufen."""
    return _grau(jpg, "crop=iw:iw")


def kachel_abdruck(png, x, y):
    """Kachel um (x, y) im 334er Raster aus dem iPhone-Foto (832×1808) – innerer Bereich ohne Kreis/Ränder."""
    sx, sy = 832 / 334.0, 1808 / 735.0
    w = int(96 * sx)
    return _grau(png, f"crop={w}:{w}:{int(x * sx - w / 2)}:{int(y * sy - w / 2)}")


def abstand(a, b):
    if not a or not b or len(a) != len(b):
        return 1e9
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


def alle_kacheln(unten_max):
    """Mitten aller vollständig sichtbaren Kacheln (unten nach oben) im zuletzt gelesenen Bild."""
    ys = list(range(120, int(unten_max), 2))
    spalte = M.farben(*[(SPALTEN[0], y) for y in ys])
    belegt = [y for y, c in zip(ys, spalte) if not weiss(c)]
    if not belegt:
        return []
    yc = belegt[-1] - ZEILE / 2 + 1
    pos, erste = [], True
    while yc - ZEILE / 2 > 112:
        for x in SPALTEN:
            if erste and x != SPALTEN[0] and kachel_leer(x, yc):
                continue
            pos.append((x, yc))
        erste = False; yc -= ZEILE
    return pos


def kacheln_finden(abdruecke, unten_max, nur=None):
    """Artur 18.11.2026 (falsches Bild ausgewählt): Slides per Bildvergleich in der Galerie suchen, nicht „die letzten
    N“. Alle Slides der Slideshow werden gemeinsam zugeordnet (jede eine eigene Kachel); gleiche Bilder aus älteren
    AirDrops → die neueste. Unsicher nur, wenn ein FREMDES Bild fast so gut passt. → {index: (x, y)} für `nur`."""
    png = "/tmp/slides-galerie.png"
    # 18.11.2026: EIN Bild für Kachel-Raster und Bildvergleich (vorher zwei Fotos kurz nacheinander – die Galerie
    # federte nach dem Hochschieben noch nach → Raster aus Bild 2, Abdrücke aus Bild 1 → „nicht eindeutig“)
    time.sleep(0.6)
    M.lesen()
    subprocess.run([FF, "-v", "error", "-y", "-i", os.path.join(seh.TMP, "f.png"), "-vf", "scale=832:1808", png],
                   capture_output=True)
    kach = alle_kacheln(unten_max)
    drucke = [(k, kachel_abdruck(png, *k)) for k in kach]
    if not drucke:
        raise M.Stopp("Galerie: keine Kacheln gefunden")
    D = [[abstand(a, kd) for _k, kd in drucke] for a in abdruecke]
    # gemeinsame Zuordnung: immer das global beste Paar (Slide, Kachel) nehmen, beide sperren
    paare = sorted((D[i][j], j, i) for i in range(len(abdruecke)) for j in range(len(drucke)))
    zu, belegt = {}, set()
    for d_, j, i in paare:
        if i in zu or j in belegt:
            continue
        zu[i] = j; belegt.add(j)
    eigene = set(zu.values())
    treffer = {}
    for i in sorted(zu):
        j = zu[i]
        gleich = [jj for jj in range(len(drucke)) if abstand(drucke[jj][1], drucke[j][1]) < 1500 and D[i][jj] < D[i][j] * 1.6 + 200]
        jn = min(gleich)                                   # unten zuerst → kleinster Index = neueste Kopie
        fremd = [D[i][jj] for jj in range(len(drucke)) if jj not in gleich and jj not in eigene]
        zweit = min(fremd) if fremd else 1e9
        M.log(f"Slide {i + 1}: Abstand {D[i][j]:.0f}, nächstes fremdes Bild {zweit:.0f}")
        if nur is not None and i not in nur:
            continue
        # 18.11.: weiße Chat-Slides ähneln sich (1171/1686) → bei sehr gutem Treffer (≤ 1500) reicht Vorsprung 1,25
        noetig = 1.25 if D[i][j] <= 1500 else 1.5
        if D[i][j] > 4000 or zweit < D[i][j] * noetig or (D[i][j] > 3000 and zweit < D[i][j] * 2.5):   # 18.11.: 2529/7949 war eindeutig
            raise M.Stopp(f"Slide {i + 1} in der Galerie nicht eindeutig gefunden (Abstand {D[i][j]:.0f}, fremd {zweit:.0f})")
        treffer[i] = drucke[jn][0]
    return treffer


def weiter_n(tx):
    for t in tx:
        m = re.fullmatch(r"Weiter \((\d+)\)", t[0].strip())
        if m:
            return int(m.group(1)), t
    # 18.11.2026 (Dumpling, 1 Slide): bei einem einzelnen Bild steht nur „Weiter“ ohne Zahl – in der Galerie
    # (erkennbar an „AutoCut“/„Layout verwenden“) zählt das als „Weiter (1)“
    if any(t[0].strip() in ("AutoCut", "Layout verwenden") for t in tx):
        w = [t for t in tx if t[0].strip() == "Weiter" and t[2] > 600 and t[1] > 167]
        if w:
            return 1, w[0]
    return 0, None


ZUSCHNEIDEN = (311, 341)
ZUSCHNEIDEN_1 = (311, 425)                          # 18.11.2026: Editor bei nur 1 Bild (Dumpling) – ein Knopf mehr darüber                            # Zuschneiden-Symbol rechts im Foto-Editor (334er Raster)


def knopf_916(tx):
    """9:16-Knopf in der Formatleiste (OCR liest hier manchmal gespiegelt: „91:6“, „D:E“ …) → (x, y) oder None."""
    leiste = [t for t in tx if 620 < t[2] < 665]
    for t in leiste:
        if re.fullmatch(r"9\s*[:.]\s*16|91\s*:\s*6|9:1б", t[0].strip()):
            return t[1], t[2]
    eins = [t for t in leiste if t[0].strip() in ("1:1", "1:l", "l:1")]
    if eins:
        return eins[0][1] - 60, eins[0][2]
    frei = [t for t in leiste if t[0].strip().lower() == "frei"]
    if frei:
        return frei[0][1] + 120, frei[0][2]
    return None


def zuschneiden_offen(tx):
    return any(t[0].strip() == "Abbrechen" and t[2] > 660 for t in tx) and knopf_916(tx) is not None


def alle_auf_916(n):
    """Artur 17.11.2026 (Regel bei Slideshows): im Editor Zuschneiden öffnen, JEDES Bild auf 9:16 stellen (in der
    Zuschneiden-Ansicht bleiben, unten Bild für Bild weiter), am Ende einmal Speichern – vor der Beschreibung.
    Ohne 9:16 bietet „Link hinzufügen“ bei Fotos kein „Produkt“ an."""
    z, tx, _t = M.lage()
    if z != B.EDITOR:
        raise M.Stopp(f"9:16: nicht im Editor („{z}“) – Zuschneiden nicht getippt")
    zx, zy = ZUSCHNEIDEN if n > 1 else ZUSCHNEIDEN_1     # 18.11.: 1 Bild → Editor mit Extra-Knopf, Zuschneiden tiefer
    M.tipp(zx, zy, tx, "Zuschneiden", abstand=10); M.ruhe(1.5)
    tx = M.lesen()
    if not zuschneiden_offen(tx):
        raise M.Stopp("Zuschneiden-Ansicht nicht offen (kein „Abbrechen“/9:16-Leiste)")
    for _ in range(n):                               # ausgewähltes Bild steht in der Mitte → ganz nach links (Bild 1)
        M.tipp(130, 543, M.lesen(), "linker Nachbar", abstand=10); M.ruhe(0.5)
    for i in range(1, n + 1):
        tx = M.lesen(); f = knopf_916(tx)
        if not f:
            raise M.Stopp(f"9:16-Knopf nicht gefunden (Bild {i})")
        M.tipp(f[0], f[1] - 12, tx, f"9:16 (Bild {i})", abstand=10); M.ruhe(0.7)
        if i < n:
            M.tipp(204, 543, M.lesen(), "nächstes Bild", abstand=10); M.ruhe(0.7)
    M.tipp(301, 684, M.lesen(), "Speichern (unten rechts)", abstand=10); M.ruhe(1.5)
    if M.lage()[0] != B.EDITOR:
        raise M.Stopp("nach „Speichern“ nicht zurück im Editor")
    M.log(f"alle {n} Bilder auf 9:16 ✓")


def link_vorstufe():
    """Foto-Post: Link hinzufügen → Produkt → Blatt „Hinzufügen von“ → Einkaufswagen (danach weiter wie bei Videos)."""
    for _ in range(20):
        z, tx, _t = M.lage()
        if z == B.WAGEN_LISTE:
            return
        if z == B.BEITRAG:
            M.tastatur_zu(); tx = M.lesen()
            l = seh.finde("Link hinzufügen", tx)
            if not l:
                raise M.Stopp("„Link hinzufügen“ nicht gefunden")
            M.tipp(l[0], l[1], tx, "Link hinzufügen"); M.ruhe(1.5); continue
        if seh.finde("Hinzufügen von", tx):
            e = [t for t in tx if t[0].strip().endswith("Einkaufswagen") and t[2] > 520]
            if not e:
                raise M.Stopp("Blatt „Hinzufügen von“ ohne „Einkaufswagen“")
            M.tipp(80, e[0][2], tx, "Hinzufügen von: Einkaufswagen"); M.ruhe(1.8); continue
        w = [t for t in tx if "Weitere Produkte hinzuf" in t[0] and t[2] > 600]
        if z == B.SHOWCASE_LISTE and w:                 # Blatt „Hinzufügen von“ kam nicht von selbst → Knopf unten
            M.tipp(w[0][1], w[0][2], tx, "Weitere Produkte hinzufügen"); M.ruhe(1.5); continue
        if z == B.LINK_BLATT or seh.finde("LIVE gehen", tx):
            pr = [t for t in tx if t[0].strip() == "Produkt" and t[2] > 450]
            if not pr:
                raise M.Stopp("Link hinzufügen bietet kein „Produkt“ an (Bilder nicht auf 9:16?)")
            M.tipp(pr[0][1], pr[0][2], tx, "Produkt"); M.ruhe(2.0); continue
        time.sleep(0.8)
    raise M.Stopp("Link-Vorstufe: Einkaufswagen-Liste nicht erreicht")


def fotos_zum_beitrag(n, galerie=None):
    """„+“ → Galerie → n Fotos (Mehrfachauswahl) → Editor → Beitragsseite."""
    gewaehlt = False
    warte_runden = 0
    for _ in range(60):
        z, tx, tabs = M.lage()
        if z == B.BEITRAG:
            return tx
        if M.dialog_wegmachen(z, tx):
            continue
        if z in (B.FEED, B.PROFIL, B.TIKTOK) and tabs:
            M.tipp(167, 681, tx, "+"); M.warte_bildschirm((B.KAMERA, B.GALERIE), 1.6); continue
        if z == B.KAMERA:
            if galerie:
                M.tipp(galerie[0], galerie[1], tx, "Galerie unten rechts")
            else:
                M.tipp(30, 672, tx, "Galerie unten links", abstand=60)
            M.warte_bildschirm((B.GALERIE,), 1.6); continue
        anz, wt = weiter_n(tx)
        if z == B.UNBEKANNT and seh.finde("Aktuell", tx) and \
           (seh.finde("Mehrere auswählen", tx) or seh.finde("Mehrere auswahlen", tx)):
            z = B.GALERIE                                    # 18.11.: Galerie mit „◂ Safari“-Zeile wurde nicht erkannt
        if seh.finde("Aktuell", tx) and any(t[0].strip() in ("AutoCut", "Layout verwenden") for t in tx):
            z = B.GALERIE                                    # 18.11.: Galerie mit 1 Bild („Weiter“ ohne Zahl) galt als Editor
        if z == B.EDITOR and BIS_EDITOR:
            raise M.Hart("--bis-editor: im Editor angehalten")
        if z == B.EDITOR:
            if not HOOK["ok"]:                               # Cover-Ersatz: Hook von Bild 1 groß im Editor lesen
                oben = [t for t in tx if 95 < t[2] < 600 and not (t[1] > 290 and len(t[0].strip()) <= 3)]   # Hook kann oben oder unten stehen
                zus = " ".join(t[0] for t in sorted(oben, key=lambda t: t[2]))
                if HOOK["text"] and not (any(M._passt(HOOK["text"], t[0]) for t in oben) or M._passt(HOOK["text"], zus)):
                    HOOK["fehl"] = HOOK.get("fehl", 0) + 1
                    if HOOK["fehl"] == 2:                    # Editor zeigt evtl. ein anderes Bild → nach rechts wischen bis Bild 1
                        for _ in range(n):
                            seh.kabel().ziehe(70, 330, 290, 330, 0.25); M.ruhe(0.5)
                        continue
                    if HOOK["fehl"] < 6:
                        time.sleep(0.6); continue
                    if not HOOK.get("neu"):                      # Artur 18.11.: AirDrop evtl. noch nicht in der Galerie →
                        HOOK["neu"] = True; HOOK["fehl"] = 0     # Beitrag verwerfen, kurz warten, neu auswählen
                        M.log("Hook passt nicht – Bilder evtl. noch nicht da: verwerfen, 10 s warten, neu auswählen")
                        M.zur_hauptseite(abbrechen=True); time.sleep(10)
                        gewaehlt = False; FORMAT["ok"] = False
                        continue
                    raise M.Sperre(f"Editor zeigt nicht den Hook „{HOOK['text']}“ ({[t[0] for t in oben][:3]}) – NICHT gepostet")
                HOOK["ok"] = True; M.log(f"Bild 1 im Editor passt: {HOOK['text']}")
            if not FORMAT["ok"]:
                alle_auf_916(n); FORMAT["ok"] = True; continue
            w = seh.finde("Weiter", tx, genau=True, unter=600)
            if not (w and w[0] > 167):
                raise M.Stopp("Editor: „Weiter“ nicht rechts")
            M.tipp(w[0], w[1], tx, "Weiter (Editor)"); M.warte_bildschirm((B.BEITRAG,), 2.0); continue
        if z == B.GALERIE or wt:
            if gewaehlt:
                if anz != n:
                    raise M.Sperre(f"Auswahl zeigt „Weiter ({anz})“ statt {n} – NICHT gepostet")
                if wt[1] <= 167:
                    raise M.Stopp("„Weiter“ nicht rechts (AutoCut-Gefahr)")
                M.tipp(wt[1], wt[2], tx, f"Weiter ({n})"); M.warte_bildschirm((B.EDITOR, B.BEITRAG), 2.5); continue
            # Artur 17.11.2026: Tab „Alle“ lassen (nicht „Fotos“) – im Fotos-Tab gab es keinen Produktlink
            m = seh.finde("Mehrere auswählen", tx) or seh.finde("Mehrere auswahlen", tx)
            if m and not M.mehrfach_an(m[1]):
                M.tipp(19, m[1], tx, "Mehrere auswählen (an)"); M.ruhe(1.0); continue
            if anz:
                raise M.Stopp(f"Galerie: schon {anz} ausgewählt, bevor ich angefangen habe")
            # Artur 18.11.: Slides per Bildvergleich finden (Galerie ist nicht verlässlich nach Datum sortiert).
            # 1. Bild antippen (Auswahlfeld unten geht auf), Galerie hochschieben, Rest neu suchen und antippen
            try:
                t = kacheln_finden(ABDRUECKE, 662, nur={0})
            except M.Stopp as e:                             # 18.11.2026 (Coquette): AirDrop noch nicht in der Galerie
                if warte_runden >= 3:
                    if NEU_GESENDET["ja"]:
                        raise
                    NEU_GESENDET["ja"] = True                # Artur 18.11.: AirDrop hängt → aus neuem Ordner nochmal
                    M.log("Slides kamen nicht an → AirDrop aus neuem Ordner nochmal")
                    M.tipp(22, 60, tx, "Galerie zu (X)", abstand=15)
                    SENDEN["f"](True); warte_runden = 0; time.sleep(8)
                    continue
                warte_runden += 1
                M.log(f"{e} → AirDrop evtl. noch unterwegs: Galerie zu, 10 s warten, neu öffnen ({warte_runden}/3)")
                M.tipp(22, 60, tx, "Galerie zu (X)", abstand=15); time.sleep(10)
                continue
            M.tipp(t[0][0] + KREIS[0], t[0][1] + KREIS[1], tx, "Kreis Bild 1", abstand=10); M.ruhe(0.8)
            if n > 1:
                seh.kabel().ziehe(200, 450, 200, 250, 0.6); M.ruhe(1.2)
                try:
                    t = kacheln_finden(ABDRUECKE, 556, nur=set(range(1, n)))
                except M.Stopp as e:                         # 18.11. „Jetzt erstellen“-Galerie: Raster endet über dem
                    M.log(f"{e} → Unterkante 590 probieren")  # Auswahlstreifen (y≈583) statt darunter
                    t = kacheln_finden(ABDRUECKE, 590, nur=set(range(1, n)))
                tx = M.lesen()
                for i in range(1, n):
                    x, y = t[i]
                    M.tipp(x + KREIS[0], y + KREIS[1], tx, f"Kreis Bild {i + 1}", abstand=10); M.ruhe(0.7)
            gewaehlt = True; M.ruhe(0.6); continue
        time.sleep(0.8)
    raise M.Stopp("Fotos-Auswahl: Beitragsseite nicht erreicht")


def sound_kommerziell_sichern():
    """Artur 18.11.2026 (Nr. 17 Naruto): TikTok legt manchmal einen NICHT kommerziellen Sound auf die Slideshow → im
    Blatt „Link hinzufügen“ ist „Produkt“ grau („Verwende kommerziellen Sound …“). Dann im Editor einen kommerziellen
    Sound wählen (erster Eintrag von „Official Sound Studio“ = TikTok-Bibliothek) und zurück zur Beitragsseite."""
    z, tx, _t = M.lage()
    if z != B.BEITRAG:
        return
    M.tastatur_zu(); tx = M.lesen()
    l = seh.finde("Link hinzufügen", tx)
    if not l:
        return
    M.tipp(l[0], l[1], tx, "Link hinzufügen (Sound-Prüfung)"); M.ruhe(1.5)
    tx = M.lesen()
    titel = [t for t in tx if t[0].strip() == "Link hinzufügen" and t[2] > 400]
    grau = seh.finde("kommerziellen Sound", tx) or seh.finde("kommerziellen", tx)
    if titel:                                        # X direkt tippen: im Blatt steht „LIVE gehen“ → M.tipp sperrt (18.11.)
        seh.kabel().tipp(311, titel[0][2]); M.log("Link-Blatt zu (X)"); M.ruhe(1.8)
    if not grau:
        return
    M.log("Sound nicht kommerziell → im Editor kommerziellen Sound wählen (Artur 18.11.)")
    for _ in range(3):                               # Blatt-Animation kann den ersten Tipp schlucken
        if M.lage()[0] == B.EDITOR:
            break
        seh.kabel().tipp(18, 57); M.log("Zurück in den Editor"); M.ruhe(2.0)
    tx = M.lesen()
    pille = [t for t in tx if 55 < t[2] < 100 and 80 < t[1] < 250]
    if not pille:
        raise M.Stopp("Sound nicht kommerziell, aber Sound-Knopf im Editor nicht gefunden")
    M.tipp(pille[0][1], pille[0][2], tx, "Sound-Auswahl öffnen"); M.ruhe(2.5)
    tx = M.lesen()
    oss = [t for t in tx if "Official Sound Studio" in t[0] and t[2] > 380]
    if oss:
        M.tipp(160, oss[0][2] - 17, tx, f"Kommerzieller Sound ({oss[0][0][:30]})"); M.ruhe(2.5)
    else:                                            # 18.11. (Purelei): nicht in „Für dich“ → Suche „Official Sound Studio“,
        seh.kabel().tipp(311, 395); M.ruhe(2.0)      # im Ergebnis beim zweiten Treffer (viel genutzt) auf ✓
        seh.kabel().text("Official Sound Studio"); M.ruhe(0.5); seh.kabel().taste("return"); M.ruhe(3.0)
        tx = M.lesen()
        treffer = [t for t in tx if "Official Sound Studio" in t[0] and t[2] > 300 and t[1] < 200]
        if not treffer:
            raise M.Stopp("Sound nicht kommerziell, Suche nach „Official Sound Studio“ ohne Treffer")
        t = treffer[1] if len(treffer) > 1 else treffer[0]
        seh.kabel().tipp(295, t[2]); M.log(f"Kommerzieller Sound per Suche (Zeile y={t[2]:.0f})"); M.ruhe(3.0)
    M.tipp(167, 200, M.lesen(), "Sound-Liste zu"); M.ruhe(1.5)
    tx = M.lesen()
    w = seh.finde("Weiter", tx, genau=True, unter=600)
    if not (w and w[0] > 167):
        raise M.Stopp("nach Sound-Wechsel: „Weiter“ im Editor nicht gefunden")
    M.tipp(w[0], w[1], tx, "Weiter (Editor)"); M.warte_bildschirm((B.BEITRAG,), 2.5)


_feld_text_alt = M.feld_text
_feld_tippen_alt = M.beschreibung_feld_tippen
TITEL_PLATZHALTER = re.compile(r"füge einen titel hinzu[^\n]*?erweckt|mit einer detail+ierten beschreibung[^\n]*?erzielen\.?"
                               r"|\d+/90", re.I)


def feld_text_slides(tx):
    """Foto-Post: oben Titel (bleibt leer, Artur 17.11.), darunter Beschreibung – Platzhalter beider Felder raus.
    18.11.2026: Vorschau-Leiste der Slides (y ≤ 122) nicht mitlesen – Text/Preise auf den Slides (Blaue-Haie-Meme) galten sonst als Beschreibung."""
    tl = [t[2] for t in tx if "titel hinzu" in t[0].lower() and t[2] < 300]   # 18.11.: ab dem Titel-Platzhalter lesen –
    y0 = tl[0] - 6 if tl else 123                                           # darüber Vorschaubilder (Text/Preise auf Slides)
    feld = " ".join(t[0] for t in tx if t[1] < 230 and y0 < t[2] < 345 and t[0].strip() not in ("#", "@", "+")
                    and not t[0].strip().lower().startswith(("vorschau", "cover", "umformulieren"))).lower()
    feld = re.sub(r"beschreibung hinzufügen\W*", " ", feld)
    return " ".join(TITEL_PLATZHALTER.sub(" ", feld).split())


def feld_tippen_slides(tx):
    b = seh.finde("Beschreibung", tx, ueber=330)
    if b and "titel" not in b[2:] and b[1] > 150:
        M.tipp(b[0], b[1], tx, "Beschreibung"); M.ruhe(0.7); return
    alt = [t for t in tx if t[1] < 230 and 60 < t[2] < 330 and "titel" not in t[0].lower() and not re.fullmatch(r"\d+/90", t[0].strip())
           and not t[0].strip().lower().startswith(("vorschau", "cover"))]
    alt = [t for t in alt if t[2] > (min([x[2] for x in tx if "titel" in x[0].lower()] or [0]) + 15)]
    if not alt:
        raise M.Stopp("Beschreibungsfeld (unter dem Titel) nicht gefunden")
    M.tipp(alt[0][1], alt[0][2], tx, "Beschreibung (vorhandener Text)"); M.ruhe(0.7)


WAGEN = M.AUS / "wagen.json"                      # Artur 17.11.: Produkt schon im Einkaufswagen → nicht nochmal hinzufügen


def wagen_lesen():
    try:
        return json.loads(WAGEN.read_text())
    except Exception:
        return {}


def wagen_merken(account, pid):
    w = wagen_lesen(); w[f"{account}|{pid}"] = time.strftime("%Y-%m-%d %H:%M"); WAGEN.write_text(json.dumps(w, indent=1))


def marke_summe(slides):
    import hashlib
    return hashlib.sha1(b"".join(p.read_bytes() for p in slides)).hexdigest()


def main():
    a = sys.argv[1:]
    if not a or "--account" not in a:
        sys.exit(__doc__)
    ordner = pathlib.Path(a[0]).resolve()
    account = a[a.index("--account") + 1]
    entwurf = "--entwurf" in a
    plan = json.loads((ordner / "plan.json").read_text())
    slides = sorted((ordner / "fertig").glob("S_Bild*.jpg"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1]))
    if not slides:
        sys.exit("STOPP: keine Slides in fertig/")
    pid = str(plan.get("produkt_id") or "")
    if not pid:
        sys.exit("STOPP: plan.json ohne produkt_id")
    name = re.sub(r"^\d+\s*", "", ordner.name)              # ohne Nummer (Produktname-Knopf darf keine Zahl haben)
    marke = M.EIN / f"{name}.slides"                     # Doppel-Schutz: Prüfsumme über alle Slides
    marke.write_bytes(b"".join(p.read_bytes() for p in slides))
    hook = re.sub(r"[^\w\s€?!.,:-]", "", plan["bilder"][0].get("hook") or plan["bilder"][0].get("text", "")).strip()
    d = {"version": 1, "datei": marke.name, "account": account, "social1_link": "",
         "tts_link": f"https://shop.tiktok.com/view/product/{pid}", "produkt": plan.get("produkt_voll") or plan["produkt"],
         "titel": plan.get("titel", ""), "text": plan.get("titel", ""),
         "hashtags": plan.get("hashtags", []), "stapel": "slideshows-" + time.strftime("%Y-%m-%d"),
         "status": "freigegeben", "notiz": f"Slideshow {len(slides)} Bilder", "verlauf": [],
         "kachel": hook, "button": plan.get("button_fest") or random.choice(BUTTONS), "brand": plan.get("brand", ""), "handle": "",
         "quelle": str(ordner), "social1_liste": SLIDES_LISTE, "art": "slideshow", "bilder": len(slides)}
    p = M.EIN / f"{name}.json"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    gesendet = ordner / "iphone" / ".gesendet"                # Artur 18.11.: nicht bei jedem Versuch nochmal AirDrop
    schon = gesendet.exists() and time.time() - gesendet.stat().st_mtime < 2 * 86400 \
        and gesendet.read_text().strip() == marke_summe(slides)
    if schon:
        M.log("Slides sind schon auf dem iPhone (früherer Versuch) → kein neuer AirDrop")
    def senden(neuer_ordner=False):
        tmp = ordner / "iphone"
        subprocess.run([sys.executable, str(HIER / "jpg_datum.py"), str(tmp), *map(str, slides)], check=True,
                       capture_output=True)
        import airdrop, shutil
        # Artur 18.11.2026: „AirDrop hängt … Lösung: einen neuen Ordner der Bilder erstellen oder die Bilder woanders
        # hin verschieben“ – „mach das nur wenn das passiert“ → erst normal senden, nur bei Hänger aus neuem Ordner
        def aus_neuem_ordner():
            neu = pathlib.Path(f"/tmp/airdrop-slides-{int(time.time() * 1000)}")
            neu.mkdir(parents=True, exist_ok=True)
            return [pathlib.Path(shutil.copy2(f, neu / f.name)) for f in sorted(tmp.glob("slide-*.jpg"))]
        if neuer_ordner:
            airdrop.senden(aus_neuem_ordner())
        else:
            try:
                airdrop.senden(sorted(tmp.glob("slide-*.jpg")))
            except Exception as e:
                M.log(f"AirDrop hängt ({str(e)[:60]}) → aus neuem Ordner nochmal (Artur 18.11.)")
                airdrop.senden(aus_neuem_ordner())
        M.log(f"{len(slides)} Slides per AirDrop")
        gesendet.write_text(marke_summe(slides))
        M._zurueck_in_tiktok() if hasattr(M, "_zurueck_in_tiktok") else None
    SENDEN["f"] = senden
    if "--ohne-airdrop" not in a and not schon:
        senden()
    HOOK["text"] = hook
    ABDRUECKE[:] = [slide_abdruck(p) for p in slides]
    M.cover_pruefen = lambda kachel: None if HOOK["ok"] else (_ for _ in ()).throw(M.Sperre("Hook nicht im Editor geprüft"))
    _ablauf_alt, _in_wagen_alt = M._ablauf, M.in_wagen
    def _ablauf(dd, F, ppid):
        if not F["produkt"] and f"{account}|{ppid}" in wagen_lesen() and "--neu-in-wagen" not in a:
            if F["konto"] or True:
                M.log("Produkt liegt schon im Einkaufswagen → direkt verlinken (Artur 17.11.)")
                if not F["konto"]:
                    if M._konto != dd["account"]:
                        M.konto(dd["account"]); M._konto = dd["account"]
                    F["konto"] = True
                F["produkt"] = "wagen"
        return _ablauf_alt(dd, F, ppid)
    def _in_wagen(tx):
        r = _in_wagen_alt(tx); wagen_merken(account, pid); return r
    M._ablauf, M.in_wagen = _ablauf, _in_wagen
    if "--weiter" in a:                               # Test: Beitrag läuft schon (Editor/Beitragsseite offen)
        M._konto = account
    if "--ab-beitrag" in a:                           # Test: Beitragsseite ist schon offen (Bilder geprüft)
        M._konto = account; HOOK["ok"] = True
    _verlinken_alt = M.verlinken
    def _verlinken(weg, produkt, kurz=""):
        if weg in ("wagen", "showcase"):
            sound_kommerziell_sichern()
        if weg == "wagen":
            link_vorstufe()
        return _verlinken_alt(weg, produkt, kurz)
    M.verlinken = _verlinken
    M.MAX_WIEDERAUFNAHMEN = 0                         # Artur 17.11.: bei Hänger stehen bleiben, nicht selbst neu anfangen
    M.feld_text = feld_text_slides
    M.beschreibung_feld_tippen = feld_tippen_slides
    M.zum_beitrag = lambda kachel, galerie=None, warten_s=120: fotos_zum_beitrag(len(slides), galerie)
    M.video_waehlen = M.zum_beitrag
    try:
        try:
            M.ein_video(p, d, entwurf=entwurf)
        except M.Stopp as e:
            # 18.11.2026 (Shark): AirDrop übersprungen, andere Slideshows kamen danach → Slides oben angeschnitten, nicht
            # gefunden. Dann einmal frisch senden (werden die neuesten Kacheln) und den Post neu anfangen.
            if not (schon and "nicht eindeutig" in str(e)) or "--ohne-airdrop" in a:
                raise
            M.log(f"{e} → Slides frisch per AirDrop, Post neu")
            M.zur_hauptseite(abbrechen=True)
            senden()
            HOOK["ok"] = False; HOOK.pop("fehl", None); HOOK.pop("neu", None); FORMAT["ok"] = False
            M.ein_video(p, d, entwurf=entwurf)
    except M.Stopp as e:
        M.schreibe(p, d, "fehler", str(e))
        sys.exit(f"STOPP: {e}")


if __name__ == "__main__":
    main()
