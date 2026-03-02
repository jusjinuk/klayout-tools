---
description: Inspect a GDS file and show layers, cells, and geometry as text
argument-hint: <gds_file>
allowed-tools: ["Bash", "Read"]
---

# GDS Inspect

Show the contents of a GDS file in human-readable text format.

## Arguments

Parse $ARGUMENTS to get the GDS file path.

## Steps

1. Verify the file exists: `test -f <gds_file>`
2. Run a KLayout Python script to extract GDS info:
   ```bash
   klayout -b -rm <(cat << 'PYEOF'
   import pya
   import sys
   import os

   gds_path = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.environ.get("GDS_PATH", "")
   ly = pya.Layout()
   ly.read(gds_path)
   top = ly.top_cell()
   top.flatten(True)

   print(f"File: {gds_path}")
   print(f"Top cell: {top.name}")
   print(f"DBU: {ly.dbu} um")
   bbox = top.dbbox()
   print(f"Bounding box: ({bbox.left:.3f}, {bbox.bottom:.3f}) to ({bbox.right:.3f}, {bbox.top:.3f}) um")
   print()

   for li in ly.layer_indices():
       info = ly.get_info(li)
       shapes_list = []
       for shape in top.shapes(li).each():
           if shape.is_box():
               b = shape.box
               shapes_list.append(f"  Box: ({b.left*ly.dbu:.3f}, {b.bottom*ly.dbu:.3f}) to ({b.right*ly.dbu:.3f}, {b.top*ly.dbu:.3f})")
           elif shape.is_polygon():
               poly = shape.polygon
               pts = [(round(p.x*ly.dbu, 3), round(p.y*ly.dbu, 3)) for p in poly.each_point_hull()]
               shapes_list.append(f"  Polygon: {pts}")
       if shapes_list:
           print(f"Layer {info.layer}/{info.datatype} ({len(shapes_list)} shapes):")
           for s in shapes_list[:20]:  # Limit output
               print(s)
           if len(shapes_list) > 20:
               print(f"  ... and {len(shapes_list) - 20} more shapes")
   PYEOF
   ) -- <gds_file>
   ```
3. Present the output to the user
