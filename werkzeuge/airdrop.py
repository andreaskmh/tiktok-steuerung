#!/usr/bin/env python3
"""Videos per AirDrop vom Mac aufs iPhone (Kabel-Steuerung) – ersetzt das Ziehen in die iPhone-Synchronisierung.

  python3 werkzeuge/airdrop.py <video> [<video> …]

1. bin/airdrop öffnet das AirDrop-Fenster am Mac mit den Dateien,
2. Empfänger wird per Bedienungshilfen gewählt (TS_AIRDROP_ZIEL, Standard „iPhone von Artur (2)“ = iPhone 11),
3. gleiche Apple-ID → iPhone nimmt ohne Abfrage an und öffnet das Video in Fotos (getestet 12.11.2026);
   kommt doch „Annehmen“ (oder der Hinweis „Neu in Fotos“ → „Fortfahren“), tippt das Skript es per Kabel an.
Voraussetzung am iPhone: Einstellungen → Allgemein → AirDrop → „Nur für Kontakte“ (seit 12.11.2026, vorher „Empfangen aus“).
"""
import os, pathlib, re, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import seh

ZIEL = os.environ.get("TS_AIRDROP_ZIEL", "iPhone von Artur (2)")   # Gerätename im AirDrop-Fenster


class Stopp(Exception):
    pass


def empfaenger_klicken(ziel, sek=20):
    """Knopf im AirDrop-Fenster, dessen Hilfetext genau dem Gerätenamen entspricht, anklicken."""
    skript = f'''
tell application "System Events" to tell process "airdrop"
  set g to UI element 1 of UI element 1 of scroll area 1 of group 1 of window "AirDrop"
  set namen to ""
  repeat with b in (buttons of g)
    set h to (help of b as text)
    if h is "{ziel}" then
      click b
      return "OK"
    end if
    set namen to namen & h & "; "
  end repeat
  return "FEHLT " & namen
end tell'''
    ende = time.time() + sek
    letzte = ""
    while time.time() < ende:
        r = subprocess.run(["osascript", "-e", skript], capture_output=True, text=True)
        letzte = (r.stdout + r.stderr).strip()
        if letzte.startswith("OK"):
            return
        time.sleep(1)
    raise Stopp(f"AirDrop-Empfänger „{ziel}“ nicht gefunden ({letzte})")


DATUM = re.compile(r"^(heute|gestern|\d{1,2}\. \w+|\w+tag)$", re.I)


def _fotos_vorn(tx):
    """Fotos zeigt das angekommene Video (Datum oben / „Zuletzt gesichert“ / Fotos-Bildschirm laut bildschirm.py)."""
    import bildschirm as B
    return any(DATUM.match(t.strip()) and y < 80 for t, _, y in tx) or bool(seh.finde("Zuletzt gesichert", tx)) or \
        B.erkenne(tx) in (B.FOTOS_VOLLBILD, B.FOTOS_ALBUM, B.FOTOS_MEDIATHEK)


def angekommen(p, sek):
    """Warten, bis das iPhone das Video in Fotos zeigt (oder bin/airdrop „OK“ meldet). Abfragen unterwegs annehmen.
    → „fotos“ (am iPhone gesehen) oder „mac“ (nur bin/airdrop meldet OK, Fotos ging nicht auf).
    16.11.2026 (Tempo, AirDrop kam 2× nicht an): „kaum Text nach 9 s“ zählt nur noch, wenn sich der Bildschirm seit dem
    Senden geändert hat (vorher konnte ein ruhiger Bildschirm als „angekommen“ gelten); meldet bin/airdrop OK, wird noch
    bis 4 s auf Fotos geschaut."""
    K = seh.kabel()
    if not K:
        raise Stopp("Kabel-Steuerung nicht aktiv – Ankunft am iPhone bitte selbst prüfen")
    start = time.time(); ende = start + sek
    sig0 = None
    mac_ok = None
    while time.time() < ende:
        if mac_ok is None and p.poll() is not None:
            out = p.stdout.read()
            if "OK" not in out:
                raise Stopp(f"AirDrop: {out.strip()}")
            mac_ok = time.time()                                  # Mac fertig – kurz noch auf Fotos am iPhone schauen
        if mac_ok and time.time() - mac_ok > 4:
            return "mac"
        tx = seh.lesen()
        sig = " ".join(t for t, _, _ in tx)
        sig0 = sig if sig0 is None else sig0
        for knopf, gegen in (("Annehmen", "Ablehnen"), ("Fortfahren", None)):
            a = seh.finde(knopf, tx, genau=True)
            if a and (gegen is None or seh.finde(gegen, tx, genau=True)):
                K.tipp(a[0], a[1]); time.sleep(1.5); break
        else:
            if _fotos_vorn(tx) or \
               (time.time() - start > 9 and len(tx) <= 6 and sig != sig0):   # 13.11.2026: Video spielt schon im Vollbild
                time.sleep(1.0)                                  # (kaum Text) – 16.11.: nur wenn der Bildschirm wechselte
                return "fotos"
        time.sleep(0.5)
    if mac_ok:
        return "mac"
    raise Stopp("Video nicht am iPhone angekommen (AirDrop am iPhone an? „Nur für Kontakte“)")


def senden(videos, nach_klick=None, max_s=None):
    """nach_klick(): wird aufgerufen, sobald der Empfänger angeklickt ist (Übertragung läuft) – 15.11.2026: damit ein Video
    auch dann als „gesendet“ gilt, wenn die Ankunft am Bildschirm nicht erkannt wird (sonst doppeltes AirDrop).
    → „fotos“/„mac“ (siehe angekommen). 16.11.2026 (Tempo): Wartezeit 40 s + 20 s je Video (war 60 + 30; ein Video kommt
    sonst nach 5–15 s an) – kommt es nicht, schickt post_mensch.airdrop_einmal sofort nochmal, statt in TikTok zu warten."""
    videos = [str(pathlib.Path(v).resolve()) for v in videos]
    for v in videos:
        if not pathlib.Path(v).exists():
            raise Stopp(f"Datei fehlt: {v}")
    subprocess.run(["zsh", str(HIER / "build.sh")], capture_output=True)
    p = subprocess.Popen([str(HIER / "bin" / "airdrop"), *videos], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        time.sleep(1.5)
        empfaenger_klicken(ZIEL)
        if nach_klick:
            nach_klick()
        erg = angekommen(p, max_s or (40 + 20 * len(videos)))
    finally:
        if p.poll() is None:
            p.terminate()
    time.sleep(0.5 * len(videos))                                # 16.11.: war 2 + n s – Fotos zeigt das Video schon
    return erg


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        senden(sys.argv[1:])
        print("OK – in Fotos am iPhone")
    except Stopp as e:
        sys.exit(f"STOPP: {e}")
