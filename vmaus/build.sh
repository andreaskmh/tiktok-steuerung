#!/bin/zsh
# Baut vmaus/bin/vmaus. Braucht die Client-Header in vmaus/quelle/
# (Karabiner-DriverKit-VirtualHIDDevice 8.8.0, client_protocol_version 7; nicht im Git).
set -e
HIER=${0:A:h}; Q=$HIER/quelle
if [[ ! -d $Q/include ]]; then
  echo "Hole Quellcode (pqrs-org/Karabiner-DriverKit-VirtualHIDDevice v8.8.0)…"
  T=$(mktemp -d); git clone -q --depth 1 --branch v8.8.0 https://github.com/pqrs-org/Karabiner-DriverKit-VirtualHIDDevice.git $T/vhid
  mkdir -p $Q/vendor; cp -R $T/vhid/include $Q/; cp -R $T/vhid/vendor/vendor $Q/vendor/; cp $T/vhid/version.json $T/vhid/LICENSE.md $Q/
fi
mkdir -p $HIER/bin
clang -fno-objc-arc -O2 -c -isystem $Q/vendor/vendor/include \
  $Q/vendor/vendor/src/pqrs/osx/autorelease_pool/PQRSOSXAutoreleasePoolImpl.m -o $HIER/bin/pool.o
clang++ -std=c++23 -O2 -Wall -isystem $Q/vendor/vendor/include -isystem $Q/include \
  $HIER/vmaus.cpp $HIER/bin/pool.o -framework Foundation -framework IOKit -o $HIER/bin/vmaus
echo "gebaut: $HIER/bin/vmaus (Protokoll $(grep -o '"client_protocol_version": [0-9]*' $Q/version.json | grep -o '[0-9]*$'))"
