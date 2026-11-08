# Änderungen

- **08.11.2026** – Projekt angelegt: Test-Werkzeuge vom Wisch-Versuch übernommen (`werkzeuge/test/`),
  Fenster-Aufnahme + Zeiger-Werkzeug, Mini-Gerät-Sketch (noch nicht geflasht), Übergabe-Format.
- **08.11.2026** – `geraet/attrappe.py` (Gerät simulieren ohne Arduino), `GERAET_PORT` in `geraet.py`,
  `zeiger` findet `fenster` jetzt auch ohne Pfadaufruf. Getestet: zeiger rel, Protokoll, Wisch-Test komplett mit Attrappe.
- **08.11.2026** – Weg „echtere Software-Eingaben“ getestet (`werkzeuge/test/echt.swift`, `felder.swift`): wirkungslos.
- **08.11.2026** – `vmaus/`: virtuelle Maus über Karabiner-DriverKit-VirtualHIDDevice 8.8.0 (root-Dienst + Socket nur für Artur,
  einmalige Einrichtung per `einrichten.sh`), `geraet.py` spricht auch mit ihr. Der halbe Wisch am Anfang war Arturs Trackpad.
