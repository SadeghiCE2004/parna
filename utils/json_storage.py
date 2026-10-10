"""Helpers for safely persisting JSON files."""

import json
import os
import tempfile

def write_json_atomic(filename, data):
    """Write JSON beside the destination, then replace it in one operation."""
    directory = os.path.dirname(os.path.abspath(filename))
    prefix = f".{os.path.basename(filename)}."
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix=prefix,
        suffix=".tmp",
        dir=directory,
        text=True,
    )

    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as temporary_file:
            json.dump(data, temporary_file, ensure_ascii=False, indent=2)
        os.replace(temporary_path, filename)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise
