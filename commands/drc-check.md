---
description: Run KLayout DRC check on a GDS file and report violations
argument-hint: <drc_file> <gds_file>
allowed-tools: ["Bash", "Read"]
---

# DRC Check

Run a KLayout DRC rule file against a GDS file and report the results.

## Arguments

Parse $ARGUMENTS to extract two file paths:
1. The .drc rule file path
2. The .gds file path

If only one argument is given, assume it's a .gds file and look for a .drc file in the same directory or parent directory.

## Steps

1. Verify both files exist using Bash: `test -f <path>`
2. Create a temp output path: `TMPFILE=$(mktemp /tmp/drc_check_XXXXXX.lyrdb)`
3. Run KLayout DRC:
   ```bash
   klayout -b -r <drc_file> -rd input=<gds_file> -rd output=$TMPFILE 2>&1
   ```
4. If KLayout exits with error, report the error message
5. If successful, parse the .lyrdb output:
   ```bash
   grep -oP '(?<=<name>)[^<]+' $TMPFILE | sort | uniq -c | sort -rn
   ```
6. Report results:
   - List each violation category and count
   - If zero violations: "PASS — no DRC violations found"
   - If violations found: list them with "FAIL — N violations in M categories"
7. Clean up: `rm -f $TMPFILE`
