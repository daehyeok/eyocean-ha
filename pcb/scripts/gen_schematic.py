#!/usr/bin/env python3
"""Generate pcb/eyocean_carrier.kicad_sch from board_def.py.

Usage: gen_schematic.py <kicad-symbol-dir>
  e.g. /tmp/.mount_kicadXXXX/usr/share/kicad/symbols  (KiCad 10 *.kicad_symdir)

Plain Python 3, no KiCad modules needed. Every connection is made by putting
a net label, power symbol or no-connect flag exactly on a pin end point.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_def as B  # pylint: disable=g-import-not-at-top

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", B.PROJECT + ".kicad_sch")


# --- tiny s-expression helpers ----------------------------------------------
def tokenize(text):
  return re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', text)


def parse(tokens):
  stack = [[]]
  for t in tokens:
    if t == "(":
      stack.append([])
    elif t == ")":
      node = stack.pop()
      stack[-1].append(node)
    else:
      stack[-1].append(t[1:-1] if t.startswith('"') else t)
  return stack[0]


def find_block(text, head):
  """Return the raw text of the first balanced block starting with head."""
  start = text.index(head)
  depth = 0
  i = start
  in_str = False
  while i < len(text):
    c = text[i]
    if in_str:
      if c == "\\":
        i += 1
      elif c == '"':
        in_str = False
    elif c == '"':
      in_str = True
    elif c == "(":
      depth += 1
    elif c == ")":
      depth -= 1
      if depth == 0:
        return text[start:i + 1]
    i += 1
  raise ValueError(head)


def walk(node):
  if isinstance(node, list):
    yield node
    for ch in node:
      yield from walk(ch)


class LibSymbol:
  """A library symbol: raw text for lib_symbols plus its pin end points."""

  def __init__(self, symdir, lib, name):
    path = os.path.join(symdir, lib + ".kicad_symdir", name + ".kicad_sym")
    with open(path) as f:
      text = f.read()
    raw = find_block(text, '(symbol "%s"' % name)
    self.lib_id = "%s:%s" % (lib, name)
    self.raw = raw.replace('(symbol "%s"' % name,
                           '(symbol "%s"' % self.lib_id, 1)
    self.pins = {}
    for n in walk(parse(tokenize(raw))):
      if n and n[0] == "pin":
        at = next(c for c in n if isinstance(c, list) and c[0] == "at")
        num = next(c for c in n if isinstance(c, list) and c[0] == "number")
        self.pins[num[1]] = (float(at[1]), float(at[2]))


# --- schematic emitters -------------------------------------------------------
def fmt(v):
  s = ("%.4f" % v).rstrip("0").rstrip(".")
  return "0" if s == "-0" else s


def prop(key, val, x, y, hide=False, size=1.27, justify=None):
  just = "\n\t\t\t\t(justify %s)" % justify if justify else ""
  return ("\t\t(property \"%s\" \"%s\"\n\t\t\t(at %s %s 0)\n%s"
          "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
          "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size %s %s)\n\t\t\t\t)%s\n"
          "\t\t\t)\n\t\t)\n") % (key, val, fmt(x), fmt(y),
                                 "\t\t\t(hide yes)\n" if hide else "",
                                 size, size, just)


def symbol(lib, ref, value, x, y, footprint="", descr="", in_bom=True,
           on_board=True, hide_ref=False, hide_val=False):
  out = ["\t(symbol\n\t\t(lib_id \"%s\")\n\t\t(at %s %s 0)\n\t\t(unit 1)\n"
         "\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom %s)\n"
         "\t\t(on_board %s)\n\t\t(in_pos_files %s)\n\t\t(dnp no)\n"
         "\t\t(uuid \"%s\")\n" % (lib.lib_id, fmt(x), fmt(y),
                                  "yes" if in_bom else "no",
                                  "yes" if on_board else "no",
                                  "yes" if in_bom else "no", B.uid(ref))]
  out.append(prop("Reference", ref, x + 2.54, y - 2.54, hide=hide_ref,
                  justify="left"))
  out.append(prop("Value", value, x + 2.54, y + 2.54, hide=hide_val,
                  justify="left"))
  out.append(prop("Footprint", footprint, x, y, hide=True))
  out.append(prop("Datasheet", "", x, y, hide=True))
  out.append(prop("Description", descr, x, y, hide=True))
  for num in sorted(lib.pins, key=lambda s: (len(s), s)):
    out.append("\t\t(pin \"%s\"\n\t\t\t(uuid \"%s\")\n\t\t)\n" %
               (num, B.uid(ref + "-pin-" + num)))
  out.append("\t\t(instances\n\t\t\t(project \"%s\"\n\t\t\t\t(path \"/%s\"\n"
             "\t\t\t\t\t(reference \"%s\")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n"
             "\t\t\t)\n\t\t)\n\t)\n" % (B.PROJECT, B.ROOT_UUID, ref))
  return "".join(out)


def pin_xy(lib, x, y, num):
  px, py = lib.pins[str(num)]
  return x + px, y - py  # library y is up, schematic y is down


def label(net, x, y, left_side, key):
  angle = 180 if left_side else 0
  just = "right bottom" if left_side else "left bottom"
  return ("\t(label \"%s\"\n\t\t(at %s %s %d)\n\t\t(effects\n\t\t\t(font\n"
          "\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n"
          "\t\t(uuid \"%s\")\n\t)\n") % (net, fmt(x), fmt(y), angle, just,
                                         B.uid("label-" + key))


def no_connect(x, y, key):
  return "\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid \"%s\")\n\t)\n" % (
      fmt(x), fmt(y), B.uid("nc-" + key))


def text(s, x, y, key, size=1.27):
  return ("\t(text \"%s\"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n"
          "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t)\n"
          "\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid \"%s\")\n\t)\n") % (
              s, fmt(x), fmt(y), size, size, B.uid("text-" + key))


def main():
  symdir = sys.argv[1]
  conn9 = LibSymbol(symdir, "Connector_Generic", "Conn_01x09")
  conn24 = LibSymbol(symdir, "Connector_Generic", "Conn_02x04_Odd_Even")
  cap = LibSymbol(symdir, "Device", "C")
  hole = LibSymbol(symdir, "Mechanical", "MountingHole")
  gnd = LibSymbol(symdir, "power", "GND")
  v33 = LibSymbol(symdir, "power", "+3V3")
  flag = LibSymbol(symdir, "power", "PWR_FLAG")
  libs = [conn9, conn24, cap, hole, gnd, v33, flag]

  body = []
  pwr_n = [0]

  def power(lib, x, y):
    pwr_n[0] += 1
    ref = "#PWR%02d" % pwr_n[0]
    body.append(symbol(lib, ref, lib.lib_id.split(":")[1], x, y,
                       in_bom=False, on_board=False, hide_ref=True))

  def flag_at(x, y, n):
    body.append(symbol(flag, "#FLG%02d" % n, "PWR_FLAG", x, y, in_bom=False,
                       on_board=False, hide_ref=True))

  def wire_pins(ref, lib, x, y, pins):
    for num, (name, net) in pins.items():
      px, py = pin_xy(lib, x, y, num)
      left = px < x
      key = "%s-%d" % (ref, num)
      if net is None:
        body.append(no_connect(px, py, key))
      elif net == B.N_GND:
        power(gnd, px, py)
      elif net == B.N_3V3:
        power(v33, px, py)
      else:
        body.append(label(net, px, py, left, key))
      del name

  # ESP32-S3 SuperMini headers.
  j1 = (63.5, 76.2)
  j2 = (63.5, 127.0)
  for ref, (x, y), pins in (("J1", j1, B.J1_PINS), ("J2", j2, B.J2_PINS)):
    body.append(symbol(conn9, ref, B.VALUES[ref], x, y, B.FOOTPRINTS[ref],
                       B.DESCR[ref]))
    wire_pins(ref, conn9, x, y, pins)
    for num, (name, _) in pins.items():
      px, py = pin_xy(conn9, x, y, num)
      body.append(text(name, x + 5.08, py + 0.5, "%s-%d" % (ref, num)))

  # CC1101 module socket.
  j3 = (152.4, 76.2)
  body.append(symbol(conn24, "J3", B.VALUES["J3"], j3[0], j3[1],
                     B.FOOTPRINTS["J3"], B.DESCR["J3"]))
  wire_pins("J3", conn24, j3[0], j3[1], B.J3_PINS)

  # Decoupling at the CC1101 VDD pin.
  for i, (ref, x) in enumerate((("C1", 139.7),)):
    y = 114.3
    body.append(symbol(cap, ref, B.VALUES[ref], x, y, B.FOOTPRINTS[ref],
                       B.DESCR[ref]))
    p1 = pin_xy(cap, x, y, 1)
    p2 = pin_xy(cap, x, y, 2)
    power(v33, *p1)
    power(gnd, *p2)
    if i == 0:
      flag_at(*p1, n=1)
      flag_at(*p2, n=2)

  # Mounting holes.
  for i, ref in enumerate(("H1", "H2", "H3", "H4")):
    body.append(symbol(hole, ref, B.VALUES[ref], 127.0 + 12.7 * i, 152.4,
                       B.FOOTPRINTS[ref], B.DESCR[ref], in_bom=False))

  body.append(text("ESP32-S3 SuperMini <-> CC1101 carrier. CC1101 is 3.3 V "
                   "only: never connect 5V.", 50.8, 40.64, "note1", 2.0))
  body.append(text("GPIO3 left unused (strapping / VBUS sense). Pin map is "
                   "set in esphome substitutions.", 50.8, 45.72, "note2"))

  head = ("(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n"
          "\t(generator_version \"10.0\")\n\t(uuid \"%s\")\n\t(paper \"A4\")\n"
          "\t(title_block\n\t\t(title \"eyocean-ha ESP32-S3 SuperMini + CC1101 "
          "carrier\")\n\t\t(rev \"1.0\")\n\t)\n\t(lib_symbols\n" % B.ROOT_UUID)
  lib_text = "".join(
      "\t\t" + l.raw.replace("\n", "\n\t") + "\n" for l in libs)
  tail = ("\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n"
          "\t)\n\t(embedded_fonts no)\n)\n")
  with open(OUT, "w") as f:
    f.write(head + lib_text + "\t)\n" + "".join(body) + tail)
  print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
  main()
