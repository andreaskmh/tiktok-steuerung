// vmaus – virtuelle USB-Maus + Tastatur über Karabiner-DriverKit-VirtualHIDDevice.
// Läuft als root (LaunchDaemon) und nimmt Befehle über ein Unix-Socket an, das nur Arturs Benutzer öffnen darf.
// Gleiche Befehle wie das Mini-Gerät (geraet/hid_maus), eine Zeile = ein Befehl, Antwort "OK …" / "ERR …":
//   PING | STATUS | SCROLL dx dy n [ms] | SHIFTSCROLL n [ms] | MOVE dx dy | DRAG dx dy steps [ms]
//   CLICK [L|R|M] | PRESS [L|R|M] | RELEASE [L|R|M] | KEY name | STOP
// SCROLL: dx = horizontales Rad (echte Rad-Achse), dy = vertikal; Wert je Schritt, begrenzt auf ±10.
//
// Aufruf: vmaus [socket-pfad] [uid]   (Standard /var/run/tiktok-maus.sock, uid 501)

#include <pqrs/karabiner/driverkit/virtual_hid_device_driver.hpp>
#include <pqrs/karabiner/driverkit/virtual_hid_device_service.hpp>
#include <pqrs/osx/autorelease_pool.hpp>
#include <atomic>
#include <csignal>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace hr = pqrs::karabiner::driverkit::virtual_hid_device_driver::hid_report;
namespace svc = pqrs::karabiner::driverkit::virtual_hid_device_service;

static std::atomic<bool> pointing_ready{false}, keyboard_ready{false};
static std::unique_ptr<svc::client> client;
static std::mutex mtx;
static hr::buttons knoepfe; // aktueller Tastenzustand der Maus

static long begrenze(long v, long lo, long hi) { return v < lo ? lo : (v > hi ? hi : v); }
static void ms(long n) { std::this_thread::sleep_for(std::chrono::milliseconds(n)); }

static void zeiger(long dx, long dy, long vw, long hw) {
  hr::pointing_input r;
  r.buttons = knoepfe;
  r.x = static_cast<uint8_t>(static_cast<int8_t>(begrenze(dx, -127, 127)));
  r.y = static_cast<uint8_t>(static_cast<int8_t>(begrenze(dy, -127, 127)));
  r.vertical_wheel = static_cast<uint8_t>(static_cast<int8_t>(begrenze(vw, -127, 127)));
  r.horizontal_wheel = static_cast<uint8_t>(static_cast<int8_t>(begrenze(hw, -127, 127)));
  std::lock_guard<std::mutex> l(mtx);
  if (client) client->async_post_report(r);
}

static void bewege(long dx, long dy) {
  while (dx || dy) {
    long sx = begrenze(dx, -127, 127), sy = begrenze(dy, -127, 127);
    zeiger(sx, sy, 0, 0); dx -= sx; dy -= sy; ms(2);
  }
}

static void tastatur(bool shift, uint16_t key) {
  hr::keyboard_input r;
  if (shift) r.modifiers.insert(hr::modifier::left_shift);
  if (key) r.keys.insert(key);
  std::lock_guard<std::mutex> l(mtx);
  if (client) client->async_post_report(r);
}

static uint8_t knopf(const std::string& t) {
  if (t.empty() || t == "L") return 1;
  if (t == "R") return 2;
  if (t == "M") return 3;
  return 0;
}

static std::string ausfuehren(std::string z) {
  while (!z.empty() && (z.back() == '\r' || z.back() == ' ')) z.pop_back();
  std::istringstream in(z);
  std::string cmd; in >> cmd;
  for (auto& c : cmd) c = toupper(c);
  if (cmd.empty()) return "";
  std::string rest; std::getline(in, rest);
  while (!rest.empty() && rest.front() == ' ') rest.erase(0, 1);
  std::vector<long> v; { std::istringstream r(rest); long x; while (r >> x) v.push_back(x); }

  if (cmd == "PING") return "OK PONG";
  if (cmd == "STATUS") return std::string("OK pointing=") + (pointing_ready ? "1" : "0") + " keyboard=" + (keyboard_ready ? "1" : "0");
  if (!pointing_ready) return "ERR virtuelle Maus nicht bereit (Treiber aktiviert? Daemon läuft?)";

  if (cmd == "STOP") { knoepfe.clear(); zeiger(0, 0, 0, 0); if (keyboard_ready) tastatur(false, 0); return "OK STOP"; }
  if (cmd == "SCROLL") {
    if (v.size() < 3) return "ERR SCROLL dx dy n [ms]";
    long n = begrenze(v[2], 1, 50), w = begrenze(v.size() > 3 ? v[3] : 20, 1, 500);
    long hw = begrenze(v[0], -10, 10), vw = begrenze(v[1], -10, 10);
    for (long i = 0; i < n; i++) { zeiger(0, 0, vw, hw); ms(w); }
    return "OK SCROLL";
  }
  if (cmd == "SHIFTSCROLL") {
    if (v.empty()) return "ERR SHIFTSCROLL n [ms]";
    if (!keyboard_ready) return "ERR Tastatur nicht bereit";
    long n = begrenze(v[0], -50, 50), w = begrenze(v.size() > 1 ? v[1] : 20, 1, 500);
    tastatur(true, 0); ms(15);
    for (long i = 0; i < labs(n); i++) { zeiger(0, 0, n > 0 ? 1 : -1, 0); ms(w); }
    ms(15); tastatur(false, 0);
    return "OK SHIFTSCROLL";
  }
  if (cmd == "MOVE") {
    if (v.size() < 2) return "ERR MOVE dx dy";
    bewege(begrenze(v[0], -3000, 3000), begrenze(v[1], -3000, 3000));
    return "OK MOVE";
  }
  if (cmd == "DRAG") {
    if (v.size() < 3) return "ERR DRAG dx dy steps [ms]";
    long dx = begrenze(v[0], -3000, 3000), dy = begrenze(v[1], -3000, 3000);
    long st = begrenze(v[2], 1, 200), w = begrenze(v.size() > 3 ? v[3] : 8, 1, 500);
    knoepfe.insert(1); zeiger(0, 0, 0, 0); ms(30);
    long gx = 0, gy = 0;
    for (long i = 1; i <= st; i++) {
      long zx = dx * i / st, zy = dy * i / st;
      bewege(zx - gx, zy - gy); gx = zx; gy = zy; ms(w);
    }
    ms(30); knoepfe.erase(1); zeiger(0, 0, 0, 0);
    return "OK DRAG";
  }
  if (cmd == "CLICK" || cmd == "PRESS" || cmd == "RELEASE") {
    uint8_t k = knopf(rest);
    if (!k) return "ERR L|R|M";
    if (cmd != "RELEASE") { knoepfe.insert(k); zeiger(0, 0, 0, 0); }
    if (cmd == "CLICK") ms(40);
    if (cmd != "PRESS") { knoepfe.erase(k); zeiger(0, 0, 0, 0); }
    return "OK " + cmd;
  }
  if (cmd == "KEY") {
    if (!keyboard_ready) return "ERR Tastatur nicht bereit";
    std::string k = rest; for (auto& c : k) c = toupper(c);
    namespace u = pqrs::hid::usage::keyboard_or_keypad;
    uint16_t code = 0;
    if (k == "LEFT") code = type_safe::get(u::keyboard_left_arrow);
    else if (k == "RIGHT") code = type_safe::get(u::keyboard_right_arrow);
    else if (k == "UP") code = type_safe::get(u::keyboard_up_arrow);
    else if (k == "DOWN") code = type_safe::get(u::keyboard_down_arrow);
    else if (k == "RETURN") code = type_safe::get(u::keyboard_return_or_enter);
    else if (k == "ESC") code = type_safe::get(u::keyboard_escape);
    else if (k == "SPACE") code = type_safe::get(u::keyboard_spacebar);
    if (!code) return "ERR KEY LEFT|RIGHT|UP|DOWN|RETURN|ESC|SPACE";
    tastatur(false, code); ms(30); tastatur(false, 0);
    return "OK KEY";
  }
  return "ERR unbekannt: " + cmd;
}

int main(int argc, char** argv) {
  std::string pfad = argc > 1 ? argv[1] : "/var/run/tiktok-maus.sock";
  uid_t uid = argc > 2 ? static_cast<uid_t>(atoi(argv[2])) : 501;
  signal(SIGPIPE, SIG_IGN);

  pqrs::dispatcher::extra::initialize_shared_dispatcher(pqrs::osx::autorelease_pool::execute_with_autorelease_pool);
  client = std::make_unique<svc::client>();
  client->connected.connect([] {
    std::cerr << "verbunden" << std::endl;
    svc::virtual_hid_keyboard_parameters p;
    p.set_country_code(pqrs::hid::country_code::us);
    client->async_virtual_hid_keyboard_initialize(p);
    client->async_virtual_hid_pointing_initialize();
  });
  client->connect_failed.connect([](auto&& e) { std::cerr << "connect_failed " << e << std::endl; });
  client->closed.connect([] { std::cerr << "closed" << std::endl; pointing_ready = false; keyboard_ready = false; });
  client->error_occurred.connect([](auto&& e) { std::cerr << "error " << e << std::endl; });
  client->driver_version_mismatched.connect([](auto&& m) { if (m) std::cerr << "driver_version_mismatched" << std::endl; });
  client->virtual_hid_pointing_ready.connect([](auto&& r) { if (r != pointing_ready) std::cerr << "pointing_ready " << r << std::endl; pointing_ready = r; });
  client->virtual_hid_keyboard_ready.connect([](auto&& r) { if (r != keyboard_ready) std::cerr << "keyboard_ready " << r << std::endl; keyboard_ready = r; });
  client->async_start();

  int s = socket(AF_UNIX, SOCK_STREAM, 0);
  sockaddr_un a{}; a.sun_family = AF_UNIX;
  strncpy(a.sun_path, pfad.c_str(), sizeof(a.sun_path) - 1);
  unlink(pfad.c_str());
  if (bind(s, reinterpret_cast<sockaddr*>(&a), sizeof(a)) != 0) { perror("bind"); return 1; }
  chown(pfad.c_str(), uid, 0);
  chmod(pfad.c_str(), 0600);
  listen(s, 4);
  std::cerr << "lauscht auf " << pfad << " (uid " << uid << ")" << std::endl;

  while (true) {
    int c = accept(s, nullptr, nullptr);
    if (c < 0) continue;
    std::string puffer; char buf[256];
    ssize_t n;
    while ((n = read(c, buf, sizeof(buf))) > 0) {
      puffer.append(buf, n);
      size_t p;
      while ((p = puffer.find('\n')) != std::string::npos) {
        std::string zeile = puffer.substr(0, p); puffer.erase(0, p + 1);
        if (zeile.size() > 200) zeile.resize(200);
        std::string antwort = ausfuehren(zeile);
        if (!antwort.empty()) { antwort += "\n"; write(c, antwort.data(), antwort.size()); }
      }
      if (puffer.size() > 1000) puffer.clear();
    }
    close(c);
  }
}
