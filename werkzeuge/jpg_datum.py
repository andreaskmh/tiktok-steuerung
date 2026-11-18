#!/usr/bin/env python3
"""JPEG mit Aufnahmedatum (EXIF DateTimeOriginal) versehen – ohne Zusatzprogramme (Slideshows, 17.11.2026).

  python3 werkzeuge/jpg_datum.py <ziel-ordner> bild1.jpg bild2.jpg …

Kopiert die Bilder nach <ziel-ordner>/slide-01.jpg … und gibt jedem ein Datum ab jetzt−N·10 s aufsteigend
(Bild 1 am ältesten, letztes Bild = jetzt) → feste Reihenfolge in Fotos/TikTok-Galerie. Vorhandenes EXIF wird ersetzt.
"""
import datetime, pathlib, struct, sys


def exif_block(dt):
    s = dt.strftime("%Y:%m:%d %H:%M:%S").encode() + b"\0"          # 20 Byte
    # TIFF (big endian): Header 8, IFD0 mit 1 Eintrag (ExifIFD-Zeiger), Exif-IFD mit 2 Einträgen
    ifd0_off = 8
    ifd0 = struct.pack(">H", 1) + struct.pack(">HHII", 0x8769, 4, 1, 0) + struct.pack(">I", 0)
    exif_off = ifd0_off + len(ifd0)
    ifd0 = struct.pack(">H", 1) + struct.pack(">HHII", 0x8769, 4, 1, exif_off) + struct.pack(">I", 0)
    daten_off = exif_off + 2 + 2 * 12 + 4
    exif = (struct.pack(">H", 2) + struct.pack(">HHII", 0x9003, 2, 20, daten_off)
            + struct.pack(">HHII", 0x9004, 2, 20, daten_off + 20) + struct.pack(">I", 0))
    tiff = b"MM\0*" + struct.pack(">I", ifd0_off) + ifd0 + exif + s + s
    app1 = b"Exif\0\0" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1


def ohne_app1(b):
    assert b[:2] == b"\xff\xd8", "kein JPEG"
    i, out = 2, bytearray(b[:2])
    while i < len(b) and b[i] == 0xFF and b[i + 1] not in (0xDA,):
        typ, ln = b[i + 1], struct.unpack(">H", b[i + 2:i + 4])[0]
        if typ != 0xE1:
            out += b[i:i + 2 + ln]
        i += 2 + ln
    return bytes(out) + b[i:]


def main():
    ziel = pathlib.Path(sys.argv[1]); ziel.mkdir(parents=True, exist_ok=True)
    bilder = [pathlib.Path(p) for p in sys.argv[2:]]
    jetzt = datetime.datetime.now().replace(microsecond=0)
    for i, p in enumerate(bilder):
        dt = jetzt - datetime.timedelta(seconds=10 * (len(bilder) - 1 - i))
        b = ohne_app1(p.read_bytes())
        (ziel / f"slide-{i + 1:02d}.jpg").write_bytes(b[:2] + exif_block(dt) + b[2:])
    print(f"✓ {len(bilder)} Bilder datiert ({(jetzt - datetime.timedelta(seconds=10 * (len(bilder) - 1))).time()}–{jetzt.time()})")


if __name__ == "__main__":
    main()
