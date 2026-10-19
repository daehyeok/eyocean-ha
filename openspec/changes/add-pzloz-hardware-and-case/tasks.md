## 1. Connecting Carrier PCB (KiCad)

- [x] 1.1 Create KiCad project (`pcb/eyocean_carrier.kicad_pro`, `pcb/eyocean_carrier.kicad_sch`) with two `1×09` (`2.54 mm` pitch) pin sockets for the ESP32-S3 SuperMini, one `2×04` (`2.54 mm` pitch) pin socket for the CC1101 module matching `CC1101_specs/CC1101-Pin-out-1-600x290.jpg`, `100 nF` + `10 µF` (`0603`/`0805`) 3.3 V decoupling capacitors, and 4× M2 mounting hole symbols, and verify schematic ERC passes via `~/.bin/kicad.AppImage kicad-cli sch erc` with zero errors.
- [x] 1.2 Create the 2-layer PCB layout (`pcb/eyocean_carrier.kicad_pcb`) with a `56.0 × 32.0 mm` rounded board outline, 4× M2 corner mounting holes (`50.0 × 26.0 mm` spacing, `2.2 mm` drill), inline placement of the ESP32-S3 SuperMini (`15.24 mm` row spacing, USB-C at west edge) and CC1101 (`2×04` top-view socket on east side, SMA overhanging the east edge), WiFi antenna copper keepout zone under the SuperMini antenna end, and planar traces + `GND` pours for `3V3`, `GND`, and `GPIO1`/`2`/`4`/`5`/`6`/`7`, and verify PCB DRC passes via `~/.bin/kicad.AppImage kicad-cli pcb drc` with zero errors and zero unconnected nets.
- [x] 1.3 Export fabrication Gerbers/drill files and board SVG/3D preview under `pcb/` and verify all Gerber and drill files are generated cleanly.

## 2. ESPHome Firmware & Pzloz Lamp Configuration

- [x] 2.1 Update `esphome/eyocean-rf.yaml` (and/or add a Pzloz / SuperMini PCB preset) with the simplified carrier PCB pinout (`pin_tx: GPIO7`, `pin_cs: GPIO6`, `pin_sck: GPIO5`, `pin_mosi: GPIO4`, `pin_miso: GPIO2`, `pin_rx: GPIO1` for `esp32-s3-devkitc-1`) and verify the YAML configuration syntax and substitutions are valid.
- [x] 2.2 Update `README.md` with the ESP32-S3 SuperMini connecting PCB pinout table, Pzloz 6-button remote configuration instructions, and enclosure assembly overview, and verify all markdown tables and links render accurately.

## 3. OpenSCAD (BOSL2) Box Enclosure

- [x] 3.1 Create the parametric BOSL2 enclosure (`cad/enclosure.scad`) with bottom case and top lid modules, 4× M2 corner pillars matching the `50.0 × 26.0 mm` PCB hole pattern, lid-top `90°` countersinks for M2 flat-head bolts, and captured M2 hex nut traps (`4.1 mm` across flats) under the base, and verify syntax with `.agents/skills/openscad-bosl2/tools/openscad-check cad/enclosure.scad`.
- [x] 3.2 Add the stepped USB-C port cutout on the west wall, the `Ø6.5 mm` CC1101 SMA bulkhead hole on the east wall (aligned with `I = 8.4 mm` from the CC1101 spec), and the WiFi RF signal/ventilation slots adjacent to the ESP32-S3 SuperMini ceramic antenna, and verify compilation and visual geometry by running `openscad-check` and `openscad-render` to produce `cad/enclosure.png` and `.3mf` exports with zero warnings or errors.
