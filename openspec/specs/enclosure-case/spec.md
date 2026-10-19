# enclosure-case Specification

## Purpose

Defines the mechanical and RF design requirements for the 3D-printable OpenSCAD (BOSL2) box enclosure housing the connecting PCB, ESP32-S3 SuperMini, and CC1101 SMA module.

## Requirements

### Requirement: Two-Piece M2 Flat-Head Bolt and Hex Nut Assembly
The enclosure SHALL consist of a bottom box base and a top lid designed in OpenSCAD using BOSL2, fastened together and securing the PCB using M2 flat-head (countersunk) bolts and captured M2 hex nuts.

#### Scenario: M2 countersunk bolt and hex nut fastening
- **WHEN** the PCB is placed on the internal standoffs and the lid is closed
- **THEN** M2 flat-head bolts pass flush through `90°` countersunk holes on the outer surface, through the case pillars and PCB M2 mounting holes, and thread into captured M2 hex nut traps (`4.0 mm` flat-to-flat + printer tolerance, at least the nut thickness deep) on the opposite half without spinning

#### Scenario: OpenSCAD compilation and mesh validity
- **WHEN** the `.scad` files are checked and rendered with `openscad-check` and `openscad-render`
- **THEN** they compile with zero errors or warnings and export valid 3D-printable `.3mf` / `.stl` geometry

### Requirement: USB-C and CC1101 SMA Antenna Cutouts
The enclosure SHALL provide accurately aligned cutouts for the ESP32-S3 SuperMini USB-C receptacle and the CC1101 SMA antenna bulkhead connector.

#### Scenario: USB-C cable connection
- **WHEN** a standard USB-C cable is plugged into the assembled enclosure
- **THEN** the USB-C cutout (`9.4 × 3.7 mm` opening with overmold clearance pocket) aligns with the socketed ESP32-S3 SuperMini USB-C port and allows full plug insertion without mechanical interference

#### Scenario: CC1101 SMA antenna bulkhead mounting
- **WHEN** the CC1101 module (`28 × 15 mm`, `6.3 mm` diameter × `8.0 mm` long SMA thread centered `8.4 mm` from the module bottom edge per `CC1101_specs/CC1101-Product-size-600x313.jpg`) is seated in its socket
- **THEN** the SMA threaded barrel protrudes cleanly through a `Ø6.5 mm` hole in the rear case wall so an external 433.92 MHz SMA antenna can be screwed on without hitting the case wall

### Requirement: WiFi Signal Window / Slots
The enclosure SHALL include open slots or a thinned RF window adjacent to the ESP32-S3 SuperMini onboard 2.4 GHz ceramic antenna to preserve WiFi signal strength and provide passive ventilation.

#### Scenario: Unobstructed WiFi antenna radiation
- **WHEN** the ESP32-S3 SuperMini is installed inside the closed enclosure
- **THEN** slotted openings in the case wall/lid sit directly adjacent to the SuperMini's onboard ceramic antenna to reduce dielectric attenuation and allow airflow
