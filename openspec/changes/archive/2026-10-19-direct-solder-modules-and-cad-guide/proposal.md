## Why

The first hardware change assumed both modules plug into 8.5 mm female sockets. You'll instead solder the ESP32-S3 SuperMini and the CC1101 directly onto the carrier through their male headers, with no socket (no C27985230 or other socket part). That drops both modules 8.5 mm, so every enclosure height (USB-C hole, SMA hole, case split, roof, bolt length) is wrong for the real build. There is also no single document explaining how the case heights are derived or how to rebuild the printable files.

## What Changes

- **BREAKING (enclosure geometry):** recompute the case stack-up for direct soldering. Each module now rests on its own male-header plastic spacer, about 2.5 mm above the carrier top, with a separate spacer height for each module. The case goes from about 26.6 mm to about 18.1 mm tall. The USB-C hole, SMA hole and case split all move down.
- **Fasteners:** default to M2 × 16 flat-head bolts, sitting flush. The hex nut pocket gets deeper and the base standoffs thicker (Ø6.5) so the nut wall stays printable. Shorter bolts still get a counterbore.
- **Pin tails:** the long header pins come through the carrier. The case requires them trimmed to ≤ 2.5 mm, and the model refuses tails longer than the standoff room.
- **PCB (BREAKING board size):** shorten the carrier from 56 to 53.5 mm (mounting holes move to a 47.5 × 26 mm pattern). At the lower CC1101 height, the SMA barrel (Ø6.3) would otherwise touch the carrier. The board now ends at the CC1101's edge so the SMA overhangs it. The routing, nets and pin map are unchanged.
- **Specs catch up with the board:** record the single 10 µF 0603 decoupling cap (LCSC C19702) chosen earlier, and switch socket wording to direct soldering.
- **New `cad/README.md` build guide:** prerequisites (OpenSCAD, BOSL2 submodule), the height stack-up table with every formula, what to measure on your own parts, Customizer parameters, how to export STL/3MF, slicer settings, bill of hardware and assembly steps.
- Re-export the JLCPCB Gerbers, the STL/3MF parts and the preview render. Update the top-level README parts list (no female headers; M2 × 16 bolts; new case size).

**Note on the working tree:** an interrupted session already applied part of this to the files: the `cad/enclosure.scad` stack-up, `BOARD_W = 53.5` in `pcb/scripts/board_def.py`, and a PCB/Gerber rebuild. The STL export and docs were not done. Implementation must review and verify these edits against this plan, not assume they are correct.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `connecting-pcb`: modules are soldered directly instead of socketed; board length 53.5 mm with the SMA overhanging the edge; single 10 µF decoupling capacitor.
- `enclosure-case`: case heights derived from a direct-solder stack-up (per-module header spacers, pin-tail room, SMA/carrier clearance); M2 × 16 flush bolts; a `cad/README.md` build guide documents the stack-up and the build.

## Impact

- `cad/enclosure.scad`, `cad/export.sh`, new `cad/README.md`, `cad/enclosure.png`, `cad/export/*.stl|3mf`.
- `pcb/scripts/board_def.py` (board width), regenerated `pcb/eyocean_carrier.kicad_*`, `pcb/production/*` (JLCPCB zip and Gerbers).
- `README.md` (parts list, case size, assembly).
- No firmware or pin-map change; `esphome/` is untouched.
- Parts already ordered: the 56 mm boards and female headers from the first design no longer match this case.
