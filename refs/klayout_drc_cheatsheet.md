# KLayout DRC Cheat Sheet

## Boilerplate

```ruby
source($input)
report("Title", $output)
```

## Layer Input

```ruby
layer_name = input(layer_number, datatype)
```

## Boolean Operations

| Op | Meaning | Example |
|----|---------|---------|
| `&` | AND (intersection) | `a & b` |
| `\|` | OR (union) | `a \| b` |
| `-` | NOT (subtraction) | `a - b` |
| `^` | XOR | `a ^ b` |

## Geometric Checks

| Method | Usage | Description |
|--------|-------|-------------|
| `.width(d)` | `layer.width(0.14.um)` | Min width violation |
| `.space(d)` | `layer.space(0.14.um)` | Min space between same-layer shapes |
| `.separation(other, d)` | `a.separation(b, 0.5.um)` | Min separation between two layers |
| `.overlap(other, d)` | `a.overlap(b, 0.1.um)` | Min overlap between two layers |
| `.enclosing(other, d)` | `a.enclosing(b, 0.06.um)` | Min enclosure of one layer by another |
| `.isolated(d)` | `layer.isolated(0.27.um)` | Isolation (like space, but different-polygon only) |
| `.notch(d)` | `layer.notch(0.27.um)` | Notch check (same-polygon only) |

## Area/Size Checks

| Method | Usage | Description |
|--------|-------|-------------|
| `.drc(area < val)` | `layer.drc(area < 0.056.um)` | Min area check |
| `.sized(amount)` | `layer.sized(0.03.um)` | Expand/shrink (positive=expand) |
| `.sized(-amount)` | `layer.sized(-0.03.um)` | Shrink (for enclosure via subtraction) |

## Output

```ruby
violation_result.output("CATEGORY_NAME", "Description text")
```

## Common Patterns

### Width + Space
```ruby
m1 = input(68, 20)
m1.width(0.14.um).output("M1_WIDTH", "Metal1 width < 0.14um")
m1.space(0.14.um).output("M1_SPACE", "Metal1 space < 0.14um")
```

### Enclosure via Subtraction
```ruby
m1   = input(68, 20)
mcon = input(67, 44)
(mcon - m1.sized(-0.03.um)).output("MCON_ENC", "MCON enclosure by M1 < 0.03um")
```

### Overlap + Separation
```ruby
dnw = input(64, 18)
pnp = input(125, 5)
(dnw & pnp).output("DNW_PNP_OVERLAP", "DNW and PNP overlap")
dnw.separation(pnp, 5.0.um).output("DNW_PNP_SEP", "DNW to PNP sep < 5.0um")
```

### Min Area
```ruby
li1 = input(67, 20)
li1.drc(area < 0.0561.um).output("LI1_AREA", "LI1 area < 0.0561um2")
```

## Units

Always use `.um` suffix for micrometer values: `0.14.um`, `5.0.um`

## Common Mistakes

1. Forgetting `source($input)` or `report("...", $output)` boilerplate
2. Wrong layer/datatype numbers
3. Missing `.um` suffix on distance values
4. Using `.space()` when `.separation()` is needed (space = same layer, separation = two layers)
5. Not handling both overlap AND spacing for proximity checks
