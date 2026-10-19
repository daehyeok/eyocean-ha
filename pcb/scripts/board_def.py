"""Single source of truth for the eyocean carrier board.

Shared by gen_schematic.py and gen_pcb.py so the schematic, the PCB and the
README pin table never drift apart. Coordinates are board-local millimetres:
origin at the board's north-west corner, +x east (toward the SMA antenna),
+y south (KiCad convention).
"""

import uuid

PROJECT = "eyocean_carrier"
NS = uuid.UUID("6f1c2a52-9a43-4f4e-9d6e-0c1101e5a301")


def uid(name):
  """Deterministic UUID so regenerating does not churn the files."""
  return str(uuid.uuid5(NS, name))


ROOT_UUID = uid("root-sheet")

# --- Board outline -----------------------------------------------------------
BOARD_W = 56.0  # x
BOARD_H = 32.0  # y
CORNER_R = 2.0
HOLE_INSET = 3.0
HOLES = [
    (HOLE_INSET, HOLE_INSET),
    (BOARD_W - HOLE_INSET, HOLE_INSET),
    (HOLE_INSET, BOARD_H - HOLE_INSET),
    (BOARD_W - HOLE_INSET, BOARD_H - HOLE_INSET),
]

# --- ESP32-S3 SuperMini (USB-C faces west, flush with the board's west edge) --
SM_LEN = 22.52  # along x
SM_WID = 18.0  # along y
SM_PIN1_X = 1.4  # first header pin centre from the USB-end board edge
PITCH = 2.54
SM_ROW_N_Y = BOARD_H / 2 - 7.62  # right-hand column (5V, GND, 3V3, GP13..GP8)
SM_ROW_S_Y = BOARD_H / 2 + 7.62  # left-hand column (TX, RX, GP1..GP7)

# CC1101 nets. Mapping chosen so the copper is planar per layer
# (see design.md "Simplified Pin Mapping").
N_GDO0 = "CC_GDO0"
N_CSN = "CC_CSN"
N_SCK = "CC_SCK"
N_MOSI = "CC_MOSI"
N_MISO = "CC_MISO"
N_GDO2 = "CC_GDO2"
N_3V3 = "+3V3"
N_GND = "GND"

# Header pin -> (label, net or None for no-connect)
J1_PINS = {  # south row = SuperMini left-hand column, pin 1 at the USB end
    1: ("TX/GPIO43", None),
    2: ("RX/GPIO44", None),
    3: ("GPIO1", N_GDO2),
    4: ("GPIO2", N_MISO),
    5: ("GPIO3", None),  # strapping pin / VBUS sense on some clones: unused
    6: ("GPIO4", N_MOSI),
    7: ("GPIO5", N_SCK),
    8: ("GPIO6", N_CSN),
    9: ("GPIO7", N_GDO0),
}
J2_PINS = {  # north row = SuperMini right-hand column
    1: ("5V", None),  # never used: CC1101 is 3.3 V only
    2: ("GND", N_GND),
    3: ("3V3", N_3V3),
    4: ("GPIO13", None),
    5: ("GPIO12", None),
    6: ("GPIO11", None),
    7: ("GPIO10", None),
    8: ("GPIO9", None),
    9: ("GPIO8", None),
}

# --- CC1101 module (CC1101_specs/): 28 x 15 mm, 2x04 header at its west end --
CC_LEN = 28.0
CC_WID = 15.0
CC_X = 25.5  # module west edge
CC_Y = 10.75  # module north edge (pin 1 corner)
CC_PIN_OFF = 1.5  # G and F in CC1101-Product-size
CC_SMA_FROM_N = CC_WID - 8.4  # I = 8.4 mm from the south edge
J3_PINS = {  # CC1101-Pin-out-1: odd column west, even column east
    1: ("GND", N_GND),
    2: ("VDD", N_3V3),
    3: ("GDO0", N_GDO0),
    4: ("CSN", N_CSN),
    5: ("SCK", N_SCK),
    6: ("MOSI", N_MOSI),
    7: ("MISO/GDO1", N_MISO),
    8: ("GDO2", N_GDO2),
}


def j1_pad(n):
  return (SM_PIN1_X + PITCH * (n - 1), SM_ROW_S_Y)


def j2_pad(n):
  return (SM_PIN1_X + PITCH * (n - 1), SM_ROW_N_Y)


def j3_pad(n):
  col = (n - 1) % 2
  row = (n - 1) // 2
  return (CC_X + CC_PIN_OFF + PITCH * col, CC_Y + CC_PIN_OFF + PITCH * row)


# Decoupling capacitors (pad-1 = +3V3 on the vertical 3V3 trace), just east
# of the CC1101 socket courtyard.
CAP_RAIL_X = 32.4
C1_PAD1 = (CAP_RAIL_X, 11.0)  # 100 nF 0603
C2_PAD1 = (CAP_RAIL_X, 8.8)  # 10 uF 0603 (6.3 V+ X5R)

# WiFi antenna keep-out under the SuperMini's far (east) end.
ANT_KEEPOUT = (17.0, 9.8, 23.2, 22.2)  # x0, y0, x1, y1

FOOTPRINTS = {
    "J1": "Connector_PinSocket_2.54mm:PinSocket_1x09_P2.54mm_Vertical",
    "J2": "Connector_PinSocket_2.54mm:PinSocket_1x09_P2.54mm_Vertical",
    "J3": "eyocean:CC1101_Socket_2x04_P2.54mm_TopView",
    "C1": "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder",
    "C2": "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder",
    "H1": "MountingHole:MountingHole_2.2mm_M2",
    "H2": "MountingHole:MountingHole_2.2mm_M2",
    "H3": "MountingHole:MountingHole_2.2mm_M2",
    "H4": "MountingHole:MountingHole_2.2mm_M2",
}
VALUES = {
    "J1": "SuperMini_L (TX..GPIO7)",
    "J2": "SuperMini_R (5V..GPIO8)",
    "J3": "CC1101_433MHz",
    "C1": "100nF",
    "C2": "10uF",
    "H1": "M2",
    "H2": "M2",
    "H3": "M2",
    "H4": "M2",
}
DESCR = {
    "J1": "ESP32-S3 SuperMini left column (TX, RX, GPIO1-7)",
    "J2": "ESP32-S3 SuperMini right column (5V, GND, 3V3, GPIO13-8)",
    "J3": "CC1101 433 MHz SMA module (CC1101_specs/), 3.3 V only",
    "C1": "CC1101 VDD decoupling",
    "C2": "CC1101 VDD decoupling",
    "H1": "M2 case mounting hole",
    "H2": "M2 case mounting hole",
    "H3": "M2 case mounting hole",
    "H4": "M2 case mounting hole",
}
