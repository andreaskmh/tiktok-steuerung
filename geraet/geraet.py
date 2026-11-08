#!/usr/bin/env python3
"""Mac-Gegenstück zum Mini-Gerät (Pro Micro, Sketch hid_maus).

Aufruf:
  python3 geraet/geraet.py ping
  python3 geraet/geraet.py "SHIFTSCROLL -3"
  python3 geraet/geraet.py "SCROLL 0 -5 5" "CLICK"        # mehrere Befehle nacheinander
  python3 geraet/geraet.py --port /dev/cu.usbmodem1101 ping

Ohne --port gilt $GERAET_PORT, sonst der erste /dev/cu.usbmodem*. Nur Python-Standardbibliothek (kein pyserial).
Wichtig: Das Gerät bewegt den Zeiger nur relativ. Zuerst mit werkzeuge/bin/zeiger an die
richtige Stelle setzen, dann wischen/scrollen.
"""
import glob, os, select, sys, termios, time


def finde_port():
    if os.environ.get("GERAET_PORT"):
        return os.environ["GERAET_PORT"]
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not ports:
        sys.exit("Kein Mini-Gerät gefunden (/dev/cu.usbmodem*). Steckt es? Ist der Sketch drauf?")
    return ports[0]


class Geraet:
    def __init__(self, port=None, baud=115200):
        self.port = port or finde_port()
        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        a = termios.tcgetattr(self.fd)
        speed = getattr(termios, f"B{baud}", termios.B115200)
        a[0] = 0                                  # iflag
        a[1] = 0                                  # oflag
        a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        a[3] = 0                                  # lflag (raw)
        a[4] = a[5] = speed
        termios.tcsetattr(self.fd, termios.TCSANOW, a)
        termios.tcflush(self.fd, termios.TCIOFLUSH)
        time.sleep(0.3)

    def befehl(self, text, timeout=10.0):
        os.write(self.fd, (text.strip() + "\n").encode("ascii", "replace"))
        puffer, ende = b"", time.time() + timeout
        while time.time() < ende:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if r:
                puffer += os.read(self.fd, 256)
                if b"\n" in puffer:
                    return puffer.split(b"\n")[0].decode(errors="replace").strip()
        return "ERR keine Antwort"

    def close(self):
        os.close(self.fd)


def main(argv):
    port = None
    if len(argv) >= 2 and argv[0] == "--port":
        port, argv = argv[1], argv[2:]
    if not argv:
        print(__doc__)
        return 2
    g = Geraet(port)
    fehler = 0
    try:
        for b in argv:
            antwort = g.befehl(b)
            print(f"{b} -> {antwort}")
            fehler |= not antwort.startswith("OK")
    finally:
        g.close()
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
