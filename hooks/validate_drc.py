#!/usr/bin/env python3
"""PreToolUse hook: validate .drc files before writing."""
import sys
import json
import re


def validate_drc_content(content):
    """Check DRC file content for common issues. Returns list of warnings."""
    warnings = []

    if not content:
        return warnings

    # Check boilerplate
    if "source($input)" not in content:
        warnings.append("Missing source($input) at top of file")
    if not re.search(r'report\(', content):
        warnings.append("Missing report() declaration")

    # Check for .output() calls
    if ".output(" not in content:
        warnings.append("No .output() calls found — rule won't report any violations")

    # Check for .um suffix on numeric values in geometric checks
    # Look for patterns like .width(0.14) without .um
    for match in re.finditer(r'\.(width|space|separation|overlap|enclosing|isolated|notch)\(\s*(\d+\.?\d*)\s*\)', content):
        method = match.group(1)
        value = match.group(2)
        # Check if .um follows the number within the same call
        end_pos = match.end()
        snippet = content[match.start():min(end_pos + 10, len(content))]
        if ".um" not in snippet:
            warnings.append(f"Possible missing .um suffix: .{method}({value}) — should be .{method}({value}.um)")

    return warnings


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        # Only check Write and Edit operations on .drc files
        if tool_name not in ("Write", "Edit"):
            print(json.dumps({}))
            sys.exit(0)

        file_path = input_data.get("file_path", "")
        if not file_path.endswith(".drc"):
            print(json.dumps({}))
            sys.exit(0)

        # Get content to validate
        content = input_data.get("content", "") or input_data.get("new_string", "")
        if not content:
            print(json.dumps({}))
            sys.exit(0)

        warnings = validate_drc_content(content)

        if warnings:
            msg = "DRC validation warnings:\n" + "\n".join(f"  - {w}" for w in warnings)
            print(json.dumps({"systemMessage": msg}))
        else:
            print(json.dumps({}))

    except Exception as e:
        print(json.dumps({"systemMessage": f"DRC validator error: {e}"}))

    sys.exit(0)


if __name__ == "__main__":
    main()
