"""
DIY iPod-style case - parametric CadQuery model
------------------------------------------------
Two printed parts (front shell, back shell) held by 4x M2 screws.

Coordinates (mm):  X = left/right, Y = up/down (+Y is the top of the player),
                   Z = depth: Z=0 is the FRONT face, Z=T is the BACK face.

Everything that depends on a purchased module is a parameter below.
MEASURE YOUR ACTUAL MODULES with calipers and edit the numbers before printing -
generic modules from different sellers differ by a millimetre or two.

Run:  python3 ipod_case.py      -> writes STEP + STL files next to this script
"""
import os
import cadquery as cq

OUT = os.path.dirname(os.path.abspath(__file__))

# ============================== PARAMETERS ==================================
# --- body ---
W = 62.0            # outer width
T = 17.0            # outer thickness (front face to back face)
R = 8.0             # corner radius (plan view)
WALL = 2.0          # side wall thickness
FRONT_WALL = 1.6    # front face thickness (around the screen)
BACK_WALL = 1.8     # back wall thickness
SEAM_Z = 11.0       # Z where the two halves meet
FRONT_FILLET = 2.0  # edge rounding, front
BACK_FILLET = 3.0   # edge rounding, back

# --- LCD: Waveshare-style 2.4" ILI9341 SPI module, portrait ---
LCD_W, LCD_H, LCD_T = 43.3, 70.5, 4.5   # PCB width, height, total thickness (glass+backlight+PCB)
ACT_W, ACT_H = 36.72, 48.96             # visible active area (portrait)
ACT_TOP = 6.0       # distance from the PCB top edge to the top of the active area  <-- MEASURE
LCD_CLR = 0.2       # clearance per side in the LCD pocket
FRAME_WALL = 1.2    # wall of the LCD locating frame
WINDOW_MARGIN = 1.0 # window is this much bigger than the active area (total, both sides)
GAP_TOP = 1.0       # inner top edge -> LCD top edge

# --- touch click wheel (custom capacitive PCB behind the front skin) ---
WHEEL_D = 38.0          # engraved outer ring diameter
WHEEL_PCB_D = 39.0      # wheel PCB pocket diameter (PCB ~38.6 mm)
WHEEL_RING_WALL = 0.8   # wall of the pocket that locates the wheel PCB
SKIN = 1.2              # plastic left in front of the wheel PCB (touch sensing goes through it)
CENTER_D = 14.0         # engraved centre-button ring diameter
ENGRAVE_DEPTH = 0.3
ENGRAVE_W = 0.6

# --- Raspberry Pi Zero 2 W (long axis vertical, SD-card end at the TOP) ---
PI_L, PI_W, PI_H = 65.0, 30.0, 5.2
PI_HOLES_X, PI_HOLES_Y = 23.0, 58.0     # hole spacing (across, along)
PI_CX = -12.5
PI_TOP_D = 1.1      # gap from the inner top edge to the SD-card end (keeps the Pi's rounded corner clear of the shell corner)

# --- DAC (PCM5102A board, jack end at the TOP) ---
DAC_W, DAC_L = 20.0, 32.0
DAC_CX = 14.0
JACK_Z = 9.8        # centre of the 3.5 mm jack, measured from the FRONT face  <-- MEASURE
JACK_HOLE_D = 6.6

# --- battery (LiPo 103040: 10 x 30 x 40 mm, ~1200 mAh) ---
BAT_L, BAT_W, BAT_T = 40.0, 30.0, 10.0

# --- ports ---
USBC_W, USBC_H, USBC_Z = 9.4, 3.6, 8.5  # USB-C panel breakout cut-out (bottom edge)
SD_SLOT_W, SD_SLOT_H, SD_SLOT_Z = 15.0, 2.4, 11.4  # microSD slot in the top edge

# --- screws: M2 x 12 self-tapping into printed bosses ---
BOSS_D = 5.4
PILOT_D = 1.8       # front boss pilot hole
CLEAR_D = 2.4       # back clearance hole
CSK_D = 4.4         # countersink diameter at the back face

# --- optional thin metal back plate (e.g. 0.4 mm stainless/aluminium, glued on) ---
PLATE_W = 46.0
PLATE_DEPTH = 0.5

# ============================ DERIVED LAYOUT ================================
# distances "d" are measured DOWN from the inner top edge of the cavity
LCD_TOP_D = GAP_TOP
LCD_BOT_D = LCD_TOP_D + LCD_H
FRAME_BOT_D = LCD_BOT_D + LCD_CLR + FRAME_WALL
WHEEL_RING_D = WHEEL_PCB_D + 2 * WHEEL_RING_WALL
WHEEL_TOP_D = FRAME_BOT_D + 0.4
WHEEL_C_D = WHEEL_TOP_D + WHEEL_RING_D / 2
WHEEL_BOT_D = WHEEL_TOP_D + WHEEL_RING_D
INNER_H = WHEEL_BOT_D + 0.6
H = INNER_H + 2 * WALL                      # outer height


def Y(d):
    """model Y coordinate for a distance d below the inner top edge"""
    return H / 2 - WALL - d


Z_BI = T - BACK_WALL                        # inner surface of the back wall


# ============================== HELPERS =====================================
def rr(w, h, r, z0, depth):
    return (cq.Workplane("XY").workplane(offset=z0).rect(w, h).extrude(depth)
            .edges("|Z").fillet(r))


def ring_profile(off_out, off_in, z0, depth):
    """rounded-rect ring following the body outline; offsets measured inward from the outer skin"""
    outer = rr(W - 2 * off_out, H - 2 * off_out, R - off_out, z0, depth)
    inner = rr(W - 2 * off_in, H - 2 * off_in, R - off_in, z0 - 0.1, depth + 0.2)
    return outer.cut(inner)


def cyl(r, h, x, y, z0, direction=(0, 0, 1)):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, h, cq.Vector(x, y, z0), cq.Vector(*direction)))


def zslab(z0, z1):
    return (cq.Workplane("XY").box(W + 20, H + 20, z1 - z0, centered=(True, True, False))
            .translate((0, 0, z0)))


# ============================ BUILD THE SHELL ===============================
outer = rr(W, H, R, 0, T)
outer = outer.faces("<Z").edges().fillet(FRONT_FILLET)
outer = outer.faces(">Z").edges().fillet(BACK_FILLET)

cavity = rr(W - 2 * WALL, H - 2 * WALL, R - WALL, FRONT_WALL, T - FRONT_WALL - BACK_WALL)
shell = outer.cut(cavity)

# ---- LCD locating frame (inside, front side) ----
lcd_cy = Y(LCD_TOP_D + LCD_H / 2)
fw, fh = LCD_W + 2 * LCD_CLR, LCD_H + 2 * LCD_CLR
frame = (cq.Workplane("XY").workplane(offset=FRONT_WALL).center(0, lcd_cy)
         .rect(fw + 2 * FRAME_WALL, fh + 2 * FRAME_WALL).extrude(LCD_T)
         .faces(">Z").workplane().rect(fw, fh).cutThruAll())
shell = shell.union(frame)

# ---- wheel PCB locating ring (with two cable notches) ----
wheel_cy = Y(WHEEL_C_D)
wring = (cq.Workplane("XY").workplane(offset=FRONT_WALL).center(0, wheel_cy)
         .circle(WHEEL_RING_D / 2).circle(WHEEL_PCB_D / 2).extrude(1.8))
for sgn in (+1, -1):
    notch = (cq.Workplane("XY").box(6, 4, 3, centered=(True, True, False))
             .translate((0, wheel_cy + sgn * (WHEEL_RING_D / 2 - 0.4), FRONT_WALL - 0.5)))
    wring = wring.cut(notch)
shell = shell.union(wring)
# recess in the front wall so only SKIN of plastic is left in front of the wheel PCB
wheel_recess = cyl(WHEEL_PCB_D / 2, FRONT_WALL - SKIN + 0.01, 0, wheel_cy, SKIN)
shell = shell.cut(wheel_recess)

# ---- screw bosses (4) ----
bx = W / 2 - WALL - BOSS_D / 2
boss_pts = [(sx * bx, Y(d)) for d in (PI_TOP_D + PI_L + 3.4, INNER_H - 6.0) for sx in (-1, 1)]
for (x, y) in boss_pts:
    shell = shell.union(cyl(BOSS_D / 2, Z_BI - FRONT_WALL + 0.2, x, y, FRONT_WALL - 0.1))

# ---- Pi standoffs (in the back half) ----
pi_cy = Y(PI_TOP_D + PI_L / 2)
for sx in (-1, 1):
    for sy in (-1, 1):
        px, py = PI_CX + sx * PI_HOLES_X / 2, pi_cy + sy * PI_HOLES_Y / 2
        shell = shell.union(cyl(2.3, 1.6, px, py, Z_BI - 1.5))          # standoff
        shell = shell.union(cyl(1.2, 1.7, px, py, Z_BI - 1.5 - 1.6))    # locating pin

# ---- battery cradle ----
bat_cy = wheel_cy
cradle = (cq.Workplane("XY").workplane(offset=Z_BI - 3.0).center(0, bat_cy)
          .rect(BAT_L + 0.6 + 2.4, BAT_W + 0.6 + 2.4).extrude(3.1)
          .faces(">Z").workplane().rect(BAT_L + 0.6, BAT_W + 0.6).cutThruAll())
shell = shell.union(cradle)

# ============================== CUT-OUTS ====================================
# LCD window
win_cy = Y(LCD_TOP_D + ACT_TOP + ACT_H / 2)
window = (cq.Workplane("XY").box(ACT_W + WINDOW_MARGIN, ACT_H + WINDOW_MARGIN, 3.0, centered=(True, True, False))
          .translate((0, win_cy, -0.5)))
shell = shell.cut(window)

# engraved wheel rings on the front face
for d_out in (WHEEL_D, CENTER_D):
    groove = (cq.Workplane("XY").workplane(offset=-0.01).center(0, wheel_cy)
              .circle(d_out / 2).circle(d_out / 2 - ENGRAVE_W).extrude(ENGRAVE_DEPTH + 0.01))
    shell = shell.cut(groove)

# microSD slot (top edge) - crosses the seam, so it ends up half in each shell
sd = (cq.Workplane("XY").box(SD_SLOT_W, 6.0, SD_SLOT_H).edges("|Y").fillet(0.6)
      .translate((PI_CX, H / 2 - 1.0, SD_SLOT_Z)))
shell = shell.cut(sd)

# headphone jack hole (top edge)
shell = shell.cut(cyl(JACK_HOLE_D / 2, 6.0, DAC_CX, H / 2 - 4.0, JACK_Z, (0, 1, 0)))

# USB-C slot (bottom edge)
usbc = (cq.Workplane("XY").box(USBC_W, 6.0, USBC_H).edges("|Y").fillet(1.3)
        .translate((0, -H / 2 + 1.0, USBC_Z)))
shell = shell.cut(usbc)

# ============================ SPLIT INTO TWO ================================
front = shell.intersect(zslab(-1, SEAM_Z))
back = shell.intersect(zslab(SEAM_Z, T + 1))

# front: screw pilot holes + rebate that receives the back shell's tongue
for (x, y) in boss_pts:
    front = front.cut(cyl(PILOT_D / 2, 7.1, x, y, SEAM_Z - 7.0))
front = front.cut(ring_profile(1.0, 2.0, SEAM_Z - 1.8, 1.9))

# back: tongue, screw clearance holes + countersinks, back-plate recess
back = back.union(ring_profile(1.1, 2.0, SEAM_Z - 1.5, 1.6))
for (x, y) in boss_pts:
    back = back.cut(cyl(CLEAR_D / 2, T - SEAM_Z + 0.2, x, y, SEAM_Z - 0.1))
    csk = cq.Solid.makeCone(CLEAR_D / 2, CSK_D / 2, (CSK_D - CLEAR_D) / 2 + 0.01,
                            cq.Vector(x, y, T - (CSK_D - CLEAR_D) / 2), cq.Vector(0, 0, 1))
    back = back.cut(cq.Workplane("XY").add(csk))
plate = rr(PLATE_W, H - 16.0, 4.0, T - PLATE_DEPTH, PLATE_DEPTH + 0.1)
back = back.cut(plate)

# ============================== EXPORT ======================================
if __name__ == "__main__":
    f_shape, b_shape = front.val(), back.val()

    asm = cq.Assembly(name="ipod_case")
    asm.add(front, name="front_shell", color=cq.Color(0.88, 0.88, 0.90, 1))
    asm.add(back, name="back_shell", color=cq.Color(0.62, 0.64, 0.70, 1))
    asm.save(os.path.join(OUT, "ipod_case_assembly.step"))
    cq.exporters.export(front, os.path.join(OUT, "front_shell.step"))
    cq.exporters.export(back, os.path.join(OUT, "back_shell.step"))

    # STLs in print orientation: front face down; back shell flipped so its back face is on the bed
    cq.exporters.export(front, os.path.join(OUT, "front_shell.stl"), tolerance=0.01, angularTolerance=0.1)
    back_print = back.rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, T))
    cq.exporters.export(back_print, os.path.join(OUT, "back_shell.stl"), tolerance=0.01, angularTolerance=0.1)

    print(f"outer size  : {W:.1f} x {H:.1f} x {T:.1f} mm")
    print(f"front shell : valid={f_shape.isValid()}  volume={f_shape.Volume():.0f} mm3")
    print(f"back shell  : valid={b_shape.isValid()}  volume={b_shape.Volume():.0f} mm3")
