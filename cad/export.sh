#!/usr/bin/env bash
# Export the printable enclosure parts (STL + 3MF) and the preview render.
#
#   cad/export.sh            # writes cad/export/enclosure_{bottom,lid}.{stl,3mf}
#
# Parts are exported in print orientation: base floor-down, lid roof-down.
# Pass Customizer overrides through, e.g.  cad/export.sh -D bolt_len=20
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export OPENSCADPATH="$HERE${OPENSCADPATH:+:$OPENSCADPATH}"
[[ -f "$HERE/BOSL2/std.scad" ]] || {
  echo "BOSL2 missing: run 'git submodule update --init'" >&2; exit 1; }

mkdir -p "$HERE/export"
for part in bottom lid; do
  for ext in stl 3mf; do
    out="$HERE/export/enclosure_$part.$ext"
    openscad --hardwarnings "$@" -D "part=\"$part\"" -o "$out" \
      "$HERE/enclosure.scad" 2>&1 | grep -E "ERROR|WARNING|Simple" || true
    [[ -s "$out" ]] || { echo "export failed: $out" >&2; exit 1; }
    echo "wrote $out"
  done
done
