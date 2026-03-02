---
name: gds-generation
description: Use when creating GDS layout files programmatically using KLayout's Python API (pya module). Covers cell creation, shape insertion, and file output.
---

# GDS File Generation with KLayout Python API

## Running KLayout Python Scripts

```bash
klayout -b -rm script.py                    # Run script in batch mode
klayout -b -rm script.py -- --arg1 val1     # With arguments (after --)
```

## Minimal GDS Generator Template

```python
import pya
import argparse

DBU_UM = 0.001  # Database unit: 1 nm

def um_to_dbu(um_val):
    """Convert micrometers to database units."""
    return round(um_val / DBU_UM)

def main():
    ly = pya.Layout()
    ly.dbu = DBU_UM
    top = ly.create_cell("TOP")

    # Define layers
    li_met1 = ly.layer(pya.LayerInfo(68, 20))   # Metal 1
    li_via  = ly.layer(pya.LayerInfo(68, 44))    # Via

    # Insert shapes (coordinates in DBU = nm)
    x0, y0 = um_to_dbu(0), um_to_dbu(0)
    x1, y1 = um_to_dbu(10), um_to_dbu(5)
    top.shapes(li_met1).insert(pya.Box(x0, y0, x1, y1))

    # Write output
    ly.write("output.gds")

if __name__ == "__main__":
    main()
```

## Key Concepts

- **Database unit (DBU):** GDS coordinates are integers in DBU. With `dbu = 0.001`, 1 DBU = 1 nm.
- **`um_to_dbu()`:** Always convert micrometer design values to integer DBU before creating shapes.
- **Layer info:** `pya.LayerInfo(layer_number, datatype)` — see SKY130 layer reference.
- **Shapes:** Use `pya.Box(x1, y1, x2, y2)` for rectangles, `pya.Polygon` for arbitrary polygons.

## Shape Types

```python
# Rectangle (Box)
top.shapes(layer).insert(pya.Box(x0, y0, x1, y1))

# Polygon (arbitrary shape)
pts = [pya.Point(x0, y0), pya.Point(x1, y0), pya.Point(x1, y1), pya.Point(x0, y1)]
top.shapes(layer).insert(pya.Polygon(pts))

# Path (wire)
pts = [pya.Point(x0, y0), pya.Point(x1, y1)]
top.shapes(layer).insert(pya.Path(pts, width_dbu))
```

## Generating Pass/Fail DRC Test Cases

For DRC testing, generate two sets of GDS files:

- **Pass cases:** Geometries that satisfy all design rules (sufficient spacing, width, etc.)
- **Fail cases:** Geometries that intentionally violate specific rules

```python
def generate_pass_case(ly, top, layer, min_width_um, min_space_um):
    """Two rectangles with sufficient width and spacing."""
    w = um_to_dbu(min_width_um * 1.5)  # 50% margin
    s = um_to_dbu(min_space_um * 1.5)
    h = um_to_dbu(2.0)
    top.shapes(layer).insert(pya.Box(0, 0, w, h))
    top.shapes(layer).insert(pya.Box(w + s, 0, 2*w + s, h))

def generate_fail_case(ly, top, layer, min_width_um, min_space_um):
    """Two rectangles with insufficient spacing."""
    w = um_to_dbu(min_width_um * 1.5)
    s = um_to_dbu(min_space_um * 0.5)  # 50% of minimum = violation
    h = um_to_dbu(2.0)
    top.shapes(layer).insert(pya.Box(0, 0, w, h))
    top.shapes(layer).insert(pya.Box(w + s, 0, 2*w + s, h))
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Float coordinates | Always convert to int DBU with `um_to_dbu()` |
| Forgetting `ly.dbu = DBU_UM` | Set DBU before creating shapes |
| Using wrong layer numbers | Check SKY130 layer reference |
| Shapes at origin overlapping | Offset shapes to avoid unintended intersections |
