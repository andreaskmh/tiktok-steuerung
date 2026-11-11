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


def angekommen(p, sek):
    """Warten, bis das iPhone das Video in Fotos zeigt (oder bin/airdrop „OK“ meldet). Abfragen unterwegs annehmen."""
    K = seh.kabel()
    if not K:
        raise Stopp("Kabel-Steuerung nicht aktiv – Ankunft am iPhone bitte selbst prüfen")
    ende = time.time() + sek
    while time.time() < ende:
        if p.poll() is not None:
            out = p.stdout.read()
            if "OK" in out:
                return
            raise Stopp(f"AirDrop: {out.strip()}")
        tx = seh.lesen()
        for knopf, gegen in (("Annehmen", "Ablehnen"), ("Fortfahren", None)):
            a = seh.finde(knopf, tx, genau=True)
            if a and (gegen is None or seh.finde(gegen, tx, genau=True)):
                K.tipp(a[0], a[1]); time.sleep(1.5); break
        else:
            if any(DATUM.match(t.strip()) and y < 80 for t, _, y in tx):   # Fotos-Ansicht mit Datum oben
                time.sleep(2)
                return
        time.sleep(0.7)
    raise Stopp("Video nicht am iPhone angekommen (AirDrop am iPhone an? „Nur für Kontakte“)")


def senden(videos):
    videos = [str(pathlib.Path(v).resolve()) for v in videos]
    for v in videos:
        if not pathlib.Path(v).exists():
            raise Stopp(f"Datei fehlt: {v}")
    subprocess.run(["zsh", str(HIER / "build.sh")], capture_output=True)
    p = subprocess.Popen([str(HIER / "bin" / "airdrop"), *videos], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        time.sleep(1.5)
        empfaenger_klicken(ZIEL)
        angekommen(p, 60 + 30 * len(videos))
    finally:
        if p.poll() is None:
            p.terminate()
    time.sleep(2 + len(videos))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        senden(sys.argv[1:])
        print("OK – in Fotos am iPhone")
    except Stopp as e:
        sys.exit(f"STOPP: {e}")
