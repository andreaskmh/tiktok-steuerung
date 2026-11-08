// hid_maus – Arduino Pro Micro (ATmega32U4) als echte USB-Maus + Tastatur.
// Gesteuert über die serielle Schnittstelle (115200 Baud, eine Zeile = ein Befehl).
// Antwort immer "OK ..." oder "ERR ...".
//
// Befehle:
//   PING                       -> OK PONG
//   SCROLL dx dy n [ms]        n Schritte Mausrad; dy = vertikal (+ hoch, - runter),
//                              dx = horizontal (über Shift + Rad, so macht es macOS bei echten Mäusen)
//   SHIFTSCROLL n [ms]         n Rad-Rasten mit gedrückter Shift-Taste (n negativ = andere Richtung)
//   MOVE dx dy                 Zeiger relativ bewegen (in Stücken bis 127)
//   DRAG dx dy steps [ms]      linke Taste halten, in steps Schritten um dx/dy ziehen, loslassen
//   CLICK [L|R|M]              einmal klicken
//   PRESS [L|R|M] / RELEASE [L|R|M]
//   KEY name                   eine Taste: LEFT RIGHT UP DOWN RETURN ESC TAB SPACE oder ein Zeichen
//   TYPE text                  Text tippen (nur ASCII, US-Layout!)
//   STOP                       alles loslassen (Maustasten + Tasten)
//
// Sicherheit: Jeder Wert wird begrenzt (n <= 50, steps <= 200, ms <= 500),
// DRAG lässt am Ende immer los; STOP lässt jederzeit alles los.

#include <Mouse.h>
#include <Keyboard.h>

const long BAUD = 115200;
String zeile;

int begrenze(long v, long lo, long hi) { return (int)(v < lo ? lo : (v > hi ? hi : v)); }

// zerlegt "a b c" in Zahlen; gibt Anzahl zurück
int zahlen(const String &s, long *out, int max) {
  int n = 0, i = 0;
  while (n < max && i < (int)s.length()) {
    while (i < (int)s.length() && s[i] == ' ') i++;
    if (i >= (int)s.length()) break;
    int j = i;
    while (j < (int)s.length() && s[j] != ' ') j++;
    out[n++] = s.substring(i, j).toInt();
    i = j;
  }
  return n;
}

uint8_t taste(const String &t) {
  if (t == "L" || t == "") return MOUSE_LEFT;
  if (t == "R") return MOUSE_RIGHT;
  if (t == "M") return MOUSE_MIDDLE;
  return 0;
}

void bewege(long dx, long dy) {
  while (dx != 0 || dy != 0) {
    int sx = begrenze(dx, -127, 127), sy = begrenze(dy, -127, 127);
    Mouse.move(sx, sy, 0);
    dx -= sx; dy -= sy;
    delay(2);
  }
}

void rad(int n, int ms, bool shift) {
  n = begrenze(n, -50, 50);
  if (shift) { Keyboard.press(KEY_LEFT_SHIFT); delay(15); }
  int schritt = n > 0 ? 1 : -1;
  for (int i = 0; i < abs(n); i++) { Mouse.move(0, 0, schritt); delay(ms); }
  if (shift) { delay(15); Keyboard.release(KEY_LEFT_SHIFT); }
}

void ausfuehren(String z) {
  z.trim();
  if (z.length() == 0) return;
  int sp = z.indexOf(' ');
  String cmd = sp < 0 ? z : z.substring(0, sp);
  String rest = sp < 0 ? "" : z.substring(sp + 1);
  cmd.toUpperCase();
  long v[4] = {0, 0, 0, 0};
  int n = zahlen(rest, v, 4);

  if (cmd == "PING") { Serial.println("OK PONG"); return; }
  if (cmd == "STOP") { Mouse.release(MOUSE_ALL); Keyboard.releaseAll(); Serial.println("OK STOP"); return; }

  if (cmd == "SCROLL") {
    if (n < 3) { Serial.println("ERR SCROLL dx dy n [ms]"); return; }
    int ms = begrenze(n > 3 ? v[3] : 20, 1, 500);
    int anz = begrenze(v[2], 1, 50);
    for (int i = 0; i < anz; i++) {
      if (v[1] != 0) { Mouse.move(0, 0, v[1] > 0 ? 1 : -1); }
      if (v[0] != 0) { rad(v[0] > 0 ? 1 : -1, 1, true); }
      delay(ms);
    }
    Serial.println("OK SCROLL"); return;
  }
  if (cmd == "SHIFTSCROLL") {
    if (n < 1) { Serial.println("ERR SHIFTSCROLL n [ms]"); return; }
    rad(v[0], begrenze(n > 1 ? v[1] : 20, 1, 500), true);
    Serial.println("OK SHIFTSCROLL"); return;
  }
  if (cmd == "MOVE") {
    if (n < 2) { Serial.println("ERR MOVE dx dy"); return; }
    bewege(begrenze(v[0], -3000, 3000), begrenze(v[1], -3000, 3000));
    Serial.println("OK MOVE"); return;
  }
  if (cmd == "DRAG") {
    if (n < 3) { Serial.println("ERR DRAG dx dy steps [ms]"); return; }
    long dx = begrenze(v[0], -3000, 3000), dy = begrenze(v[1], -3000, 3000);
    int steps = begrenze(v[2], 1, 200), ms = begrenze(n > 3 ? v[3] : 8, 1, 500);
    Mouse.press(MOUSE_LEFT); delay(30);
    long gx = 0, gy = 0;
    for (int i = 1; i <= steps; i++) {
      long zx = dx * i / steps, zy = dy * i / steps;
      bewege(zx - gx, zy - gy); gx = zx; gy = zy;
      delay(ms);
    }
    delay(30); Mouse.release(MOUSE_LEFT);
    Serial.println("OK DRAG"); return;
  }
  if (cmd == "CLICK") { uint8_t t = taste(rest); if (!t) { Serial.println("ERR L|R|M"); return; } Mouse.click(t); Serial.println("OK CLICK"); return; }
  if (cmd == "PRESS") { uint8_t t = taste(rest); if (!t) { Serial.println("ERR L|R|M"); return; } Mouse.press(t); Serial.println("OK PRESS"); return; }
  if (cmd == "RELEASE") { uint8_t t = taste(rest); if (!t) { Serial.println("ERR L|R|M"); return; } Mouse.release(t); Serial.println("OK RELEASE"); return; }
  if (cmd == "KEY") {
    String k = rest; k.toUpperCase();
    uint8_t code = 0;
    if (k == "LEFT") code = KEY_LEFT_ARROW; else if (k == "RIGHT") code = KEY_RIGHT_ARROW;
    else if (k == "UP") code = KEY_UP_ARROW; else if (k == "DOWN") code = KEY_DOWN_ARROW;
    else if (k == "RETURN") code = KEY_RETURN; else if (k == "ESC") code = KEY_ESC;
    else if (k == "TAB") code = KEY_TAB; else if (k == "SPACE") code = ' ';
    else if (rest.length() == 1) code = rest[0];
    if (!code) { Serial.println("ERR KEY name"); return; }
    Keyboard.write(code); Serial.println("OK KEY"); return;
  }
  if (cmd == "TYPE") { Keyboard.print(rest); Serial.println("OK TYPE"); return; }
  Serial.println("ERR unbekannt: " + cmd);
}

void setup() {
  Serial.begin(BAUD);
  Mouse.begin();
  Keyboard.begin();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { ausfuehren(zeile); zeile = ""; }
    else if (zeile.length() < 200) zeile += c;
  }
}
