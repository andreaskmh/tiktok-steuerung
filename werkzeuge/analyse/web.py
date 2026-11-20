#!/usr/bin/env python3
"""Browser-Version von statsKMH: app/web/vorlage.html + provision.json → app/web/statsKMH.html (danach als Artifact veröffentlichen)."""
import os
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..", "app", "web")
d = open(os.path.join(H, "provision.json")).read().replace("</", "<\\/")
open(os.path.join(W, "statsKMH.html"), "w").write(open(os.path.join(W, "vorlage.html")).read().replace("__DATEN__", d))
print(os.path.normpath(os.path.join(W, "statsKMH.html")))
