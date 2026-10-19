## Purpose

Defines the electrical and mechanical requirements for the KiCad 2-layer connecting carrier PCB that mates an ESP32-S3 SuperMini Development Board with a CC1101 433.92 MHz SMA RF transceiver module.

## ADDED Requirements

### Requirement: ESP32-S3 SuperMini and CC1101 Pin Socket Footprints
The PCB SHALL provide through-hole 2.54 mm pitch pin sockets for plugging in both the ESP32-S3 SuperMini Development Board and the CC1101 RF transceiver module.

#### Scenario: ESP32-S3 SuperMini socket mating
- **WHEN** an ESP32-S3 SuperMini board (`23.5 × 18.0 mm`, two 9-pin rows spaced `15.24 mm` apart at `2.54 mm` pitch) is inserted into the carrier PCB
- **THEN** the board seats into two vertical `1×09` (`2.54 mm` pitch) female pin sockets oriented with the USB-C connector facing the PCB's west/front edge

#### Scenario: CC1101 module socket mating and pinout compliance
- **WHEN** the CC1101 433.92 MHz SMA module (`28.0 × 15.0 mm`, specs in `CC1101_specs/`) is inserted into the carrier PCB
- **THEN** its `2×04` (`2.54 mm` pitch) header mates with a vertical `2×04` female pin socket wired according to `CC1101-Pin-out-1-600x290.jpg` (`1=GND`, `2=VDD`, `3=GDO0`, `4=CSN`, `5=SCK`, `6=MOSI`, `7=MISO/GDO1`, `8=GDO2`) with the SMA connector extending beyond the PCB's east/rear edge

### Requirement: Simplified Planar Signal and Power Routing
The PCB SHALL connect the CC1101 module strictly to the 3.3 V power rail (`3V3` → `VDD`, `GND` → `GND`, never 5 V) and map the six SPI/radio signals (`GDO0`, `CSN`, `SCK`, `MOSI`, `MISO`, `GDO2`) to adjacent non-strapping ESP32-S3 SuperMini GPIOs to achieve simple, direct routing.

#### Scenario: 3.3V power supply and decoupling
- **WHEN** the ESP32-S3 SuperMini is powered via USB-C
- **THEN** the carrier PCB supplies regulated `3.3V` (`3V3` pin) and `GND` (copper pour) to CC1101 `VDD` (pin 2) and `GND` (pin 1) with local decoupling capacitance (`100 nF` and `10 µF` in hand-solderable `0603`/`0805` SMD footprints) and zero connection to the `5V` rail

#### Scenario: Clean signal routing with zero DRC/ERC errors
- **WHEN** Electrical Rules Check (ERC) and Design Rules Check (DRC) are executed on the KiCad project via `kicad-cli`
- **THEN** both ERC and DRC pass with zero errors and zero unrouted nets

### Requirement: M2 Case Mounting Holes and Antenna Keepout
The PCB SHALL include M2 mounting holes for fastening into the 3D-printed enclosure and maintain a copper keepout region near the ESP32-S3 SuperMini onboard WiFi antenna.

#### Scenario: M2 mounting holes for enclosure assembly
- **WHEN** the carrier PCB is placed inside the enclosure base
- **THEN** four corner M2 mounting holes (`2.05 mm`–`2.20 mm` drill) align with the enclosure's internal mounting bosses and clear all traces and copper pours

#### Scenario: WiFi antenna copper keepout
- **WHEN** the ESP32-S3 SuperMini is seated in its socket
- **THEN** the PCB region directly beneath the SuperMini's onboard 2.4 GHz ceramic antenna is free of copper pours and traces on both `F.Cu` and `B.Cu`
