// eyocean-ha enclosure: ESP32-S3 SuperMini + CC1101 carrier board (pcb/).
//
// Two-piece box held together by four M2 flat-head (countersunk, DIN 965 /
// ISO 10642) bolts entering flush from the lid top, through the lid pillars,
// the carrier board's M2 holes and the base standoffs, into M2 hex nuts
// captured in pockets under the base. The same four bolts clamp the board.
//
// The shell splits on the CC1101 SMA axis: the base wall has a U-slot so the
// socketed CC1101 drops in with its SMA thread already through the east
// wall; the lid closes the hole. USB-C opens in the west wall, WiFi slots sit
// over and beside the SuperMini's ceramic antenna.
//
// Frame: x/y follow pcb/scripts/board_def.py (origin = board north-west
// corner, +x east toward the SMA) with y negated (scad +y = north);
// z = 0 is the carrier board's bottom face.
//
//   openscad -D 'part="bottom"' -o enclosure_bottom.3mf cad/enclosure.scad
//   openscad -D 'part="lid"'    -o enclosure_lid.3mf    cad/enclosure.scad

include <BOSL2/std.scad>

/* [Part] */
// What to show / export
part = "assembly";  // [assembly, bottom, lid, print]

/* [Carrier board (pcb/scripts/board_def.py)] */
board_w = 56;       // [40:0.5:80]
board_h = 32;       // [20:0.5:50]
pcb_t = 1.6;        // [0.8:0.1:2.0]
hole_inset = 3;     // [2:0.5:5]

/* [Module stack-up - measure yours] */
// Female socket body height above the carrier (low-profile: 5.0)
socket_h = 8.5;     // [4:0.1:12]
// Plastic spacer of the male headers soldered to the modules
pin_spacer_h = 2.5; // [0:0.1:4]
// ESP32-S3 SuperMini board
sm_len = 22.52;
sm_wid = 18;
sm_t = 1.0;         // [0.8:0.1:1.6]
usb_shell = [8.94, 3.26];
// USB-C shell overhang beyond the SuperMini's west edge
usb_overhang = 0.3; // [0:0.1:1.5]
// CC1101 module (CC1101_specs/CC1101-Product-size): A x B, C, D
cc_x = 25.5;
cc_y = 10.75;
cc_len = 28;
cc_wid = 15;
cc_t = 1.2;
cc_h = 5.0;
// SMA axis from the module's north edge (B - I = 15 - 8.4)
sma_from_n = 6.6;
// Unthreaded SMA body between module edge and thread start
sma_body = 2.5;     // [0:0.1:5]
sma_thread = [6.3, 8.0];  // M, L

/* [Case] */
wall = 2.0;         // [1.2:0.2:3]
floor_t = 2.0;      // [1.2:0.2:3]
roof_t = 2.0;       // [1.2:0.2:3]
// Board edge to inner wall
gap = 0.5;          // [0.2:0.1:1.5]
// Board bottom above the floor (socket solder tails)
standoff_h = 3.5;   // [2:0.5:6]
// Air above the tallest module part
top_clear = 1.5;    // [0.5:0.25:4]
corner_r = 3;       // [1:0.5:5]
pillar_d = 5.5;     // [5:0.25:7]
// Tongue height (inner half of the wall) at the split
lip_h = 1.5;        // [0.8:0.1:3]
lip_clear = 0.15;   // [0:0.05:0.4]

/* [Openings] */
usb_hole = [9.4, 3.7];
usb_pocket = [13.0, 7.5];
// Wall left at the USB connector face (pocket depth = wall - usb_lip)
usb_lip = 0.8;      // [0.6:0.1:1.6]
sma_hole_d = 6.5;   // [6.3:0.1:7.5]
slot_w = 1.8;       // [1:0.1:3]
slot_n = 4;         // [2:1:6]
slot_pitch = 2.6;   // [2:0.1:4]

/* [Fasteners: M2 flat head + M2 hex nut] */
// Shorter bolts sink the head into a counterbore in the lid pillar
bolt_len = 25;      // [16, 18, 20, 25, 30]
bolt_hole_d = 2.2;  // [2.0:0.05:2.6]
cs_d = 4.2;         // [3.8:0.1:4.8]
nut_af = 4.1;       // [4.0:0.05:4.4]
nut_h = 1.6;        // [1.2:0.1:2.0]
// Hex pocket depth from the base bottom (nut seats at its top)
nut_pocket = 3.2;   // [2.0:0.1:4.5]

/* [Hidden] */
$fn = 96;
epsilon = 0.01;
layer_height = 0.2;  // general utility part

// --- derived stack-up -------------------------------------------------------
module_z = pcb_t + socket_h + pin_spacer_h;  // module PCB bottoms
usb_z = module_z + sm_t + usb_shell.y / 2;
sma_z = module_z + cc_t / 2;
parts_top = max(module_z + sm_t + usb_shell.y, module_z + cc_h);
floor_top = -standoff_h;
z_bot = floor_top - floor_t;
roof_bot = parts_top + top_clear;
z_top = roof_bot + roof_t;
split_z = sma_z;

x_in0 = -max(gap, usb_overhang + 0.2);
x_in1 = max(board_w + gap, cc_x + cc_len + sma_body);
y_in0 = -(board_h + gap);  // south (scad y is negated board y)
y_in1 = gap;               // north
IN = [x_in1 - x_in0, y_in1 - y_in0];
IN_C = [(x_in0 + x_in1) / 2, (y_in0 + y_in1) / 2];
OUT = IN + [2 * wall, 2 * wall];

holes = [for (x = [hole_inset, board_w - hole_inset])
           for (y = [hole_inset, board_h - hole_inset]) [x, -y]];
sm_c = [sm_len / 2, -board_h / 2];
ant_x = sm_len - 3;  // SuperMini chip antenna, far (east) end

// Bolt tip 0.3 mm past the nut; the head sits flush or in a counterbore.
tip_z = z_bot + nut_pocket - nut_h - 0.3;
head_z = tip_z + bolt_len;           // top of the flat head
head_recess = max(0, z_top - head_z);
cs_depth = (cs_d - bolt_hole_d) / 2;  // 90 deg countersink
cbore_d = cs_d + 0.4;
// Up to 0.5 mm below flush is fine; deeper heads get a counterbore.
cbore = head_recess > 0.5;
// 0.8 mm (two FDM perimeters) around the counterbore; stays clear of the
// CC1101 module edge next to the east pillars.
lid_pillar_d = cbore ? max(pillar_d, cbore_d + 1.6) : pillar_d;
thick_z = head_z - cs_depth - 1.0;  // bottom of the thick pillar section

assert(head_z <= z_top + epsilon,
       str("bolt_len ", bolt_len, " too long: max ", z_top - tip_z));
assert(tip_z >= z_bot + 0.3, "nut_pocket too shallow for nut_h");
assert(nut_pocket <= floor_t + standoff_h - 1.2,
       "nut_pocket reaches the board");
assert(head_z - cs_depth > pcb_t + 3,
       str("bolt_len ", bolt_len, " too short to reach the nut"));
assert(cc_x + cc_len + sma_body + sma_thread.y > x_in1 + wall + 3,
       "less than 3 mm of SMA thread outside the wall");

echo(str("Case outside: ", OUT.x, " x ", OUT.y, " x ", z_top - z_bot, " mm"));
echo(str("Bolts: 4x M2x", bolt_len, " flat head (head ", head_recess,
         " mm below the lid top), 4x M2 hex nut ", nut_pocket,
         " mm deep in the base"));
echo(str("Split at z = ", split_z, " (SMA axis); USB-C centre ",
         usb_z - z_bot, " mm above the base bottom"));
echo(str("SMA thread outside wall: ",
         cc_x + cc_len + sma_body + sma_thread.y - (x_in1 + wall), " mm"));

// --- primitives -------------------------------------------------------------
// Rounded-rectangle prism around the inner cavity, grown by `grow`.
module box_prism(grow, z0, z1) {
  translate([IN_C.x, IN_C.y, z0])
    cuboid([IN.x + 2 * grow, IN.y + 2 * grow, z1 - z0],
           rounding = max(corner_r - wall + grow, 0.01), edges = "Z",
           anchor = BOTTOM);
}

module shell() {
  difference() {
    translate([IN_C.x, IN_C.y, z_bot])
      cuboid([OUT.x, OUT.y, z_top - z_bot], rounding = corner_r,
             edges = "Z", anchor = BOTTOM);
    box_prism(0, floor_top, roof_bot);
  }
}

// Inner half of the wall between z0 and z1 (the tongue / its groove).
module tongue(z0, z1, extra = 0) {
  difference() {
    box_prism(wall / 2 + extra, z0, z1);
    box_prism(-epsilon, z0 - epsilon, z1 + epsilon);
  }
}

module above(z) {
  translate([IN_C.x, IN_C.y, z]) cuboid([OUT.x + 2, OUT.y + 2, 100],
                                        anchor = BOTTOM);
}

module below(z) {
  translate([IN_C.x, IN_C.y, z]) cuboid([OUT.x + 2, OUT.y + 2, 100],
                                        anchor = TOP);
}

// --- openings ---------------------------------------------------------------
module usb_cut() {
  // Shell opening through the full wall, overmold pocket from outside. The
  // opening reaches below the split so neither half keeps a thin sliver.
  z_lo = min(usb_z - usb_hole.y / 2, split_z - 1.0);
  z_hi = usb_z + usb_hole.y / 2;
  translate([x_in0 - wall - epsilon, sm_c.y, (z_lo + z_hi) / 2])
    cuboid([wall + 2 * epsilon, usb_hole.x, z_hi - z_lo], rounding = 1,
           edges = "X", anchor = LEFT);
  translate([x_in0 - wall - epsilon, sm_c.y, usb_z])
    cuboid([wall - usb_lip + epsilon, usb_pocket.x, usb_pocket.y],
           rounding = 2, edges = "X", anchor = LEFT);
}

module sma_cut(raise = 0) {
  y = -(cc_y + sma_from_n);
  hull() for (dz = [0, raise])
    translate([x_in1 - epsilon, y, sma_z + dz])
      cyl(d = sma_hole_d, h = wall + 2 * epsilon, orient = RIGHT,
          anchor = BOTTOM);
}

module wifi_slots() {
  xs = [for (i = [0 : slot_n - 1]) ant_x + (i - (slot_n - 1) / 2) * slot_pitch];
  // Roof, across the antenna end.
  for (x = xs)
    translate([x, sm_c.y, roof_bot - epsilon])
      cuboid([slot_w, sm_wid - 4, roof_t + 2 * epsilon],
             rounding = slot_w / 2 - 0.01, edges = "Z", anchor = BOTTOM);
  // North and south walls, beside the antenna, above the tongue.
  z0 = split_z + lip_h + 1.0;
  for (x = xs, side = [-1, 1])
    translate([x, side > 0 ? y_in1 - epsilon : y_in0 - wall - epsilon,
               (z0 + roof_bot - 0.8) / 2])
      cuboid([slot_w, wall + 2 * epsilon, roof_bot - 0.8 - z0],
             rounding = slot_w / 2 - 0.01, edges = "Y", anchor = FRONT);
}

module bolt_bores() {
  for (h = holes) translate([h.x, h.y, 0]) {
    down(1) cyl(d = bolt_hole_d, h = z_top - z_bot + 2, anchor = BOTTOM,
                $fn = 32);
    // 90 deg countersink under the head, plus a counterbore above it when a
    // shorter bolt is used.
    translate([0, 0, head_z - cs_depth])
      cyl(d1 = bolt_hole_d, d2 = cs_d, h = cs_depth + epsilon,
          anchor = BOTTOM, $fn = 48);
    up(head_z) cyl(d = cbore ? cbore_d : cs_d,
                   h = head_recess + 1, anchor = BOTTOM, $fn = 48);
    // Hex nut trap, open at the base bottom.
    translate([0, 0, z_bot - epsilon])
      cyl(d = nut_af / cos(30), h = nut_pocket + epsilon, anchor = BOTTOM,
          $fn = 6, spin = 30);
  }
}

// --- parts ------------------------------------------------------------------
module bottom_case() {
  difference() {
    union() {
      intersection() { shell(); below(split_z); }
      tongue(split_z - epsilon, split_z + lip_h);
      for (h = holes)  // board standoffs
        translate([h.x, h.y, floor_top - epsilon])
          cyl(d = pillar_d, h = standoff_h + epsilon, anchor = BOTTOM,
              chamfer2 = 0.4);
    }
    usb_cut();
    sma_cut(raise = lip_h + sma_hole_d);
    bolt_bores();
  }
}

module top_lid() {
  difference() {
    union() {
      difference() {
        intersection() { shell(); above(split_z); }
        tongue(split_z - epsilon, split_z + lip_h + lip_clear, lip_clear);
      }
      for (h = holes)  // clamp pillars down onto the board
        translate([h.x, h.y, pcb_t]) {
          cyl(d = pillar_d, h = roof_bot - pcb_t + epsilon, anchor = BOTTOM,
              chamfer1 = 0.4);
          if (cbore)  // thicker around the head counterbore
            translate([0, 0, thick_z - pcb_t])
              cyl(d = lid_pillar_d, h = roof_bot - thick_z + epsilon,
                  anchor = BOTTOM, chamfer1 = 1.0);
        }
    }
    usb_cut();
    sma_cut();
    wifi_slots();
    bolt_bores();
  }
}

// --- reference models (assembly view only, not printed) ---------------------
module board_and_modules() {
  color("darkgreen") translate([0, -board_h, 0])
    cube([board_w, board_h, pcb_t]);
  color("#222") for (y = [board_h / 2 - 7.62, board_h / 2 + 7.62])
    translate([1.4 - 1.27, -y - 1.27, pcb_t]) cube([22.86, 2.54, socket_h]);
  color("#222") translate([cc_x + 1.5 - 1.27, -(cc_y + 1.5 + 8.89), pcb_t])
    cube([5.08, 10.16, socket_h]);
  color("royalblue") translate([0, -board_h / 2 - sm_wid / 2, module_z])
    cube([sm_len, sm_wid, sm_t]);
  color("silver") translate([-usb_overhang, sm_c.y, usb_z])
    cuboid([7.3, usb_shell.x, usb_shell.y], rounding = 1, edges = "X",
           anchor = LEFT);
  color("white") translate([ant_x - 1, sm_c.y, module_z + sm_t])
    cuboid([2, 6, 1], anchor = BOTTOM);
  color("purple") translate([cc_x, -(cc_y + cc_wid), module_z])
    cube([cc_len, cc_wid, cc_t]);
  color("gold") translate([cc_x + cc_len, -(cc_y + sma_from_n), sma_z])
    cyl(d = sma_thread.x, h = sma_body + sma_thread.y, orient = RIGHT,
        anchor = BOTTOM);
}

if (part == "bottom") {
  // Orient for printing: floor on the bed.
  up(-z_bot) bottom_case();
} else if (part == "lid") {
  // Orient for printing: roof on the bed.
  up(z_top) xrot(180) top_lid();
} else if (part == "print") {
  up(-z_bot) bottom_case();
  fwd(OUT.y + 8) up(z_top) xrot(180) top_lid();
} else {
  bottom_case();
  board_and_modules();
  up(18) top_lid();  // exploded
}
