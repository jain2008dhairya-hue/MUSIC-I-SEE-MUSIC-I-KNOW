# DIY iPod

A pocket music player in the shape of a classic iPod, built from a Raspberry Pi Zero 2 W, a 2.4" colour display, an I2S DAC and a custom touch click wheel, in a 3D printed case. Target cost is under ₹10,000 (about $100), not counting printing.

## Why I built it

The iPod's click wheel is still one of the nicest ways to browse music. I wanted to see how close hobbyist parts get to it: the same screen resolution as the iPod Classic (320x240), a wheel you scroll with your thumb, and proper DAC audio instead of the Pi's noisy built-in output.

## How it works

- **Raspberry Pi Zero 2 W** runs the player (`mpd`) and draws a menu UI on the display.
- **2.4" ILI9341 LCD** (240x320) is driven over SPI0.
- **PCM5102A DAC** receives digital audio over I2S and outputs stereo line level to a 3.5 mm jack.
- **Touch wheel**: a custom PCB with 8 sector pads and a centre pad. An ESP32-S3 reads them on its capacitive touch inputs and sends wheel and click events to the Pi over UART. (The Pi has no touch inputs of its own.)
- **Power**: a 1200 mAh LiPo with an IP5306-class USB-C charge and boost module, switched by a slide switch, feeding a 5 V rail.
- **Case**: two printed shells (front and back) held by four M2 screws, 62 x 118.5 x 17 mm, with cut-outs for the microSD slot, headphone jack and USB-C, and a recess for a thin metal back plate.

## Images

**Case (CAD preview)**

![Case preview](images/case_preview.png)

**Wiring diagram**

![Wiring diagram](images/wiring_diagram.png)

The full KiCad schematic is in `PCB/ipod_player.kicad_sch`; the net-by-net connection list is in `PCB/ipod_connections.md`.

## Repository layout

| Folder / file | Contents |
|---|---|
| `CAD/` | Case: `ipod_case_assembly.step` (full assembly), print-ready `front_shell.stl` and `back_shell.stl`, and the parametric CadQuery script `ipod_case.py` |
| `PCB/` | KiCad project: schematic, module symbol library, connection table, and the script that generated them |
| `firmware/` | Pi configuration and pin map (player and touch firmware still to be written) |
| `BOM.csv` | Bill of materials with India prices |
| `images/` | Preview and wiring images |

## Bill of materials

Full list in [`BOM.csv`](BOM.csv). Estimated total: about **₹7,200** (printing excluded). Prices for the Pi, display and DAC come from Indian retailer listings; the rest are estimates.

## Printing and assembly

1. Print `front_shell.stl` face-down and `back_shell.stl` back-face-down, PLA or PETG, 0.2 mm layers. Supports are only needed around the port cut-outs.
2. Measure your actual display and DAC with calipers and compare to the parameters at the top of `CAD/ipod_case.py`. Edit and re-run the script if they differ (`pip install cadquery`, then `python3 ipod_case.py`).
3. Mount the display in the front frame, the wheel PCB in its round pocket, and the Pi on the standoffs in the back shell. Close with four M2x12 screws.

## Status

What is done: case modeled and checked for fit against the Pi, display, DAC, battery and wheel PCB; schematic complete; BOM priced.

What is not done yet: the wheel PCB layout (only its schematic exists), the player UI and touch firmware, and a physical build. The case has not been printed or tested. The ESP32-S3 board is not yet included in the case fit check; a small "Super Mini" size board mounted on the wheel PCB is the plan.
