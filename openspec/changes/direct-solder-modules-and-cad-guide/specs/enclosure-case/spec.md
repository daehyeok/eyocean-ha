## ADDED Requirements

### Requirement: Direct-Solder Height Stack-Up
The enclosure SHALL derive every height (module positions, USB-C and SMA openings, case split, roof, overall height) from a single stack-up for modules soldered directly onto the carrier. That stack-up SHALL use a separate header-spacer height for the SuperMini and for the CC1101, and an optional socket height that defaults to zero.

#### Scenario: Default direct-solder heights
- **WHEN** the model is built with the defaults (`pcb_t 1.6`, `socket_h 0`, both header spacers `2.5`)
- **THEN** both module boards sit at `z = 4.1 mm` above the carrier's bottom face, the case splits on the CC1101 SMA axis, and the echoed case size is about `60.5 × 37 × 18.1 mm`

#### Scenario: Per-module spacer override
- **WHEN** a builder measures a different header spacer for one module and sets only that module's spacer parameter
- **THEN** only that module's height and the openings that depend on it (the USB-C hole for the SuperMini; the SMA hole and the case split for the CC1101) move, plus the roof when that module is the tallest part

#### Scenario: Pin tails and SMA clearance are checked
- **WHEN** the configured pin-tail length leaves less than `0.5 mm` under the board, or the SMA barrel would reach the carrier while the board extends past the CC1101 edge
- **THEN** OpenSCAD stops with an assertion naming the problem instead of exporting parts that do not fit

### Requirement: Enclosure Build Guide
The `cad/` directory SHALL contain a `README.md` that lets a builder go from a fresh clone to printed, assembled parts without reading the OpenSCAD source.

#### Scenario: Following the build guide
- **WHEN** a builder opens `cad/README.md`
- **THEN** it lists the prerequisites (OpenSCAD version, `git submodule update --init` for BOSL2), the height stack-up table with each formula, which part dimensions to measure and which parameters they map to, the commands to export STL/3MF (`cad/export.sh` with `-D` overrides), print orientation and slicer settings, the bill of hardware (bolts, nuts, antenna), and step-by-step assembly including pin-tail trimming

## MODIFIED Requirements

### Requirement: Two-Piece M2 Flat-Head Bolt and Hex Nut Assembly
The enclosure SHALL consist of a bottom box base and a top lid designed in OpenSCAD using BOSL2, fastened together and securing the PCB using M2 flat-head (countersunk) bolts and captured M2 hex nuts.

#### Scenario: M2 countersunk bolt and hex nut fastening
- **WHEN** the PCB is placed on the internal standoffs and the lid is closed
- **THEN** M2 × 16 flat-head bolts pass flush through `90°` countersunk holes on the lid top, through the lid pillars, the PCB M2 mounting holes and the base standoffs, and thread into captured M2 hex nut traps (`4.0 mm` flat-to-flat + printer tolerance, at least the nut thickness deep) in the base without spinning, with at least `0.7 mm` of standoff wall around each nut pocket

#### Scenario: OpenSCAD compilation and mesh validity
- **WHEN** the `.scad` files are checked and rendered with `openscad-check` and `openscad-render`
- **THEN** they compile with zero errors or warnings and export valid 3D-printable `.3mf` / `.stl` geometry

### Requirement: USB-C and CC1101 SMA Antenna Cutouts
The enclosure SHALL provide accurately aligned cutouts for the ESP32-S3 SuperMini USB-C receptacle and the CC1101 SMA antenna connector, positioned from the direct-solder stack-up.

#### Scenario: USB-C cable connection
- **WHEN** a standard USB-C cable is plugged into the assembled enclosure
- **THEN** the USB-C cutout (`9.4 × 3.7 mm` opening with overmold clearance pocket) aligns with the soldered ESP32-S3 SuperMini's USB-C port and allows full plug insertion without mechanical interference

#### Scenario: CC1101 SMA antenna bulkhead mounting
- **WHEN** the CC1101 module (`28 × 15 mm`, `6.3 mm` diameter × `8.0 mm` long SMA thread centered `8.4 mm` from the module's south edge per `CC1101_specs/CC1101-Product-size-600x313.jpg`) is soldered onto the carrier
- **THEN** the SMA threaded barrel protrudes cleanly through a `Ø6.5 mm` hole in the east case wall so an external 433.92 MHz SMA antenna can be screwed on without hitting the case wall
