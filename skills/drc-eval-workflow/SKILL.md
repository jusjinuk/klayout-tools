---
name: drc-eval-workflow
description: Use when running KLayout DRC evaluation pipelines — executing DRC rules against GDS test files, parsing results, and computing metrics.
---

# DRC Evaluation Workflow

## Running KLayout DRC in Batch Mode

```bash
klayout -b -r rule.drc -rd input=test.gds -rd output=result.lyrdb
```

- `-b`: Batch mode (no GUI)
- `-r rule.drc`: DRC rule file
- `-rd input=...`: Pass GDS input path as variable `$input`
- `-rd output=...`: Pass output path as variable `$output`

## Parsing .lyrdb Results

The `.lyrdb` file is XML (KLayout Report Database). Parse it to extract violations:

```python
import xml.etree.ElementTree as ET

def parse_lyrdb(lyrdb_path):
    """Parse KLayout RDB file and return violations by category."""
    tree = ET.parse(lyrdb_path)
    root = tree.getroot()
    violations = {}
    for cat in root.iter("category"):
        name_el = cat.find("name")
        if name_el is not None:
            name = name_el.text
            count = sum(1 for _ in cat.iter("value"))
            violations[name] = count
    return violations
```

## Evaluation Workflow

1. **Prepare:** Collect DRC rule (.drc) and test GDS files (pass/ and fail/ directories)
2. **Run:** Execute KLayout on each GDS file
3. **Parse:** Extract violation counts from each .lyrdb output
4. **Score:** Compare against ground truth (pass files should have 0 violations, fail files should have >0)
5. **Metrics:** Compute per-category F1, compile rate, and overall success

## Computing F1 Score

```python
def compute_f1(predictions, labels):
    """Compute F1 from binary predictions and labels.
    predictions: dict of {filename: {category: violation_count}}
    labels: dict of {filename: {category: 0_or_1}}
    """
    tp = fp = fn = 0
    for fname, cats in labels.items():
        for cat, label in cats.items():
            pred = 1 if predictions.get(fname, {}).get(cat, 0) > 0 else 0
            if pred == 1 and label == 1:
                tp += 1
            elif pred == 1 and label == 0:
                fp += 1
            elif pred == 0 and label == 1:
                fn += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return {"f1": f1, "precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn}
```

## Quick Single-File Check

For a quick validation of one DRC rule against one GDS file:

```bash
# Create temp output
TMPFILE=$(mktemp /tmp/drc_XXXXXX.lyrdb)
klayout -b -r my_rule.drc -rd input=test.gds -rd output=$TMPFILE
# Check if any violations found
grep -c "<value>" $TMPFILE  # 0 = no violations
```
