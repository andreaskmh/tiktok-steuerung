#!/bin/zsh
# Übersetzt alle Swift-Werkzeuge nach werkzeuge/bin/ (Ordner ist nicht im Git).
set -e
HIER=${0:A:h}
mkdir -p $HIER/bin
for f in $HIER/*.swift $HIER/test/*.swift; do
  n=${f:t:r}
  if [[ ! -x $HIER/bin/$n || $f -nt $HIER/bin/$n ]]; then
    swiftc -O -o $HIER/bin/$n $f && echo "gebaut: $n"
  fi
done
