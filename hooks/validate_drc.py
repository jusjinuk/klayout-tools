#!/usr/bin/env python3
"""PreToolUse hook: validate .drc files and inject relevant KLayout docs."""
import sys
import json
import re
import os


# DRC operations we know how to look up
DRC_OPERATIONS = {
    "width", "space", "separation", "overlap", "enclosing",
    "isolated", "notch", "sized", "drc", "input", "output",
    "covering", "interacting", "inside", "outside", "not_covering",
    "not_interacting", "not_inside", "not_outside",
    "area", "perimeter", "bbox_min", "bbox_max",
    "edges", "corners", "extended", "hulls", "merged",
    "angle", "length", "centers", "start_segments", "end_segments",
    "with_area", "without_area", "with_perimeter", "without_perimeter",
    "rectangles", "rectilinear", "non_rectangles", "non_rectilinear",
    "enc", "enclosed", "iso", "sep", "notch",
}


def find_ref_doc():
    """Find the bundled klayout_docs_v2.txt reference."""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if plugin_root:
        path = os.path.join(plugin_root, "refs", "klayout_docs_v2.txt")
        if os.path.isfile(path):
            return path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "..", "refs", "klayout_docs_v2.txt")
    if os.path.isfile(path):
        return path
    return None


def extract_operations(content):
    """Extract DRC operation names used in the .drc content."""
    ops = set()
    for match in re.finditer(r'\.(\w+)\s*\(', content):
        name = match.group(1)
        if name in DRC_OPERATIONS:
            ops.add(name)
    for match in re.finditer(r'(?<!\.)(\w+)\s*\(', content):
        name = match.group(1)
        if name in DRC_OPERATIONS:
            ops.add(name)
    return ops


def extract_doc_sections(ref_path, operations):
    """Extract full doc sections for each operation from the reference file.

    Sections start with '## "operation_name" - ...' and end at the next '## '.
    Returns only sections from the Layer Object part (more useful than DRC expr).
    """
    with open(ref_path, "r") as f:
        lines = f.readlines()

    sections = {}
    for op in operations:
        # Find all section headers matching this operation
        pattern = re.compile(rf'^## "{re.escape(op)}" - ', re.IGNORECASE)
        for i, line in enumerate(lines):
            if pattern.match(line):
                # Extract until next ## heading
                block = [line.rstrip()]
                for j in range(i + 1, min(i + 40, len(lines))):
                    if lines[j].startswith("## "):
                        break
                    block.append(lines[j].rstrip())
                # Keep the longest (most detailed) section for each op
                text = "\n".join(block).strip()
                if op not in sections or len(text) > len(sections[op]):
                    sections[op] = text

    return sections


def validate_drc_content(content):
    """Check DRC file content for common issues. Returns list of warnings."""
    warnings = []
    if not content:
        return warnings

    if "source($input)" not in content:
        warnings.append("Missing source($input) at top of file")
    if not re.search(r'report\(', content):
        warnings.append("Missing report() declaration")
    if ".output(" not in content:
        warnings.append("No .output() calls found — rule won't report any violations")

    for match in re.finditer(
        r'\.(width|space|separation|overlap|enclosing|isolated|notch)\(\s*(\d+\.?\d*)\s*\)',
        content
    ):
        method = match.group(1)
        value = match.group(2)
        end_pos = match.end()
        snippet = content[match.start():min(end_pos + 10, len(content))]
        if ".um" not in snippet:
            warnings.append(
                f"Possible missing .um suffix: .{method}({value})"
                f" — should be .{method}({value}.um)"
            )

    return warnings


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        if tool_name not in ("Write", "Edit"):
            print(json.dumps({}))
            sys.exit(0)

        file_path = input_data.get("file_path", "")
        if not file_path.endswith(".drc"):
            print(json.dumps({}))
            sys.exit(0)

        content = input_data.get("content", "") or input_data.get("new_string", "")
        if not content:
            print(json.dumps({}))
            sys.exit(0)

        parts = []

        # 1. Validate
        warnings = validate_drc_content(content)
        if warnings:
            parts.append(
                "DRC validation warnings:\n"
                + "\n".join(f"  - {w}" for w in warnings)
            )

        # 2. Auto-lookup relevant doc sections
        ref_path = find_ref_doc()
        if ref_path:
            operations = extract_operations(content)
            # Skip trivial ops that don't need doc lookup
            operations.discard("input")
            operations.discard("output")
            if operations:
                sections = extract_doc_sections(ref_path, operations)
                if sections:
                    doc_text = "\n\n".join(
                        sections[op] for op in sorted(sections)
                    )
                    parts.append(
                        "KLayout reference for operations in this .drc file:\n\n"
                        + doc_text
                    )

        if parts:
            print(json.dumps({"systemMessage": "\n\n".join(parts)}))
        else:
            print(json.dumps({}))

    except Exception as e:
        print(json.dumps({"systemMessage": f"DRC hook error: {e}"}))

    sys.exit(0)


if __name__ == "__main__":
    main()
