---
description: Scaffold a Python GDS generator script using KLayout pya API
argument-hint: <output_script_name>
allowed-tools: ["Write", "Read", "Bash"]
---

# GDS Create

Create a Python script template for generating GDS files using KLayout's pya API.

## Arguments

Parse $ARGUMENTS to get the output script name. If no `.py` extension, add it.

## Steps

1. Load the gds-generation skill using the Skill tool: `klayout-tools:gds-generation`
2. Write the template script to the specified path using the patterns from the skill
3. The template should include:
   - Imports (pya, argparse)
   - DBU constant and um_to_dbu helper
   - Layer definitions (common SKY130 layers)
   - Main function with cell creation and shape insertion boilerplate
   - argparse for output path
   - `ly.write()` output
4. Tell the user the file was created and how to run it:
   ```
   Run with: klayout -b -rm <script_name>
   ```
