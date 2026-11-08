#!/usr/bin/env python3
"""Attrappe des Mini-Geräts zum Testen ohne Arduino.

Öffnet einen virtuellen seriellen Port (pty), antwortet wie der Sketch hid_maus
(gleiche Befehle, gleiche Grenzen, gleiche Antworten) – bewegt aber nichts.

  python3 geraet/attrappe.py            # gibt den Port aus, z. B. /dev/ttys012
  GERAET_PORT=/dev/ttys012 python3 geraet/geraet.py ping
"""
import os, pty, sys, time, tty

def b(v, lo, hi): return max(lo, min(hi, v))

def ausfuehren(z, log):
    z = z.strip()
    if not z: return None
    cmd, _, rest = z.partition(" ")
    cmd = cmd.upper()
    try: v = [int(x) for x in rest.split()]
    except ValueError: v = []
    def need(n, use):
        return None if len(v) >= n else f"ERR {use}"
    if cmd == "PING": return "OK PONG"
    if cmd == "STOP": return "OK STOP"
    if cmd == "SCROLL":
        e = need(3, "SCROLL dx dy n [ms]");
        if e: return e
        n, ms = b(v[2], 1, 50), b(v[3] if len(v) > 3 else 20, 1, 500)
        log(f"rad dx={v[0]:+d} dy={v[1]:+d} x{n} ({ms} ms)"); time.sleep(n * ms / 1000); return "OK SCROLL"
    if cmd == "SHIFTSCROLL":
        e = need(1, "SHIFTSCROLL n [ms]");
        if e: return e
        n, ms = b(v[0], -50, 50), b(v[1] if len(v) > 1 else 20, 1, 500)
        log(f"shift+rad {n:+d} ({ms} ms)"); time.sleep(abs(n) * ms / 1000); return "OK SHIFTSCROLL"
    if cmd == "MOVE":
        e = need(2, "MOVE dx dy");
        if e: return e
        log(f"move {b(v[0],-3000,3000):+d} {b(v[1],-3000,3000):+d}"); return "OK MOVE"
    if cmd == "DRAG":
        e = need(3, "DRAG dx dy steps [ms]");
        if e: return e
        st, ms = b(v[2], 1, 200), b(v[3] if len(v) > 3 else 8, 1, 500)
        log(f"drag {v[0]:+d} {v[1]:+d} in {st} Schritten"); time.sleep(st * ms / 1000 + 0.06); return "OK DRAG"
    if cmd in ("CLICK", "PRESS", "RELEASE"):
        t = rest.strip() or "L"
        if t not in ("L", "R", "M"): return "ERR L|R|M"
        log(f"{cmd.lower()} {t}"); return f"OK {cmd}"
    if cmd == "KEY":
        k = rest.strip()
        if k.upper() not in ("LEFT","RIGHT","UP","DOWN","RETURN","ESC","TAB","SPACE") and len(k) != 1: return "ERR KEY name"
        log(f"key {k}"); return "OK KEY"
    if cmd == "TYPE": log(f"type {rest!r}"); return "OK TYPE"
    return "ERR unbekannt: " + cmd

def main():
    master, slave = pty.openpty()
    tty.setraw(master)
    print(os.ttyname(slave), flush=True)
    log = lambda s: print("  [attrappe]", s, file=sys.stderr, flush=True)
    puffer = b""
    while True:
        try: d = os.read(master, 256)
        except OSError: time.sleep(0.05); continue
        puffer += d
        while b"\n" in puffer or b"\r" in puffer:
            i = min(x for x in (puffer.find(b"\n"), puffer.find(b"\r")) if x >= 0)
            zeile, puffer = puffer[:i].decode(errors="replace"), puffer[i+1:]
            a = ausfuehren(zeile, log)
            if a:
                log(f"{zeile!r} -> {a}")
                os.write(master, (a + "\r\n").encode())

if __name__ == "__main__":
    main()
