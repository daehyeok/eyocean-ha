#!/usr/bin/env python3
"""Generate pcb/eyocean_carrier.kicad_pcb from board_def.py.

Run with KiCad's bundled Python (it needs the pcbnew module):
  ~/.bin/kicad.AppImage python3.11 pcb/scripts/gen_pcb.py <kicad-footprint-dir>

Places the footprints, draws the outline, routes every net by hand-picked
coordinates (planar per layer), adds GND pours on both layers, the WiFi
antenna keep-out and the silkscreen, fills the zones and saves the board.
"""

import os
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_def as B  # pylint: disable=g-import-not-at-top

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", B.PROJECT + ".kicad_pcb"))
ORIGIN = (100.0, 100.0)  # board north-west corner on the KiCad page

W_SIG = 0.25
W_PWR = 0.5
VIA_D = 0.6
VIA_DRILL = 0.3


def mm(x, y):
  return pcbnew.VECTOR2I_MM(ORIGIN[0] + x, ORIGIN[1] + y)


def to_local(v):
  return (pcbnew.ToMM(v.x) - ORIGIN[0], pcbnew.ToMM(v.y) - ORIGIN[1])


CC_FP = "CC1101_Socket_2x04_P2.54mm_TopView"


def set_description(fp, text):
  """Set the symbol-synced 'Description' field (API differs per version)."""
  for getter in ("GetFieldByName", "GetField"):
    try:
      field = getattr(fp, getter)("Description")
      if field is not None:
        field.SetText(text)
        return
    except Exception:  # pylint: disable=broad-except
      pass
  fp.SetField("Description", text)


def make_cc1101_footprint(fpdir):
  """Write eyocean.pretty/CC1101_Socket_2x04_P2.54mm_TopView.kicad_mod.

  KiCad's PinSocket_2x04 numbers its pads for face-to-face mating (pad 2 is
  WEST of pad 1). The CC1101 module's header points down into the socket, so
  the pads must follow the module's own top-view pinout (CC1101-Pin-out-1:
  pad 2 EAST of pad 1). This is the stock footprint mirrored in X.
  """
  src = os.path.join(fpdir, "Connector_PinSocket_2.54mm.pretty",
                     "PinSocket_2x04_P2.54mm_Vertical.kicad_mod")
  with open(src) as f:
    text = f.read()

  def neg(m):
    v = -float(m.group(2))
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return m.group(1) + ("0" if s == "-0" else s)

  text = re.sub(r"(\((?:at|start|end|center|mid|xy) )(-?[\d.]+)", neg, text)
  text = text.replace('(footprint "PinSocket_2x04_P2.54mm_Vertical"',
                      '(footprint "%s"' % CC_FP, 1)
  text = text.replace(
      '(descr "', '(descr "CC1101 module socket, pads numbered in the '
      'module top view (X-mirror of PinSocket_2x04). ', 1)
  text = text.replace("(xyz 0 0 0)\n\t\t)\n\t\t(scale",
                      "(xyz 2.54 0 0)\n\t\t)\n\t\t(scale", 1)
  out_dir = os.path.join(HERE, "..", "eyocean.pretty")
  os.makedirs(out_dir, exist_ok=True)
  with open(os.path.join(out_dir, CC_FP + ".kicad_mod"), "w") as f:
    f.write(text)
  return os.path.normpath(os.path.join(out_dir, ".."))


class Builder:
  """Wraps a BOARD with helpers for nets, footprints, copper and graphics."""

  def __init__(self, fpdir):
    self.fpdir = fpdir
    self.projdir = make_cc1101_footprint(fpdir)
    self.board = pcbnew.NewBoard(OUT)
    self.nets = {}

  def net(self, name):
    if name not in self.nets:
      ni = pcbnew.NETINFO_ITEM(self.board, name)
      self.board.Add(ni)
      self.nets[name] = ni
    return self.nets[name]

  def footprint(self, ref, pad_targets, rot=None, pos=None):
    """Load and place a footprint.

    Args:
      ref: reference designator (key into board_def tables).
      pad_targets: {pad number: (x, y)} board-local positions. The first two
        entries pick the rotation, the first one the translation.
      rot: fixed rotation (degrees) when pad_targets is empty.
      pos: footprint origin when pad_targets is empty.
    Returns:
      The placed FOOTPRINT.
    """
    lib, name = B.FOOTPRINTS[ref].split(":")
    libdir = self.projdir if lib == "eyocean" else self.fpdir
    fp = pcbnew.FootprintLoad(os.path.join(libdir, lib + ".pretty"), name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(B.VALUES[ref])
    set_description(fp, B.DESCR[ref])
    if ref.startswith(("H", "C")):
      fp.Reference().SetVisible(False)
    fp.SetPath(pcbnew.KIID_PATH("/" + B.uid(ref)))
    fp.SetSheetfile(B.PROJECT + ".kicad_sch")
    fp.SetSheetname("/")
    self.board.Add(fp)
    if pad_targets and len(pad_targets) == 1:
      (n1, t1), = pad_targets.items()
      fp.SetOrientationDegrees(rot or 0)
      fp.SetPosition(mm(0, 0))
      p1 = to_local(fp.FindPadByNumber(str(n1)).GetPosition())
      fp.SetPosition(mm(t1[0] - p1[0], t1[1] - p1[1]))
    elif pad_targets:
      items = list(pad_targets.items())
      (n1, t1), (n2, t2) = items[0], items[1]
      want = (t2[0] - t1[0], t2[1] - t1[1])
      best = None
      for r in (0, 90, 180, 270):
        fp.SetOrientationDegrees(r)
        fp.SetPosition(mm(0, 0))
        p1 = to_local(fp.FindPadByNumber(str(n1)).GetPosition())
        p2 = to_local(fp.FindPadByNumber(str(n2)).GetPosition())
        got = (p2[0] - p1[0], p2[1] - p1[1])
        err = abs(got[0] - want[0]) + abs(got[1] - want[1])
        if best is None or err < best[0]:
          best = (err, r)
      assert best[0] < 1e-3, (ref, best)
      fp.SetOrientationDegrees(best[1])
      fp.SetPosition(mm(0, 0))
      p1 = to_local(fp.FindPadByNumber(str(n1)).GetPosition())
      fp.SetPosition(mm(t1[0] - p1[0], t1[1] - p1[1]))
      for n, t in items:
        got = to_local(fp.FindPadByNumber(str(n)).GetPosition())
        assert abs(got[0] - t[0]) < 1e-3 and abs(got[1] - t[1]) < 1e-3, (
            ref, n, got, t)
    else:
      fp.SetOrientationDegrees(rot or 0)
      fp.SetPosition(mm(*pos))
    return fp

  def assign(self, fp, pins):
    for num, (_, netname) in pins.items():
      if netname is None:
        netname = "unconnected-(%s-Pin_%d-Pad%d)" % (fp.GetReference(), num,
                                                    num)
      elif not netname.startswith(("+", "GND")):
        netname = "/" + netname
      fp.FindPadByNumber(str(num)).SetNet(self.net(netname))

  def track(self, netname, pts, layer, width=W_SIG):
    for a, b in zip(pts, pts[1:]):
      t = pcbnew.PCB_TRACK(self.board)
      t.SetStart(mm(*a))
      t.SetEnd(mm(*b))
      t.SetWidth(pcbnew.FromMM(width))
      t.SetLayer(layer)
      t.SetNet(self.net(netname))
      self.board.Add(t)

  def via(self, netname, xy):
    v = pcbnew.PCB_VIA(self.board)
    v.SetPosition(mm(*xy))
    v.SetDrill(pcbnew.FromMM(VIA_DRILL))
    v.SetWidth(pcbnew.FromMM(VIA_D))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(self.net(netname))
    self.board.Add(v)

  def line(self, a, b, layer, width=0.15):
    s = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(*a))
    s.SetEnd(mm(*b))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    self.board.Add(s)

  def arc(self, start, mid, end, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(self.board, pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(mm(*start), mm(*mid), mm(*end))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    self.board.Add(s)

  def rect(self, x0, y0, x1, y1, layer, width=0.15):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
      self.line(a, b, layer, width)

  def text(self, s, xy, layer=pcbnew.F_SilkS, size=1.0, angle=0):
    t = pcbnew.PCB_TEXT(self.board)
    t.SetText(s)
    t.SetPosition(mm(*xy))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    t.SetTextThickness(pcbnew.FromMM(0.15))
    t.SetTextAngleDegrees(angle)
    self.board.Add(t)

  def zone(self, netname, layer, pts, clearance=0.3):
    z = pcbnew.ZONE(self.board)
    z.SetLayer(layer)
    z.SetNet(self.net(netname))
    z.Outline().NewOutline()
    for p in pts:
      z.Outline().Append(mm(*p))
    z.SetLocalClearance(pcbnew.FromMM(clearance))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.4))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))
    self.board.Add(z)
    return z

  def keepout(self, x0, y0, x1, y1, name):
    z = pcbnew.ZONE(self.board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    lset = pcbnew.LSET()
    lset.AddLayer(pcbnew.F_Cu)
    lset.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(lset)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.Outline().NewOutline()
    for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
      z.Outline().Append(mm(*p))
    self.board.Add(z)


def outline(b):
  w, h, r = B.BOARD_W, B.BOARD_H, B.CORNER_R
  e = pcbnew.Edge_Cuts
  b.line((r, 0), (w - r, 0), e, 0.1)
  b.line((w, r), (w, h - r), e, 0.1)
  b.line((w - r, h), (r, h), e, 0.1)
  b.line((0, h - r), (0, r), e, 0.1)
  k = r * (1 - 0.70710678)
  b.arc((w - r, 0), (w - k, k), (w, r), e)
  b.arc((w, h - r), (w - k, h - k), (w - r, h), e)
  b.arc((r, h), (k, h - k), (0, h - r), e)
  b.arc((0, r), (k, k), (r, 0), e)


def route(b):
  """Hand-routed copper. See design.md for the channel plan."""
  f, bk = pcbnew.F_Cu, pcbnew.B_Cu
  j1, j3 = B.j1_pad, B.j3_pad

  # 3V3: SuperMini 3V3 pin north, along the north margin, down the cap rail
  # (C2 and C1 pad 1 sit on it) and west into CC1101 VDD.
  v = B.j2_pad(3)
  b.track(B.N_3V3, [v, (v[0], 6.2), (B.CAP_RAIL_X - 1.6, 6.2),
                    (B.CAP_RAIL_X, 7.8), (B.CAP_RAIL_X, j3(2)[1]), j3(2)],
          f, W_PWR)

  # Signals: each SuperMini pad drops south into a channel under the left
  # header row, runs east, turns north in the corridor between the antenna
  # keep-out and the CC1101 socket and enters its port. Deeper channel =
  # further west pad = further east corridor = further south port, so no
  # two tracks on one layer ever cross.
  depth = (25.0, 25.6, 26.2)
  corridor = (23.6, 24.3, 25.0)
  # F.Cu feeds the odd (west) CC1101 column straight in at the pad row.
  for i, (sm_pin, cc_pin) in enumerate(((9, 3), (7, 5), (4, 7))):
    s, t = j1(sm_pin), j3(cc_pin)
    net = B.J3_PINS[cc_pin][1]
    b.track(net, [s, (s[0], depth[i]), (corridor[i], depth[i]),
                  (corridor[i], t[1]), t], f)
  # B.Cu feeds the even (east) column between the odd pads, then jogs 45 deg.
  for i, (sm_pin, cc_pin) in enumerate(((8, 4), (6, 6), (3, 8))):
    s, t = j1(sm_pin), j3(cc_pin)
    net = B.J3_PINS[cc_pin][1]
    lane = t[1] + B.PITCH / 2
    knee = t[0] - B.PITCH / 2
    b.track(net, [s, (s[0], depth[i]), (corridor[i], depth[i]),
                  (corridor[i], lane), (knee, lane), t], bk)

  # GND stitching vias tie the two pours together.
  for xy in ((12.0, 16.0), (38.0, 16.0), (45.0, 5.0), (45.0, 28.0),
             (10.0, 29.0), (35.6, 12.6), (35.8, 7.4), (8.0, 4.0)):
    b.via(B.N_GND, xy)


def silk(b):
  s = pcbnew.F_SilkS
  fab = pcbnew.F_Fab
  # Module outlines on Fab (the modules sit ~11 mm above the board on
  # sockets; on silk they would collide with the socket outlines).
  b.rect(0.4, B.BOARD_H / 2 - B.SM_WID / 2, B.SM_LEN,
         B.BOARD_H / 2 + B.SM_WID / 2, fab, 0.1)
  b.rect(B.CC_X, B.CC_Y, B.CC_X + B.CC_LEN, B.CC_Y + B.CC_WID, fab, 0.1)
  x0, y0, x1, y1 = B.ANT_KEEPOUT
  b.rect(x0, y0, x1, y1, fab, 0.1)
  b.text("ESP32-S3", (9.0, 14.0))
  b.text("SuperMini", (9.0, 15.6))
  b.text("<- USB-C", (9.0, 18.0))
  b.text("WiFi ANT", (20.1, 16.0), size=1.0, angle=90)
  b.text("CC1101 433MHz", (41.0, 22.5))
  b.text("SMA ->", (48.0, 16.0), angle=90)
  b.text("eyocean-ha carrier v1.0", (40.0, 30.0))
  b.text("TX", (B.j1_pad(1)[0] + 0.2, 27.3))
  b.text("5V", (B.j2_pad(1)[0], 5.7), size=0.8)
  b.text("3V3", (B.j2_pad(3)[0] + 0.3, 4.9), size=0.8)
  b.text("3V3 only", (16.0, 4.6), size=1.0)


def main():
  fpdir = sys.argv[1]
  b = Builder(fpdir)
  ds = b.board.GetDesignSettings()
  ds.m_CopperEdgeClearance = pcbnew.FromMM(0.5)
  ds.m_HoleClearance = pcbnew.FromMM(0.25)

  outline(b)
  fps = {}
  fps["J1"] = b.footprint("J1", {n: B.j1_pad(n) for n in range(1, 10)})
  fps["J2"] = b.footprint("J2", {n: B.j2_pad(n) for n in range(1, 10)})
  fps["J3"] = b.footprint("J3", {n: B.j3_pad(n) for n in range(1, 9)})
  b.assign(fps["J1"], B.J1_PINS)
  b.assign(fps["J2"], B.J2_PINS)
  b.assign(fps["J3"], B.J3_PINS)
  for ref, p1 in (("C1", B.C1_PAD1), ("C2", B.C2_PAD1)):
    # Rotation 0 puts pad 2 east of pad 1 (away from the 3V3 rail).
    fp = b.footprint(ref, {1: p1}, rot=0)
    fp.FindPadByNumber("1").SetNet(b.net(B.N_3V3))
    fp.FindPadByNumber("2").SetNet(b.net(B.N_GND))
  for i, xy in enumerate(B.HOLES):
    b.footprint("H%d" % (i + 1), {}, rot=0, pos=xy)

  route(b)
  board_poly = [(0, 0), (B.BOARD_W, 0), (B.BOARD_W, B.BOARD_H),
                (0, B.BOARD_H)]
  b.zone(B.N_GND, pcbnew.F_Cu, board_poly)
  b.zone(B.N_GND, pcbnew.B_Cu, board_poly)
  b.keepout(*B.ANT_KEEPOUT, name="WIFI_ANT_KEEPOUT")
  silk(b)

  # Zones are filled by `kicad-cli pcb drc --refill-zones --save-board`
  # (see build.sh): the standalone ZONE_FILLER ignores the project's hole and
  # edge clearances.
  b.board.BuildConnectivity()
  pcbnew.SaveBoard(OUT, b.board)
  print("wrote", OUT)


if __name__ == "__main__":
  main()
