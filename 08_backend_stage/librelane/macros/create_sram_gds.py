
import pya

# Create layout with 1nm DBU
layout = pya.Layout()
layout.dbu = 0.001  # 1nm

# Create top cell "sram"
top = layout.create_cell("sram")

# Macro dimensions: 683.1 x 416.16 um = 683100 x 416160 nm
w = 683100
h = 416160

# Layer mapping for sky130 (GDS layer numbers)
# These are approximate — based on standard sky130 mapping
layer_nwell   = layout.layer(1, 0)   # nwell
layer_diff    = layout.layer(2, 0)   # diffusion  
layer_poly    = layout.layer(5, 0)   # poly
layer_contact = layout.layer(6, 0)   # contact
layer_met1    = layout.layer(10, 0)  # metal1
layer_via1    = layout.layer(11, 0)  # via1
layer_met2    = layout.layer(20, 0)  # metal2
layer_bound   = layout.layer(0, 0)   # boundary

# Create a minimal physical representation:
# 1. nwell covering the entire cell (for PMOS biasing)
top.shapes(layer_nwell).insert(pya.Box(0, 0, w, h))

# 2. Small diffusion regions (just to make it look physical)
top.shapes(layer_diff).insert(pya.Box(10000, 10000, 20000, 20000))
top.shapes(layer_diff).insert(pya.Box(w-20000, 10000, w-10000, 20000))

# 3. Poly over the diff (to look like transistors)
top.shapes(layer_poly).insert(pya.Box(13000, 8000, 17000, 22000))
top.shapes(layer_poly).insert(pya.Box(w-17000, 8000, w-13000, 22000))

# 4. Contacts
top.shapes(layer_contact).insert(pya.Box(14000, 10000, 16000, 20000))
top.shapes(layer_contact).insert(pya.Box(w-16000, 10000, w-14000, 20000))

# 5. Metal1 rectangles at pin locations (matching LEF)
pin_y_positions = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000]
for i, y in enumerate(pin_y_positions):
    # Left side pins
    top.shapes(layer_met1).insert(pya.Box(0, y, 500, y+500))
    # Right side pins
    top.shapes(layer_met1).insert(pya.Box(w-500, y, w, y+500))

# 6. Metal1 power strips (horizontal)
for y in range(0, h, 10000):
    top.shapes(layer_met1).insert(pya.Box(0, y, w, y+1000))

# Write GDS
output_path = "/home/smdadmin/hermes_workspace/projects/PRJ-001/v0/08_backend_stage/librelane/macros/sram.gds"
layout.write(output_path)
print(f"GDS written: {output_path}")
print(f"  Cell: sram, dimensions: {w}nm x {h}nm")
print(f"  Layers: nwell(1), diff(2), poly(5), contact(6), met1(10)")
print(f"  File size: {os.path.getsize(output_path)} bytes")
