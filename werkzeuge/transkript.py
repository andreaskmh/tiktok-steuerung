#!/usr/bin/env python3
"""Lokales Transkript für TikTok-Videos (ohne Social1-Credits): yt-dlp lädt den Ton, Whisper (mlx, M1) macht Text + Sprache.

  ~/.tiktok-research/venv/bin/python werkzeuge/transkript.py <zielordner> <nr> <tiktok-link> [<nr> <link> ...]

Schreibt <zielordner>/<nr>.json = {"sprache": "en", "text": "..."} bzw. {"fehler": "..."} (z. B. Video nicht verfügbar).
Einrichtung (einmalig, 19.11.2026): venv in ~/.tiktok-research/venv mit yt-dlp, mlx-whisper, imageio-ffmpeg.
"""
import json, os, pathlib, subprocess, sys, time, warnings

warnings.filterwarnings("ignore")
HEIM = pathlib.Path.home() / ".tiktok-research"
os.environ["PATH"] = f"{HEIM / 'bin'}:{os.environ['PATH']}"          # ffmpeg (imageio-ffmpeg) für Whisper
MODELL = "mlx-community/whisper-large-v3-turbo"


def main(a):
    if len(a) < 3:
        sys.exit(__doc__)
    ziel = pathlib.Path(a[0])
    ziel.mkdir(parents=True, exist_ok=True)
    tmp = HEIM / "tmp"
    tmp.mkdir(exist_ok=True)
    import mlx_whisper
    for nr, url in zip(a[1::2], a[2::2]):
        aus = ziel / f"{nr}.json"
        if aus.exists():
            continue
        ton = tmp / f"{nr}.mp4"                                   # ganzes Video (nur Ton gibt bei TikTok oft 403), bis 3 Versuche
        for _ in range(3):
            r = subprocess.run([str(HEIM / "venv" / "bin" / "yt-dlp"), "-q", "--no-warnings", "-f", "worst[ext=mp4]/b", "--merge-output-format", "mp4",
                                "-o", str(ton), url], capture_output=True, text=True, timeout=180)
            if ton.exists() or "Unsupported URL" in r.stderr or "not available" in r.stderr:
                break
            if "Log in for access" in r.stderr:                  # altersbeschränkt: braucht TikTok-Login → vorerst übersprungen
                break
            time.sleep(3)
        if not ton.exists():
            aus.write_text(json.dumps({"fehler": (r.stderr.strip().splitlines() or ["Download fehlgeschlagen"])[-1][:200]}))
            print(f"Nr {nr}: nicht ladbar", flush=True)
            continue
        try:
            erg = mlx_whisper.transcribe(str(ton), path_or_hf_repo=MODELL)
            aus.write_text(json.dumps({"sprache": erg.get("language", ""), "text": erg.get("text", "").strip()}, ensure_ascii=False))
            print(f"Nr {nr}: {erg.get('language')} {len(erg.get('text', ''))} Zeichen", flush=True)
        except Exception as e:                                   # z. B. Video ohne Tonspur
            aus.write_text(json.dumps({"fehler": str(e)[:200]}))
            print(f"Nr {nr}: Fehler {str(e)[:80]}", flush=True)
        finally:
            ton.unlink(missing_ok=True)


if __name__ == "__main__":
    main(sys.argv[1:])
