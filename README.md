# klayout-tools

A Claude Code plugin for KLayout DRC (Design Rule Checking) and GDS layout file workflows.

## Features

### Skills
- **klayout-drc** — KLayout DRC Ruby DSL reference and patterns
- **gds-generation** — Create GDS files with KLayout Python API
- **gds-editing** — Inspect and modify existing GDS files
- **drc-eval-workflow** — Run DRC evaluation pipelines

### Commands
- `/drc-check <drc_file> <gds_file>` — Run KLayout DRC and report violations
- `/gds-inspect <gds_file>` — Show GDS file contents as text
- `/gds-create <name>` — Scaffold a GDS generator script

### Agents
- **drc-reviewer** — Review DRC rules for correctness
- **gds-analyzer** — Deep GDS file analysis
- **drc-doc-searcher** — Search KLayout documentation
- **eval-runner** — Run DRC evaluation pipelines

### Hooks
- Pre-write validation of .drc files
- Post-write suggestions to run DRC checks

## Requirements

- KLayout 0.28+ (with `klayout` on PATH for batch mode)
- Python 3.8+

## Installation

Add this plugin to your Claude Code marketplace or install locally.
