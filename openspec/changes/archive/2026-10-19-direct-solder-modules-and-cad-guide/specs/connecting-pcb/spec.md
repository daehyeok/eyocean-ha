## REMOVED Requirements

### Requirement: ESP32-S3 SuperMini and CC1101 Pin Socket Footprints
**Reason**: The modules are now soldered directly onto the carrier through their male headers; no female sockets are used.
**Migration**: Replaced by "ESP32-S3 SuperMini and CC1101 Direct-Solder Footprints". The pad positions, drill and pin numbering are unchanged, so a socketed build still fits the board, but the enclosure heights assume direct soldering (set `socket_h` in `cad/enclosure.scad` for a socketed build).

## ADDED Requirements

### Requirement: ESP32-S3 SuperMini and CC1101 Direct-Solder Footprints
The PCB SHALL provide 2.54 mm pitch through-hole pads that take the male headers of the ESP32-S3 SuperMini Development Board and of the CC1101 RF transceiver module, so that both modules are soldered directly onto the carrier without female sockets. Each module rests on its header's plastic spacer.

#### Scenario: ESP32-S3 SuperMini direct soldering
- **WHEN** an ESP32-S3 SuperMini board (`22.52 × 18.0 mm`, two 9-pin rows spaced `15.24 mm` apart at `2.54 mm` pitch) with male headers is placed on the carrier PCB
- **THEN** its header pins pass through two `1×09` rows of `1.0 mm` plated holes and solder in place, with the USB-C connector at the PCB's west edge and the header spacer sitting on the carrier top

#### Scenario: CC1101 module direct soldering and pinout compliance
- **WHEN** the CC1101 433.92 MHz SMA module (`28.0 × 15.0 mm`, specs in `CC1101_specs/`) with its male `2×04` header is placed on the carrier PCB
- **THEN** its pins solder into a `2×04` pad group numbered in the module's top view according to `CC1101-Pin-out-1-600x290.jpg` (`1=GND`, `2=VDD`, `3=GDO0`, `4=CSN`, `5=SCK`, `6=MOSI`, `7=MISO/GDO1`, `8=GDO2`)

#### Scenario: SMA barrel clears the carrier
- **WHEN** the CC1101 sits on its header spacer (about `2.5 mm` above the carrier top) and its `Ø6.3 mm` SMA barrel reaches below the module board
- **THEN** the carrier PCB ends at or before the CC1101's east edge (board length `53.5 mm`), so the SMA barrel overhangs the board edge and touches no part of the carrier

## MODIFIED Requirements

### Requirement: Simplified Planar Signal and Power Routing
The PCB SHALL connect the CC1101 module strictly to the 3.3 V power rail (`3V3` → `VDD`, `GND` → `GND`, never 5 V) and map the six SPI/radio signals (`GDO0`, `CSN`, `SCK`, `MOSI`, `MISO`, `GDO2`) to adjacent non-strapping ESP32-S3 SuperMini GPIOs to achieve simple, direct routing.

#### Scenario: 3.3V power supply and decoupling
- **WHEN** the ESP32-S3 SuperMini is powered via USB-C
- **THEN** the carrier PCB supplies regulated `3.3V` (`3V3` pin) and `GND` (copper pour) to CC1101 `VDD` (pin 2) and `GND` (pin 1) through a single local `10 µF` X5R `≥ 10 V` capacitor in a hand-solderable `0603` footprint (e.g. LCSC C19702), relying on the module's own on-board `100 nF`, with zero connection to the `5V` rail

#### Scenario: Clean signal routing with zero DRC/ERC errors
- **WHEN** Electrical Rules Check (ERC) and Design Rules Check (DRC) are executed on the KiCad project via `kicad-cli`
- **THEN** both ERC and DRC pass with zero errors and zero unrouted nets

### Requirement: M2 Case Mounting Holes and Antenna Keepout
The PCB SHALL include M2 mounting holes for fastening into the 3D-printed enclosure and maintain a copper keepout region near the ESP32-S3 SuperMini onboard WiFi antenna.

#### Scenario: M2 mounting holes for enclosure assembly
- **WHEN** the carrier PCB is placed inside the enclosure base
- **THEN** four corner M2 mounting holes (`2.05 mm`–`2.20 mm` drill, `3 mm` from each board edge, `47.5 × 26.0 mm` pattern) align with the enclosure's standoffs and clamp pillars and clear all traces and copper pours

#### Scenario: WiFi antenna copper keepout
- **WHEN** the ESP32-S3 SuperMini is soldered onto the carrier
- **THEN** the PCB region directly beneath the SuperMini's onboard 2.4 GHz ceramic antenna is free of copper pours and traces on both `F.Cu` and `B.Cu`
