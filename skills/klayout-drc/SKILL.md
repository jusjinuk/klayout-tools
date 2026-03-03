---
name: klayout-drc
description: Use when writing, reading, or understanding KLayout DRC rules (.drc files). Provides KLayout Ruby DSL syntax, common DRC patterns, and reference lookup instructions.
---

# KLayout DRC Rule Writing

## Reference Documentation

The plugin bundles the full KLayout DRC + Layout reference (3.7K lines). Find it by running:

```bash
find ~ -path "*/klayout-tools/refs/klayout_docs_v2.txt" -print -quit
```

Use `Grep` to search for specific operations (e.g., `separation`, `enclosing`, `sized`) and `Read` with line offsets to get surrounding context. Do NOT load the full file into context at once.

For SKY130 layer numbers, read the bundled reference:

```bash
find ~ -path "*/klayout-tools/refs/sky130_layers.md" -print -quit
```

## DRC File Template

Every .drc file must have this structure:

```ruby
source($input)
report("DRC Rule Title", $output)

# Layer inputs
layer_a = input(LAYER_NUM, DATATYPE)
layer_b = input(LAYER_NUM, DATATYPE)

# Rules — each outputs violations to a named category
layer_a.width(MIN_WIDTH.um).output("CATEGORY_NAME", "Description")
```

## Key Rules

1. **Always include** `source($input)` and `report("Title", $output)` at the top
2. **Use `.um` suffix** on all distance values: `0.14.um`, `5.0.um`
3. **Layer input** uses GDS layer number and datatype: `input(68, 20)` for met1
4. **Every check** must end with `.output("CATEGORY", "description")`
5. **Space vs separation:** `.space()` is same-layer, `.separation()` is cross-layer
6. **Overlap + separation:** For proximity rules, check BOTH overlap (`&`) AND spacing

## Common Patterns

### Width + Space (single layer)
```ruby
m1 = input(68, 20)
m1.width(0.14.um).output("M1_WIDTH_LT_0p14um", "Metal1 width < 0.14um")
m1.space(0.14.um).output("M1_SPACE_LT_0p14um", "Metal1 space < 0.14um")
```

### Enclosure (layer A must enclose layer B by minimum distance)
```ruby
m1   = input(68, 20)
mcon = input(67, 44)
# Shrink m1, then check if mcon extends beyond shrunk boundary
(mcon - m1.sized(-0.03.um)).output("MCON_M1_ENC_LT_0p03um", "MCON enclosure by M1 < 0.03um")
```

### Overlap + Separation (two layers must not be too close)
```ruby
dnw = input(64, 18)
pnp = input(125, 5)
(dnw & pnp).output("DNW_PNP_OVERLAP", "DNW and PNP overlap")
dnw.separation(pnp, 5.0.um).output("DNW_PNP_SEP", "DNW to PNP sep < 5.0um")
```

### Minimum Area
```ruby
li1 = input(67, 20)
li1.drc(area < 0.0561.um).output("LI1_AREA_LT_0p0561um2", "LI1 area < 0.0561um2")
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `source($input)` | Add at top of file |
| Missing `.um` suffix | `0.14` → `0.14.um` |
| Using `space` for cross-layer | Use `separation` instead |
| Only checking spacing, not overlap | Add `(a & b).output(...)` for overlap case |
| Wrong layer/datatype numbers | Check SKY130 layer reference |
