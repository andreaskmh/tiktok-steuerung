#!/usr/bin/env python3
"""Erweitert den installierten open-iphone-use-Server für die TikTok-Steuerung (mehrfach ausführbar).

  python3 werkzeuge/kabel/patch_oiu.py        # danach: open-iphone-use stop && open-iphone-use serve

Änderungen (docs/AENDERUNGEN.md, 12.11.2026):
  1. Live-Bild: pymobiledevice3 >= 11.52 übergibt (bild, breite, höhe, drehung) → sonst kein Bild.
  2. Neue Aktion „drag“: eigene Zieh-Bewegung (x1, y1, x2, y2 als Anteile 0..1, dauer in s).
  3. Neue Aktion „hid“: rohe Tastatur-Codes [[modifier, usage], …] (für deutsches Tastaturlayout, Umlaute, #).
  4. Neuer Abruf GET /api/devices/<id>/png: aktuelles Bild verlustfrei als PNG (für Stock-Bilder).
  5. Ruhender Bildschirm: Bild alle 0,15 s statt 0,5 s (Tipps schneller).
"""
import pathlib, sys, glob

ROOT = pathlib.Path.home() / ".local/share/open-iphone-use/runtime/venv/lib"
treffer = glob.glob(str(ROOT / "python3*/site-packages/oiu"))
if not treffer:
    sys.exit("open-iphone-use nicht installiert (~/.local/share/open-iphone-use)")
OIU = pathlib.Path(treffer[0])


def ersetze(datei, alt, neu, marke):
    p = OIU / datei
    s = p.read_text()
    if marke in s:
        print(f"  schon drin: {datei} – {marke}")
        return
    if alt not in s:
        sys.exit(f"STOPP: Stelle in {datei} nicht gefunden ({marke}) – Server-Version geändert?")
    p.write_text(s.replace(alt, neu, 1))
    print(f"  gepatcht:   {datei} – {marke}")


# 1. Live-Bild
ersetze("coredevice.py",
        "        def _broadcast_frame(self, bgra):\n            super()._broadcast_frame(bgra)\n",
        "        def _broadcast_frame(self, *args):\n            # pymobiledevice3 >=11.52 passes (bgra, width, height, rotation)\n"
        "            super()._broadcast_frame(*args)\n",
        "_broadcast_frame(self, *args)")

# 2. + 3. Aktionen drag / hid
ersetze("core.py",
        '"swipe", "advance_feed"}',
        '"swipe", "advance_feed", "drag", "hid"}  # TS: drag, hid',
        "# TS: drag, hid")
ersetze("coredevice.py",
        "        if operation in ('swipe', 'advance_feed'):\n",
        "        if operation == 'drag':  # TS-Steuerung\n"
        "            dauer = float(args.get('dauer', .3))\n"
        "            if not .05 <= dauer <= 3: raise ValueError('dauer 0.05…3 s')\n"
        "            await connection.drag(units(args['x1']), units(args['y1']), units(args['x2']), units(args['y2']), dauer)\n"
        "            return 'Dragged'\n"
        "        if operation == 'hid':  # TS-Steuerung\n"
        "            keys = args['keys']\n"
        "            if not isinstance(keys, list) or len(keys) > 500: raise ValueError('keys: list of [modifier, usage]')\n"
        "            for modifier, usage in keys:\n"
        "                if not (0 <= int(modifier) < 256 and 0 <= int(usage) < 256): raise ValueError('bad key')\n"
        "            for modifier, usage in keys:\n"
        "                await connection.press(held(int(modifier), int(usage)))\n"
        "                if args.get('pause'): await asyncio.sleep(float(args['pause']))\n"
        "            return 'Keys sent'\n"
        "        if operation in ('swipe', 'advance_feed'):\n",
        "if operation == 'drag':  # TS-Steuerung")

# 4. PNG-Abruf
ersetze("http.py",
        '                if not post and parts[3] == "frame":\n',
        '                if not post and parts[3] == "png":  # TS-Steuerung: verlustfreies Bild\n'
        '                    import io\n'
        '                    from PIL import Image\n'
        '                    con = device.backend.connection\n'
        '                    w, h = con._fb_width, con._fb_height\n'
        '                    img = Image.frombuffer("RGB", (w, h), con._latest_frame, "raw", "BGRX", 0, 1)\n'
        '                    out = io.BytesIO(); img.save(out, format="PNG")\n'
        '                    return self.reply(out.getvalue(), mime="image/png")\n'
        '                if not post and parts[3] == "frame":\n',
        'parts[3] == "png":  # TS-Steuerung')
# 5. Tempo: ruhender Bildschirm liefert alle 0,15 s ein Bild (statt 0,5 s) → jeder Tipp ist ~0,4 s schneller
ersetze("coredevice.py", "STILL_FRAME_SECONDS = .5", "STILL_FRAME_SECONDS = .15  # TS: schneller", "STILL_FRAME_SECONDS = .15")

print("fertig – Server neu starten: open-iphone-use stop && open-iphone-use serve")
