## Context

See `proposal.md` for the motivation. The current state, from `cad/enclosure.scad` at HEAD (`99c94ca`), is a single `module_z = pcb_t + socket_h(8.5) + pin_spacer_h(2.5) = 12.6`, giving a 26.6 mm case with M2 × 25 bolts. The carrier (`pcb/scripts/board_def.py`) is 56 × 32 mm, and the CC1101's west edge is at `x = 25.5`, so its east edge (`53.5`) and the SMA sit 2.5 mm inside the board's east edge.

An interrupted session left uncommitted edits that already follow most of this design:
- `enclosure.scad`: per-module spacers, `socket_h = 0`, `sma_axis_h`, `pin_tail`, `standoff_d`, `bolt_len 16`, `nut_pocket 4.0`, new asserts.
- `board_def.py`: `BOARD_W = 53.5`.
- A PCB/Gerber rebuild, whose DRC result was not re-read after the restart.

The STL export, `cad/README.md` and the top-level README were not done.

## Goals / Non-Goals

**Goals:**
- One documented stack-up drives every case height, with separate spacers per module.
- The board and case physically fit with directly soldered modules: no SMA/carrier collision, room for trimmed pin tails, flush bolts with a common length.
- `cad/README.md` is a complete build guide; the derivation lives there, not only in code comments.

**Non-Goals:**
- No routing, net, pin-map or firmware change.
- No new socket footprints or dummy holes for C27985230 (dropped when you chose direct soldering).
- No change to the case's XY layout logic, USB/SMA opening sizes or WiFi slots, beyond what follows from the heights.

## Decisions

### 1. Stack-up (z = 0 at the carrier's bottom face)

| z (mm) | Item | Formula / default |
| --- | --- | --- |
| −5.5 | Case bottom | `z_bot = −standoff_h − floor_t` = −3.5 − 2.0 |
| −3.5 | Floor top | `−standoff_h`; room for pin tails ≤ `standoff_h − 0.5` |
| 0 → 1.6 | Carrier | `pcb_t` |
| 1.6 → 4.1 | Male-header plastic spacers | `sm_spacer_h`, `cc_spacer_h` = 2.5 (+ `socket_h` = 0) |
| 4.1 | SuperMini board bottom (`sm_z`) | `pcb_t + socket_h + sm_spacer_h` |
| 4.1 | CC1101 board bottom (`cc_z`) | `pcb_t + socket_h + cc_spacer_h` |
| 4.7 | SMA axis = case split | `cc_z + sma_axis_h` (0.6 = centred on the 1.2 mm board) |
| 6.73 | USB-C centre | `sm_z + sm_t(1.0) + usb_shell.y(3.26)/2` |
| 9.1 | Tallest part | max(`sm_z + sm_t + 3.26` = 8.36, `cc_z + cc_h(5.0)` = 9.1) |
| 10.6 | Roof underside | + `top_clear` 1.5 |
| 12.6 | Case top | + `roof_t` 2.0 → **18.1 mm overall** (`60.5 × 37` footprint) |

- **Rationale:** with direct soldering a module's height is just the board plus its header spacer. Splitting `pin_spacer_h` into one per module matters because the CC1101 arrives with its header pre-fitted (spacer K is not given in `CC1101_specs/`), while you fit the SuperMini's header yourself.
- **Alternative considered:** keep one shared spacer. Rejected because a mismatch between the two modules would silently misplace either the USB-C or the SMA hole, whose vertical slack is only ±0.22 / ±0.1 mm.

### 2. Shorten the carrier to 53.5 mm (end at the CC1101 edge)
At `cc_z = 4.1` the SMA barrel's bottom is `4.7 − 3.15 = 1.55`, below the carrier top (1.6). Over the 2.5 mm of board past the module edge, that is a collision.
- **Decision:** `BOARD_W = 53.5` so the board ends exactly at the module's east edge. The holes follow (`x = 3, 50.5`); the case's east wall is still set by the SMA (`x_in1 = cc_x + cc_len + sma_body = 56`).
- **Alternatives considered:**
  - Move the CC1101 2.5 mm east: re-routes the corridor and grows the case.
  - Raise `cc_spacer_h`: depends on the module's pre-fitted header.
  - Cut a notch in the board under the SMA: more complex for the same effect.
- An assert in the model guards it: if `cc_x + cc_len < board_w` and the SMA bottom is below `pcb_t + 0.2`, the model refuses to build.

### 3. Fasteners: M2 × 16 flush
With `z_bot = −5.5` and `z_top = 12.6` the stack is 18.1 mm. The bolt tip sits 0.3 mm past the nut, which seats at the pocket top: `tip_z = z_bot + nut_pocket − nut_h − 0.3`. With `nut_pocket = 4.0`, a 16 mm bolt ends exactly flush (`head_z = 12.6`). M2 × 16 is a stock DIN 965 / ISO 10642 length.
- **Wall:** a 4.0 mm-deep hex pocket (4.73 mm across corners) reaches 1.5 mm up into the standoff, so `standoff_d = 6.5` leaves 0.88 mm of wall. The old Ø5.5 left 0.38 mm. The lid clamp pillars stay Ø5.5. An assert enforces at least 0.7 mm.
- **Shorter bolts:** M2 × 14 and × 12 still work via the existing counterbore logic.
- **Auto nut pocket (found during implementation):** a fixed 4.0 mm pocket made M2 × 16 "too long" as soon as a measured spacer lowered the roof by 0.2 mm. `nut_pocket = 0` now means automatic: the depth that puts a `bolt_len` head flush, clamped to `[nut_h + 0.6, floor_t + standoff_h − 1.2]`. It is 4.0 mm with the defaults; a number forces a fixed depth.

### 4. Pin tails
The header's long side (about 6 mm) through a 1.6 mm carrier leaves about 4.4 mm below the board. The base only has 3.5 mm.
- **Decision:** the build guide says to trim tails to ≤ 2.5 mm (`pin_tail`). The model asserts `standoff_h ≥ pin_tail + 0.5`.
- **Alternative considered:** raise `standoff_h` to 5 mm. Rejected: it adds 1.5 mm of height for something flush cutters fix in a minute; it remains a parameter for builders who won't trim.

### 5. CC1101 header is centred on the module's short edge (found during implementation)
The first design read the CC1101 table's `F = 1.5` as "row 1 is 1.5 mm from the module's north edge". Measuring both `CC1101_specs/` drawings shows the four header rows are **centred** on the 15 mm edge: the row centre is at 7.54 mm on the size drawing and about 7.5 mm on the pin-out drawing. The first column is about 1.5 mm from the west edge, as before. The table is unreliable here; `G1 = 1.5`, for example, spans about 8 mm in the drawing.
- **Decision:** keep the eight pads where they are (row 1 at board `y = 12.25`), so the copper, routing and DRC are unchanged. Place the module around them: `CC_ROW_OFF = (15 − 3 × 2.54) / 2 = 3.69`, so `CC_Y = 12.25 − 3.69 = 8.56` (was 10.75). The module now spans board `y 8.56–23.56`.
- **Effects:**
  - The SMA axis moves from board `y` 17.35 to 15.16, and the case's SMA hole and U-slot follow (`cc_y = 8.56` in `enclosure.scad`).
  - The Fab outline and the assembly reference model move with the module.
  - It still clears the lid pillars: `y ≥ 5.75` north, `≤ 26.25` south.
- **Alternative considered:** move the pads 2.19 mm south to keep `CC_Y = 10.75`. Rejected: it reroutes the B.Cu lanes toward the SuperMini's south header row for no benefit.

### 6. `cad/README.md` structure
Sections:
1. Overview, with the render image.
2. Prerequisites: OpenSCAD ≥ 2021.01; BOSL2 via `git submodule update --init`.
3. Stack-up table (Decision 1), with formulas and a short note on how the modules sit on their spacers.
4. Measure your parts: carrier top → module bottom for each module, SMA axis above the module bottom, USB-C shell height, header pin length. Each maps to its parameter.
5. Build: `cad/export.sh` (with `-D` overrides), output files, Customizer use, headless PNG render.
6. Print settings, from the openscad-bosl2 house style: PETG, 0.2 mm layers, 3 walls, 20 % infill, no supports; base floor-down, lid roof-down.
7. Hardware: 4× M2 × 16 flat-head bolts, 4× M2 hex nuts, 433 MHz SMA antenna.
8. Assembly: solder, trim tails, drop in, close, nuts, bolts, antenna.
9. Troubleshooting: USB plug won't seat, SMA rubs, bolt too long or short.

## Risks / Trade-offs

- **[Risk] CC1101 header spacer or SMA axis differs from the defaults.** If K is not 2.5, or the SMA isn't centred on the board, the SMA hole and case split are off. → Mitigation: per-module parameters, measurement steps in the README, and the existing ±0.1 mm SMA slack called out (the README suggests `sma_hole_d = 7.0` if it rubs).
- **[Risk] The 53.5 mm board edge coincides with the CC1101 edge.** Hand placement tolerance could leave the module 0.1–0.3 mm inboard. → Mitigation: the SMA bottom then clears the carrier top only by the overhang; the README notes to keep the module pushed east, and `sma_axis_h` can be set from a measurement.
- **[Risk] Uncommitted edits from the interrupted session may be incomplete or inconsistent** (e.g. a rebuild that stopped mid-way). → Mitigation: the first implementation task diff-reviews them and reruns the full PCB build and CAD export from scratch.
- **[Trade-off] Boards already made at 56 mm or with sockets no longer match the default case.** `board_w` and `socket_h` stay parameters, so a socketed build can still be exported.
