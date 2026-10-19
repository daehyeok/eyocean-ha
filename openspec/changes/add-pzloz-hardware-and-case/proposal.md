## Why

Currently, the `eyocean-ha` project documents breadboard/Dupont-wire setups for controlling 433.92 MHz EV1527-based desk lamps (such as EYOCEAN and compatible Pzloz 6-button desk lamps) and lacks a dedicated hardware carrier or enclosure. A custom connecting PCB and 3D-printed OpenSCAD box enclosure are needed to cleanly mount an ESP32-S3 SuperMini (2×9 pin header, USB-C + onboard ceramic WiFi antenna) and the CC1101 433.92 MHz SMA RF transceiver module (2×4 pin socket, specs in `CC1101_specs/`) into a compact, durable unit for controlling the Pzloz desk lamp.

## What Changes

- Add a KiCad connecting carrier PCB project (`pcb/`) featuring:
  - Pin sockets for the **ESP32-S3 SuperMini Development Board** (dual 1×9 2.54 mm female headers, 15.24 mm row spacing) and the **CC1101 433 MHz SMA module** (2×4 2.54 mm female header matching `CC1101_specs/`).
  - Clean, planar routing between the ESP32-S3 SuperMini and CC1101 (`3V3` → `VDD`, `GND` → `GND`, and adjacent safe GPIOs mapped to `GDO0`, `CSN`, `SCK`, `MOSI`, `MISO`, `GDO2` for minimal trace crossings).
  - M2 mounting holes (`2.05 mm` plated/unplated drill) positioned to secure the PCB inside the 3D-printed enclosure and support the CC1101 module.
- Update ESPHome firmware configuration (`esphome/`) to support the Pzloz desk lamp profile and the new PCB's simplified ESP32-S3 SuperMini GPIO pin assignment.
- Add a parametric OpenSCAD (BOSL2) two-piece box enclosure (`cad/`) featuring:
  - Fastening via **M2 flat-head (countersunk) bolts** from the exterior and captured **M2 hex nuts** in internal hex traps.
  - A stepped **USB-C port cutout** aligned with the socketed ESP32-S3 SuperMini USB-C receptacle.
  - A **CC1101 SMA antenna bulkhead hole** (`Ø6.5 mm` clearance for the `6.3 mm` SMA thread) on the opposite wall.
  - **WiFi RF window / ventilation slots** adjacent to the ESP32-S3 SuperMini onboard 2.4 GHz ceramic antenna to minimize enclosure attenuation and heat buildup.

## Capabilities

### New Capabilities
- `connecting-pcb`: KiCad schematic and 2-layer PCB layout connecting the ESP32-S3 SuperMini (2×9 pin sockets) and CC1101 RF module (2×4 pin socket) with simplified pin routing and M2 case mounting holes.
- `enclosure-case`: Parametric OpenSCAD (BOSL2) two-piece box case secured with M2 flat-head bolts and M2 hex nuts, providing a USB-C opening, CC1101 SMA antenna bulkhead hole, and WiFi signal slots around the ESP32-S3 ceramic antenna.
- `pzloz-firmware-config`: ESPHome configuration and documentation supporting the Pzloz desk lamp and the carrier PCB's direct GPIO routing for the ESP32-S3 SuperMini.

### Modified Capabilities

## Impact

- **New directories/files**:
  - `pcb/`: KiCad 10 project (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`) and Gerber/production export helpers.
  - `cad/`: OpenSCAD BOSL2 source files (`case.scad` / parameters) and rendered `.png` / `.3mf` outputs.
  - `esphome/`: Updated or added Pzloz / SuperMini PCB configuration (`pzloz-rf.yaml` or updated `eyocean-rf.yaml`) and `README.md` wiring table updates.
