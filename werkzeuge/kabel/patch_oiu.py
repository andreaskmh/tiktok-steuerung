#!/usr/bin/env python3
"""Erweitert den installierten open-iphone-use-Server für die TikTok-Steuerung (mehrfach ausführbar).

  python3 werkzeuge/kabel/patch_oiu.py        # danach: open-iphone-use stop && open-iphone-use serve

Änderungen (docs/AENDERUNGEN.md, 12.11.2026):
  1. Live-Bild: pymobiledevice3 >= 11.52 übergibt (bild, breite, höhe, drehung) → sonst kein Bild.
  2. Neue Aktion „drag“: eigene Zieh-Bewegung (x1, y1, x2, y2 als Anteile 0..1, dauer in s).
  3. Neue Aktion „hid“: rohe Tastatur-Codes [[modifier, usage], …] (für deutsches Tastaturlayout, Umlaute, #).
  4. Neuer Abruf GET /api/devices/<id>/png: aktuelles Bild verlustfrei als PNG (für Stock-Bilder).
  5. Ruhender Bildschirm: Bild alle 0,15 s statt 0,5 s (Tipps schneller).
  7. Flüssigeres Live-Bild für die App iPhone-Spiegel: MJPEG 60 statt 30 Bilder/s, WLAN 6 statt 2 Mbit/s (20.11.2026).
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

# 6. Schnelles Tippen (Artur 16.11.2026: „Menschen tippen deutlich schneller“): press() hält jede Taste ~0,1 s
#    (40 ms gedrückt + 40 ms + 20 ms). hid mit Argument „halt“ nutzt press_kurz: Taste nur „halt“ Sekunden gedrückt.
ersetze("coredevice.py",
        "        async def press(self, keys):\n",
        "        async def press_kurz(self, keys, halt):  # TS-Steuerung: schnelles Tippen\n"
        "            await self._ensure_keyboard()\n"
        "            service, keyboard = self._uhs, self._kb_service_id\n"
        "            modifiers = tuple(u for u in keys if u >= 0xE0)\n"
        "            if modifiers and len(modifiers) < len(keys):\n"
        "                await service.send_keyboard(keyboard, modifiers); await asyncio.sleep(.015)\n"
        "            await service.send_keyboard(keyboard, keys); await asyncio.sleep(halt)\n"
        "            await service.send_keyboard(keyboard, ()); await asyncio.sleep(.01)\n"
        "\n"
        "        async def press(self, keys):\n",
        "async def press_kurz(self, keys, halt):")
ersetze("coredevice.py",
        "                await connection.press(held(int(modifier), int(usage)))\n"
        "                if args.get('pause'): await asyncio.sleep(float(args['pause']))\n",
        "                if args.get('halt'): await connection.press_kurz(held(int(modifier), int(usage)), min(.1, float(args['halt'])))  # TS\n"
        "                else: await connection.press(held(int(modifier), int(usage)))\n"
        "                if args.get('pause'): await asyncio.sleep(float(args['pause']))\n",
        "connection.press_kurz(held(")

# 7. Flüssiges Live-Bild (App iPhone-Spiegel, Andreas 20.11.2026: „laggt, läuft auf 30 FPS“).
ersetze("http.py", "def stream(self, device, fps=30):", "def stream(self, device, fps=60):  # TS", "fps=60):  # TS")
ersetze("coredevice.py", "WIFI_MAX_BITRATE = 2_000_000", "WIFI_MAX_BITRATE = 6_000_000  # TS: wie Xcode, flüssiger", "6_000_000  # TS")

print("fertig – Server neu starten: open-iphone-use stop && open-iphone-use serve")
