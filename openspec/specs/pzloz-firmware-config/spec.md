# pzloz-firmware-config Specification

## Purpose

Defines the ESPHome firmware configuration and documentation requirements to support the Pzloz 433.92 MHz desk lamp and the ESP32-S3 SuperMini connecting PCB pinout.

## Requirements

### Requirement: ESP32-S3 SuperMini Connecting PCB Pinout Configuration
The ESPHome configuration SHALL support the simplified GPIO pin mapping used by the ESP32-S3 SuperMini connecting PCB.

#### Scenario: Configuring SPI and GDO pins for the connecting PCB
- **WHEN** the user builds or flashes the ESPHome configuration for the ESP32-S3 SuperMini connecting PCB
- **THEN** `spi` (`clk_pin`, `mosi_pin`, `miso_pin`), `cc1101` (`cs_pin`), `remote_transmitter` (`pin`), and `remote_receiver` (`pin`) match the physical traces routed on the connecting PCB (`GPIO1`, `GPIO2`, `GPIO4`–`GPIO7`; `GPIO3` stays free)

### Requirement: Pzloz 6-Button Desk Lamp Support and Documentation
The project SHALL provide configuration presets and documentation for pairing and controlling the Pzloz 6-button desk lamp (Power, Brightness, Color Temperature, Reading Mode, Night Light, Timer Function).

#### Scenario: Capturing and configuring a Pzloz remote ID and XOR key
- **WHEN** a user with a Pzloz desk lamp flashes the firmware and presses a button on their Pzloz remote
- **THEN** `remote_receiver` dumps the 32-bit EV1527 frame so the user can set `remote_id` and `xor_key` (and swap `cmd_night_light` / `cmd_timer` if needed) in the ESPHome `substitutions` block to control all 6 lamp functions from Home Assistant
