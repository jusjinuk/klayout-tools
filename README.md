# klayout-tools

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that gives Claude deep knowledge of KLayout DRC (Design Rule Checking) and GDS layout file workflows. It enables Claude to write correct DRC rules, generate and inspect GDS files, and run evaluation pipelines — all within the Claude Code CLI.

## Why This Plugin?

KLayout's DRC Ruby DSL and GDS binary format are niche domains that LLMs frequently get wrong: missing `.um` suffixes, confusing `.space()` with `.separation()`, wrong SKY130 layer numbers, forgetting boilerplate. This plugin solves that by:

1. **Teaching Claude the domain** via skills that provide syntax references, common patterns, and lookup instructions for the full KLayout documentation
2. **Automating repetitive tasks** via slash commands for running DRC checks, inspecting GDS files, and scaffolding generator scripts
3. **Providing specialized agents** that can be dispatched in parallel for DRC review, GDS analysis, documentation search, and evaluation pipelines
4. **Catching mistakes early** via hooks that validate `.drc` files before they're written and suggest running DRC checks afterward

## Plugin Architecture

```
klayout-tools/
├── .claude-plugin/plugin.json     # Plugin metadata
├── skills/                        # Domain knowledge (loaded into Claude's context)
│   ├── klayout-drc/               # KLayout DRC Ruby DSL syntax & patterns
│   ├── gds-generation/            # GDS creation with pya Python API
│   ├── gds-editing/               # GDS inspection & modification
│   └── drc-eval-workflow/         # Evaluation pipeline patterns
├── commands/                      # Slash commands (user-invocable)
│   ├── drc-check.md               # /drc-check — run KLayout DRC
│   ├── gds-inspect.md             # /gds-inspect — show GDS contents
│   └── gds-create.md              # /gds-create — scaffold generator script
├── agents/                        # Specialized worker agents
│   ├── drc-reviewer.md            # Review .drc rules for correctness
│   ├── gds-analyzer.md            # Deep GDS file analysis
│   ├── drc-doc-searcher.md        # Search KLayout docs on demand
│   └── eval-runner.md             # Run DRC eval pipelines
├── hooks/                         # Automatic validation
│   ├── hooks.json                 # Hook configuration
│   ├── validate_drc.py            # PreToolUse: validate .drc before write
│   └── post_drc_write.py          # PostToolUse: suggest /drc-check after write
└── refs/                          # Bundled quick references
    ├── klayout_drc_cheatsheet.md  # Condensed DRC DSL cheat sheet
    └── sky130_layers.md           # SKY130 layer/datatype table
```

## Features

### Skills

Skills are domain knowledge packages that Claude reads when relevant tasks arise. They do **not** embed the full KLayout documentation into context — instead, they include condensed cheat sheets and instruct Claude to search the full docs on demand via Grep.

| Skill | Trigger | What It Provides |
|-------|---------|-----------------|
| **klayout-drc** | Writing/reading `.drc` files | Ruby DSL syntax, common DRC patterns (width, space, separation, enclosure, overlap), common mistakes, reference lookup instructions |
| **gds-generation** | Creating GDS files programmatically | KLayout `pya` API for cell creation, shape insertion (Box, Polygon, Path), pass/fail test case generation patterns |
| **gds-editing** | Inspecting/modifying existing GDS files | Reading GDS with `pya.Layout`, layer enumeration, polygon extraction, GDS-to-text conversion, file modification |
| **drc-eval-workflow** | Running DRC evaluation | KLayout batch mode, `.lyrdb` XML parsing, F1 score computation, evaluation workflow patterns |

### Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/drc-check` | `/drc-check rule.drc test.gds` | Runs KLayout DRC in batch mode, parses the `.lyrdb` output, and reports violations by category |
| `/gds-inspect` | `/gds-inspect layout.gds` | Converts GDS to human-readable text showing layers, cells, polygon coordinates, and bounding boxes |
| `/gds-create` | `/gds-create my_generator` | Scaffolds a Python GDS generator script with imports, layer definitions, and shape insertion boilerplate |

### Agents

Agents are specialized workers that can be dispatched in parallel for focused tasks.

| Agent | Model | Purpose |
|-------|-------|---------|
| **drc-reviewer** | inherit | Reviews `.drc` rules against a checklist: boilerplate, layer numbers, operations, units, categories, completeness vs spec |
| **gds-analyzer** | inherit | Deep GDS analysis: layer/cell/geometry info, dimension measurement, pass vs fail comparison |
| **drc-doc-searcher** | haiku | Searches KLayout reference docs (`klayout_doc_drc_v2.txt`, `klayout_doc_layout_v2.txt`) for specific API calls and usage examples |
| **eval-runner** | inherit | Executes DRC rules against test GDS files, parses results, computes F1/accuracy metrics |

### Hooks

| Event | Hook | Behavior |
|-------|------|----------|
| **PreToolUse** | `validate_drc.py` | When Claude writes/edits a `.drc` file, validates: `source($input)` and `report()` boilerplate present, `.output()` calls exist, `.um` suffix on distance values. Warns but does not block. |
| **PostToolUse** | `post_drc_write.py` | After writing a `.drc` file, checks for nearby GDS files and suggests running `/drc-check` to validate. |

## Requirements

- **KLayout 0.28+** with `klayout` on PATH (for batch mode: `klayout -b`)
- **Python 3.8+** (for hooks)

## Installation

Install the plugin from a local path:

```bash
claude plugin add /path/to/klayout-tools
```

Or if published to a marketplace:

```bash
claude plugin add klayout-tools
```

After installation, restart Claude Code. Skills, commands, agents, and hooks will be automatically available.

## Usage Examples

### Write a DRC rule
Just ask Claude to write a DRC rule — the `klayout-drc` skill activates automatically:
```
> Write a DRC rule to check Metal1 minimum width (0.14um) and spacing (0.14um)
```

### Run a DRC check
```
> /drc-check my_rule.drc test_layout.gds
```

### Inspect a GDS file
```
> /gds-inspect layout.gds
```

### Scaffold a GDS generator
```
> /gds-create my_test_generator
```

## License

MIT
