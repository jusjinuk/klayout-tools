---
name: gds-editing
description: Use when inspecting, reading, or modifying existing GDS layout files. Covers reading GDS with KLayout Python API, extracting geometry info, and GDS-to-text conversion.
---

# GDS File Inspection and Editing

## Reading a GDS File

```python
import pya

ly = pya.Layout()
ly.read("input.gds")

# Get top cell
top = ly.top_cell()
print(f"Top cell: {top.name}")
print(f"DBU: {ly.dbu} um")
print(f"Bounding box: {top.dbbox()}")  # In um
```

## Listing Layers

```python
for li in ly.layer_indices():
    info = ly.get_info(li)
    count = 0
    for cell in ly.each_cell():
        count += cell.shapes(li).size()
    if count > 0:
        print(f"Layer {info.layer}/{info.datatype}: {count} shapes")
```

## Extracting Polygons

```python
layer_idx = ly.layer(pya.LayerInfo(68, 20))  # Metal 1
for shape in top.shapes(layer_idx).each():
    if shape.is_box():
        box = shape.box
        print(f"Box: ({box.left*ly.dbu:.3f}, {box.bottom*ly.dbu:.3f}) to ({box.right*ly.dbu:.3f}, {box.top*ly.dbu:.3f}) um")
    elif shape.is_polygon():
        poly = shape.polygon
        hull = [(p.x*ly.dbu, p.y*ly.dbu) for p in poly.each_point_hull()]
        print(f"Polygon hull: {hull}")
```

## GDS to Text Representation

For feeding GDS content into an LLM context or displaying to a user:

```python
def gds_to_text(gds_path, max_vertices=50):
    """Convert GDS to human-readable text."""
    ly = pya.Layout()
    ly.read(gds_path)
    top = ly.top_cell()
    top.flatten(True)  # Flatten hierarchy

    lines = [f"gds: {gds_path}"]
    bbox = top.dbbox()
    lines.append(f"topcell_bbox_um: ({bbox.left:.3f}, {bbox.bottom:.3f}) to ({bbox.right:.3f}, {bbox.top:.3f})")

    for li in ly.layer_indices():
        info = ly.get_info(li)
        shapes = []
        for shape in top.shapes(li).each():
            poly = shape.polygon if shape.is_polygon() else pya.Polygon(shape.box)
            hull = [(round(p.x*ly.dbu, 3), round(p.y*ly.dbu, 3)) for p in poly.each_point_hull()]
            if len(hull) <= max_vertices:
                shapes.append(hull)
        if shapes:
            lines.append(f"layer {info.layer}/{info.datatype}:")
            for i, hull in enumerate(shapes):
                pts = " ".join(f"({x},{y})" for x, y in hull)
                lines.append(f"  poly{i} hull: {pts}")

    return "\n".join(lines)
```

## Modifying a GDS File

```python
# Read, modify, write
ly = pya.Layout()
ly.read("input.gds")
top = ly.top_cell()

# Add a new shape
new_layer = ly.layer(pya.LayerInfo(68, 20))
top.shapes(new_layer).insert(pya.Box(0, 0, 10000, 5000))  # In DBU

# Delete shapes on a layer
layer_to_clear = ly.layer(pya.LayerInfo(93, 44))
top.shapes(layer_to_clear).clear()

# Write modified GDS
ly.write("output.gds")
```

## Running as KLayout Script

```bash
klayout -b -rm inspect_gds.py -- input.gds
```
