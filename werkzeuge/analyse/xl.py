"""Minimaler xlsx-Leser ohne Zusatzpakete: xl.lesen(pfad) -> {blattname: [zeilen]}."""
import re, sys, zipfile, xml.etree.ElementTree as ET

N = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
     "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _spalte(ref):
    s = re.match(r"[A-Z]+", ref).group(0); n = 0
    for c in s:
        n = n * 26 + ord(c) - 64
    return n - 1


def lesen(pfad):
    z = zipfile.ZipFile(pfad)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", N):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % N["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find("m:sheets", N):
        ziel = rels[s.get("{%s}id" % N["r"])].lstrip("/")
        ziel = ziel if ziel.startswith("xl/") else "xl/" + ziel
        zeilen = []
        for row in ET.fromstring(z.read(ziel)).iter("{%s}row" % N["m"]):
            werte = {}
            for c in row.findall("m:c", N):
                t, v = c.get("t"), c.find("m:v", N)
                if t == "s" and v is not None:
                    x = shared[int(v.text)]
                elif t == "inlineStr":
                    x = "".join(e.text or "" for e in c.iter("{%s}t" % N["m"]))
                else:
                    x = v.text if v is not None else None
                werte[_spalte(c.get("r"))] = x
            zeilen.append([werte.get(i) for i in range(max(werte) + 1)] if werte else [])
        out[s.get("name")] = zeilen
    return out


if __name__ == "__main__":
    for name, z in lesen(sys.argv[1]).items():
        print(name, len(z))
        for r in z[:int(sys.argv[2]) if len(sys.argv) > 2 else 3]:
            print(r)
