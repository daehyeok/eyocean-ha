## 1. Review in-progress edits

- [x] 1.1 Diff-review the uncommitted `cad/enclosure.scad` and `pcb/scripts/board_def.py` edits against design.md Decisions 1–4. Fix anything missing or inconsistent; there must be no leftover `module_z` or `pin_spacer_h`. Verify with `git diff` and `openscad-check cad/enclosure.scad` reporting zero errors.

## 2. Carrier PCB

- [x] 2.1 Confirm `BOARD_W = 53.5` (holes at a `47.5 × 26.0 mm` pattern) and rerun `pcb/scripts/build.sh` from scratch. Verify ERC 0, DRC 0 violations, 0 unconnected, 0 parity issues, and that `pcb/production/eyocean_carrier_jlcpcb.zip` is regenerated with 12 files.
- [x] 2.2 Visually check the board render (`pcb/production/eyocean_carrier_3d_top.png`, top SVG): the east edge sits at the CC1101 edge, and no silkscreen runs off the board. Verify the DRC report shows no silk/edge warnings.

## 3. Enclosure model

- [x] 3.1 Verify the stack-up echoes for the defaults: module bottoms `z = 4.1`, split `4.7`, USB-C centre 12.23 mm above the base bottom, case `60.5 × 37 × 18.1 mm`, `M2x16` head 0 mm below the top. Use `openscad -o x.echo cad/enclosure.scad`.
- [x] 3.2 Exercise the guards with `-D` overrides; each must stop with its assertion:
  - `board_w=56` (SMA hits the carrier)
  - `pin_tail=3.5` (no room for the tails)
  - `standoff_d=5.5` (nut wall too thin)
  - `bolt_len=20` (bolt too long)

  Then confirm `bolt_len=12` and `14` build with a counterbore, and `cc_spacer_h=3.0` moves only the SMA and split.
- [x] 3.3 Regenerate `cad/export/enclosure_{bottom,lid}.{stl,3mf}` with `cad/export.sh` and `cad/enclosure.png` with `openscad-render`. Verify both parts report `Simple: yes` and sit at `z = 0`, and check the render visually (modules low in the base, SMA in the U-slot).
- [x] 3.4 Correct the CC1101 header position (design.md Decision 5): the header rows are centred on the module's 15 mm edge. Set `CC_Y = 8.56` around the unchanged pads in `board_def.py` and `cc_y = 8.56` in `enclosure.scad`. Verify the pad coordinates are unchanged, the row centre equals the module centre, DRC/parity is still clean, and the SMA hole and U-slot moved to board y 15.16 in the regenerated parts and render.

## 4. Documentation

- [x] 4.1 Write `cad/README.md` per design.md Decision 6: overview with render, prerequisites, stack-up table with formulas, measure-your-parts mapping to parameters, build/export commands, print settings, hardware list, assembly with pin-tail trimming, troubleshooting. Verify every command in it runs as written (`cad/export.sh`, `openscad -D ...`), and every parameter name and default matches `enclosure.scad`.
- [x] 4.2 Update the top-level `README.md`:
  - Parts list: no female headers; male headers soldered direct; 4× M2 × 16 bolts.
  - Board 53.5 × 32 mm; case 60.5 × 37 × 18.1 mm.
  - Assembly steps; point to `cad/README.md` for the case build.

  Verify the links and the anchor to `cad/README.md` resolve.

## 5. Wrap-up

- [x] 5.1 Run `openspec validate direct-solder-modules-and-cad-guide --type change`, and check `git status` shows only intended files (no scratch outputs in the repo).
