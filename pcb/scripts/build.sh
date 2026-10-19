#!/usr/bin/env bash
# Regenerate, check and export the eyocean carrier board.
#
#   pcb/scripts/build.sh            # schematic + PCB + ERC + DRC + exports
#
# Needs the KiCad 10 AppImage at ~/.bin/kicad.AppImage (override: KICAD_APPIMAGE).
# Fails (non-zero exit) on any ERC/DRC error, unrouted net or parity issue.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PCB_DIR="$(cd "$HERE/.." && pwd)"
APPIMAGE="${KICAD_APPIMAGE:-$HOME/.bin/kicad.AppImage}"
NAME=eyocean_carrier
OUT="$PCB_DIR/production"
REPORTS="$OUT/reports"

# Mount the AppImage once to reach the stock symbol / footprint libraries.
"$APPIMAGE" --appimage-mount >"${TMPDIR:-/tmp}/kicad_mount.$$" &
MOUNT_PID=$!
trap 'kill $MOUNT_PID 2>/dev/null || true; rm -f "${TMPDIR:-/tmp}/kicad_mount.$$"' EXIT
for _ in $(seq 50); do
  MNT="$(head -1 "${TMPDIR:-/tmp}/kicad_mount.$$" 2>/dev/null || true)"
  [[ -n "$MNT" && -d "$MNT/usr/share/kicad" ]] && break
  sleep 0.2
done
SHARE="$MNT/usr/share/kicad"
cli() { "$APPIMAGE" kicad-cli "$@"; }

mkdir -p "$REPORTS"
cd "$PCB_DIR"

echo "== schematic"
python3 "$HERE/gen_schematic.py" "$SHARE/symbols"
cli sch erc --severity-all --exit-code-violations \
  -o "$REPORTS/erc.rpt" "$NAME.kicad_sch"

echo "== pcb"
"$APPIMAGE" python3.11 "$HERE/gen_pcb.py" "$SHARE/footprints"
cli pcb drc --schematic-parity --severity-all --exit-code-violations \
  --refill-zones --save-board -o "$REPORTS/drc.rpt" "$NAME.kicad_pcb"

echo "== exports"
# JLCPCB fab set (their KiCad guide): Protel extensions, no X2/netlist
# attributes, no soldermask subtraction; Excellon mm, absolute origin,
# decimal zeros, alternate oval format, separate PTH/NPTH files.
JLC="$OUT/jlcpcb"
rm -rf "$OUT/gerbers" "$OUT/${NAME}_gerbers.zip" "$JLC"
mkdir -p "$JLC"
cli pcb export gerbers --no-x2 --no-netlist \
  -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  -o "$JLC/" "$NAME.kicad_pcb"
cli pcb export drill --format excellon --drill-origin absolute \
  --excellon-units mm --excellon-zeros-format decimal \
  --excellon-oval-format alternate --excellon-separate-th \
  -o "$JLC/" "$NAME.kicad_pcb"
(cd "$JLC" && rm -f "../${NAME}_jlcpcb.zip" && zip -q "../${NAME}_jlcpcb.zip" ./*)
cli pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet \
  -l F.Cu,F.Silkscreen,F.Fab,Edge.Cuts -o "$OUT/${NAME}_top.svg" "$NAME.kicad_pcb"
cli pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet \
  -l B.Cu,Edge.Cuts -o "$OUT/${NAME}_bottom.svg" "$NAME.kicad_pcb"
cli sch export pdf -o "$OUT/${NAME}_schematic.pdf" "$NAME.kicad_sch"
cli pcb render --side top --quality basic -w 1600 --height 1000 \
  -o "$OUT/${NAME}_3d_top.png" "$NAME.kicad_pcb"
cli pcb export step --subst-models --force -o "$OUT/${NAME}.step" "$NAME.kicad_pcb" \
  >/dev/null || echo "(STEP export skipped)"

echo "== done: $OUT"
ls -1 "$OUT" "$JLC"
