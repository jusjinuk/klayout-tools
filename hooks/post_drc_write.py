#!/usr/bin/env python3
"""PostToolUse hook: suggest running DRC check after writing a .drc file."""
import sys
import json
import os


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        # Only trigger after Write/Edit of .drc files
        if tool_name not in ("Write", "Edit"):
            print(json.dumps({}))
            sys.exit(0)

        file_path = input_data.get("file_path", "")
        if not file_path.endswith(".drc"):
            print(json.dumps({}))
            sys.exit(0)

        # Look for nearby GDS files to suggest testing
        drc_dir = os.path.dirname(file_path)
        gds_dirs = []

        # Check common locations relative to the .drc file
        for pattern in ["data/gds", "../data/gds", ".", ".."]:
            candidate = os.path.join(drc_dir, pattern)
            if os.path.isdir(candidate):
                gds_files = [f for f in os.listdir(candidate) if f.endswith(".gds")]
                if gds_files:
                    gds_dirs.append((candidate, len(gds_files)))

        if gds_dirs:
            best_dir, count = gds_dirs[0]
            msg = f"DRC file written. Found {count} GDS files in {best_dir}. Consider running /drc-check to validate."
            print(json.dumps({"systemMessage": msg}))
        else:
            print(json.dumps({}))

    except Exception:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()
