# eyocean-ha

ESPHome-based Home Assistant integration for the **EYOCEAN LED Desk Lamp** (ASIN: B0BNDLND3Y) via 433.92 MHz RF control.

The EYOCEAN desk lamp uses a 433.92 MHz ASK/OOK remote with an **EV1527-based** protocol (32-bit fixed codes — extended from standard 24-bit EV1527, no rolling code). This project replaces the physical remote with an ESP32 + CC1101 transceiver, giving full Home Assistant control.

## Hardware

| Component                          | Purpose         |
| ---------------------------------- | --------------- |
| ESP32-S3 DevKit                    | Microcontroller |
| CC1101 433MHz module (SMA antenna) | RF transceiver  |
| Dupont wires                       | Wiring          |
| USB-C cable + power adapter        | Power           |

An ESP32-S3 SuperMini can instead sit on the [carrier board](#carrier-board--enclosure-esp32-s3-supermini),
which replaces the Dupont wires and fits a 3D-printed case.

### Wiring (ESP32-S3)

```
ESP32-S3          CC1101
─────────         ──────
GPIO9  (CLK)  →   SCK
GPIO10 (MOSI) →   MOSI
GPIO11 (MISO) →   MISO
GPIO12 (CS)   →   CSN
GPIO13 (TX)   →   GDO0
GPIO14 (RX)   →   GDO2
3.3V          →   VCC
GND           →   GND
```

### Wiring (ESP32-C3 SuperMini)

```
ESP32-C3          CC1101
─────────         ──────
GPIO4  (SCK)  →   SCK
GPIO10 (MOSI) →   MOSI
GPIO3  (MISO) →   MISO
GPIO7  (CS)   →   CSN
GPIO1  (TX)   →   GDO0
GPIO2  (RX)   →   GDO2
3.3V          →   VCC
GND           →   GND
```

> [!CAUTION]
> CC1101 runs on 3.3V only. Do NOT connect to 5V.

### Carrier board + enclosure (ESP32-S3 SuperMini)

Instead of Dupont wires you can plug both modules into a small carrier PCB
(`pcb/`) and close it in a 3D-printed box (`cad/`):

| Part                                                 | Qty | Notes                                       |
| ---------------------------------------------------- | --- | ------------------------------------------- |
| Carrier PCB, 56 × 32 mm, 2 layers, 1.6 mm            | 1   | `pcb/production/eyocean_carrier_jlcpcb.zip` |
| ESP32-S3 SuperMini                                   | 1   | solder its male headers pointing down        |
| CC1101 433 MHz module with SMA (see `CC1101_specs/`) | 1   | male 2×4 header pointing down                |
| 1×9 female header, 2.54 mm, 8.5 mm tall              | 2   | SuperMini sockets                            |
| 2×4 female header, 2.54 mm, 8.5 mm tall              | 1   | CC1101 socket                                |
| 100 nF 0603 + 10 µF 0805 capacitor                   | 1+1 | CC1101 VDD decoupling                        |
| M2 × 25 flat-head (countersunk) bolt                 | 4   | M2 × 20 also works (head sinks into a counterbore) |
| M2 hex nut                                           | 4   | captured under the base                      |
| 433 MHz SMA antenna                                  | 1   | screws on outside the case                   |

The carrier routes the CC1101 to the SuperMini's **left** header column
(TX, RX, GPIO1–7). 3V3 and GND come from the right column; 5V is never
connected. GPIO3 is left free because it is a strapping / VBUS-sense pin on
some SuperMini clones.

| CC1101 pin | Signal    | SuperMini pin | ESPHome substitution |
| ---------- | --------- | ------------- | -------------------- |
| 1          | GND       | GND           | –                    |
| 2          | VDD       | 3V3           | –                    |
| 3          | GDO0      | GPIO7         | `pin_tx`             |
| 4          | CSN       | GPIO6         | `pin_cs`             |
| 5          | SCK       | GPIO5         | `pin_sck`            |
| 6          | MOSI      | GPIO4         | `pin_mosi`           |
| 7          | MISO/GDO1 | GPIO2         | `pin_miso`           |
| 8          | GDO2      | GPIO1         | `pin_rx`             |

`esphome/pzloz-carrier.yaml` already uses these pins. It includes
`eyocean-rf.yaml` and only overrides the name, the pins and your remote
codes, so it works for EYOCEAN lamps too.

**PCB.** The KiCad 10 project is generated from `pcb/scripts/board_def.py`
(one table for pins, placement and nets). `pcb/scripts/build.sh`
regenerates the schematic and the board, runs ERC and DRC (with schematic
parity) and exports Gerbers, drill files, SVGs, a 3D render and a STEP model
to `pcb/production/`. The board keeps copper out from under the SuperMini's
chip antenna (the far end, opposite the USB-C port).

**Enclosure.** `cad/enclosure.scad` (OpenSCAD + BOSL2; BOSL2 is a git
submodule, so clone with `--recursive` or run
`git submodule update --init`). It is a base and a lid that split on the
SMA axis, 61 × 37 × 26.6 mm:

- USB-C opening in the west wall, with a recess for the plug overmold.
- Ø6.5 mm SMA hole in the east wall. The base half is a U-slot, so the
  socketed CC1101 drops in with its SMA thread already through the wall.
- WiFi slots in the lid roof and side walls over the SuperMini's antenna
  end.
- Four M2 flat-head bolts go in from the lid top, through the lid pillars,
  the board's corner holes and the base standoffs, into M2 hex nuts in
  hex pockets under the base. The same bolts clamp the board.

Every dimension that depends on your parts (socket height, header spacer,
SMA body length, bolt length) is a Customizer parameter. Measure your
modules and adjust before printing.

```bash
git submodule update --init
openscad -D 'part="bottom"' -o enclosure_bottom.3mf cad/enclosure.scad
openscad -D 'part="lid"'    -o enclosure_lid.3mf    cad/enclosure.scad
```

Print in PETG (or PLA for indoor use) at 0.2 mm layers with 3 walls, 20 %
infill and no supports. The base prints floor-down and the lid prints
roof-down.

Assembly:

1. Solder the sockets and the two capacitors to the carrier.
2. Plug in the SuperMini (USB-C at the board edge) and the CC1101 (SMA
   pointing away from the SuperMini).
3. Put the board on the base standoffs. The SMA thread drops into the
   U-slot.
4. Put on the lid. Push an M2 nut into each hex pocket under the base, then
   tighten the four bolts from the top.
5. Screw the 433 MHz antenna onto the SMA.

## Protocol Details

| Parameter       | Value                                                     |
| --------------- | --------------------------------------------------------- |
| Frequency       | 433.92 MHz                                                |
| Modulation      | ASK/OOK                                                   |
| Protocol        | EV1527-based (32-bit)                                     |
| Frame structure | 16-bit fixed prefix + 8-bit button code + 8-bit XOR check |
| Security        | Fixed code (no rolling)                                   |
| FCC ID          | 2BD2C-ZZ02DY01007                                         |

### Decoded Remote Codes

The EYOCEAN remote uses a **32-bit** frame (not standard 24-bit EV1527). All 32 bits are required — the lamp ignores truncated 24-bit frames.

**Frame structure:**

| Byte | Content       | Varies per remote?              |
| ---- | ------------- | ------------------------------- |
| 0-1  | Remote ID     | **yes** — per-remote address    |
| 2    | Function code | no — same across remotes        |
| 3    | Checksum      | `byte2 XOR key`, key per-remote |

```
code = (remote_id << 16) | (cmd << 8) | (cmd ^ xor_key)
```

The **function codes are shared across units** — only the 16-bit remote ID and the 8-bit XOR key are per-remote. This reproduces all 11 known codes from the two fully-decoded remotes below.

| Button            | Function code   |
| ----------------- | --------------- |
| Power On/Off      | `0x51`          |
| Brightness        | `0x5B`          |
| Color Temperature | `0x5A`          |
| Reading Mode      | `0x49`          |
| Night Light       | `0x41` / `0x4D` |
| Timer Function    | `0x4D` / `0x41` |

`0x41` and `0x4D` swap meaning between models: 5-button remotes (no timer) use `0x41` for night light, and the two 6-button remotes reported so far disagree with each other — see [#3](https://github.com/bl4ko/eyocean-ha/issues/3). If those two buttons act swapped on your lamp, exchange `cmd_night_light` / `cmd_timer` in the config.

**Known remotes:**

| Lamp                                | Remote ID | XOR key | Source                                                    |
| ----------------------------------- | --------- | ------- | --------------------------------------------------------- |
| EYOCEAN (ASIN B0BNDLND3Y), 5 buttons | `0xBAD1`  | `0x4E`  | this repo                                                  |
| EYOCEAN CLED-2600C (ASIN B09ZHYNYB9), 6 buttons | `0xDCCF` | `0x76` | [#3](https://github.com/bl4ko/eyocean-ha/issues/3) |
| Pzloz, 6 buttons                    | ?         | ?       | [#1](https://github.com/bl4ko/eyocean-ha/issues/1) (partial) |

The XOR key is not derivable from the remote ID with the data available (`0xBAD1`→`0x4E`, `0xDCCF`→`0x76`); treat it as an independent per-remote value.

> [!IMPORTANT]
> **You still need to capture one button from your own remote** to learn its ID and XOR key — but only one. Capture any button, then read the ID off bytes 0-1 and compute the key as `byte2 XOR byte3`; the other buttons follow from the formula. See [Capturing Your Own Codes](#capturing-your-own-codes). Standard 24-bit EV1527 decoders (Flipper Zero, rtl_433) only show the first 24 bits — you must capture raw data and decode all 32 bits.

## Installation

### 1. Configure

Everything unit-specific lives in the `substitutions:` block at the top of `esphome/eyocean-rf.yaml`:

```yaml
substitutions:
  board: esp32-s3-devkitc-1
  pin_sck: GPIO9
  pin_mosi: GPIO10
  pin_miso: GPIO11
  pin_cs: GPIO12
  pin_tx: GPIO13
  pin_rx: GPIO14

  remote_id: "0xBAD1"
  xor_key: "0x4E"
  cmd_night_light: "0x41"
  cmd_timer: "0x4D"
```

For an ESP32-C3 SuperMini, swap in:

```yaml
  board: esp32-c3-devkitm-1
  pin_sck: GPIO4
  pin_mosi: GPIO10
  pin_miso: GPIO3
  pin_cs: GPIO7
  pin_tx: GPIO1
  pin_rx: GPIO2
```

Set `remote_id` and `xor_key` from your own capture — see [Capturing Your Own Codes](#capturing-your-own-codes).

### Pzloz desk lamp (6 buttons)

Pzloz lamps use the same 32-bit protocol and function codes. Flash
`esphome/pzloz-carrier.yaml` (carrier board) or `eyocean-rf.yaml` (your own
wiring), then:

1. Press any button on the Pzloz remote and read the 32-bit frame that
   `remote_receiver` logs.
2. Set `remote_id` (bytes 0–1) and `xor_key` (byte 2 XOR byte 3) in the
   `substitutions:` block, then flash again.
3. All six buttons appear in Home Assistant: Power, Brightness, Color
   Temperature, Reading Mode, Night Light and Timer Function. If Night Light
   and Timer act swapped, exchange `cmd_night_light` and `cmd_timer`.

Please report your Pzloz remote ID and XOR key in
[#1](https://github.com/bl4ko/eyocean-ha/issues/1) so the table above can
be filled in.

### 2. Flash ESPHome

```bash
pip install esphome
esphome run esphome/eyocean-rf.yaml
```

### 3. Add to Home Assistant

The device auto-discovers via ESPHome integration. Go to **Settings → Devices & Services → ESPHome** and adopt the device.

### 4. Place Near Lamp

The ESP32+CC1101 needs RF line-of-sight to the lamp's receiver. Place within ~5m for reliable operation.

## State Management

The lamp is **receive-only** — it has no back-channel to report its state.

## Capturing Your Own Codes

You only need **one** button — the rest follow from the formula. The protocol uses **32-bit frames**; standard EV1527 decoders only show 24 bits, so you must capture raw data.

1. **Option A — Flipper Zero**: Sub-GHz → Read → press the button → save the `.sub`
2. **Option B — ESP32+CC1101**: this config already includes `remote_receiver` with `dump: all` — flash it, press the button, read the logs
3. **Option C — RTL-SDR**: `rtl_433` in raw mode

Take the 32-bit frame and split it:

```
0xDCCF5127
  ├─ 0xDCCF  → remote_id
  ├─ 0x51    → function code (Power, confirms you decoded it right)
  └─ 0x27    → xor_key = 0x51 XOR 0x27 = 0x76
```

Put `remote_id` and `xor_key` in the `substitutions:` block. If the function code doesn't match the [table above](#decoded-remote-codes), your remote is a new variant — please open an issue.

## How It Works

```
┌───────────────┐    433.92 MHz    ┌───────────────┐
│ ESP32+CC1101  │ ──── RF ────→    │ EYOCEAN Lamp  │
│  (ESPHome)    │                  │  (receiver)   │
└──────┬────────┘                  └───────────────┘
       │ WiFi
       ▼
┌────────────────┐
│ Home Assistant │
│  (dashboard)   │
└────────────────┘
```

The ESP32 connects to your WiFi and exposes entities to Home Assistant. When you toggle a switch in HA, ESPHome transmits the corresponding EV1527 code via the CC1101 at 433.92 MHz — exactly as the original remote would.

## Contributing

Got a working setup on your EYOCEAN (or compatible, e.g. Pzloz) lamp? Open a PR or issue with your remote ID, XOR key, model number and button count — more data points help map the protocol across units and brands, and may yet reveal how the XOR key is derived.

## License

MIT
