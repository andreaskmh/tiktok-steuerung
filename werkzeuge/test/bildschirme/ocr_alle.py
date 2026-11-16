"""OCR aller Roh-Bildschirmfotos → roh.json  {datei: [(text, x, y)]} in Punkten 334×735."""
import json, pathlib, subprocess, sys
H = pathlib.Path(__file__).resolve().parent
BIN = H.parent.parent / "bin"
aus = {}
for p in sorted((H / "roh").glob("*.png")):
    out = subprocess.run([str(BIN / "text"), str(p)], capture_output=True, text=True).stdout
    tx = []
    for z in out.splitlines():
        kopf, _, t = z.partition("\t")
        try:
            nx, ny, _, _ = map(float, kopf.split())
        except ValueError:
            continue
        tx.append([t, round(nx * 334, 1), round(ny * 735, 1)])
    aus[p.name] = tx
(H / "roh.json").write_text(json.dumps(aus, ensure_ascii=False))
print(len(aus))
