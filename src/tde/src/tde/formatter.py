"""Format diagnostics as TOON (Terminal Object Notation) output."""

from collections import defaultdict
from typing import Literal
from toon import encode
from .parser import Diagnostic


def format_as_toon(
    diagnostics: list[Diagnostic],
    group_by: Literal["file", "error"] = "error",
    summary: bool = False
) -> str:
    """Format diagnostics as TOON string with configurable grouping.

    Args:
        diagnostics: List of diagnostic dictionaries
        group_by: How to group diagnostics - "error" (by rule ID) or "file" (by file path)
        summary: Show only high-level counts instead of full details

    Returns:
        TOON formatted string with diagnostics grouped as specified
    """
    if not diagnostics:
        return "No diagnostics found."

    if summary:
        return _format_summary(diagnostics, group_by)

    if group_by == "error":
        return _format_grouped_by_error(diagnostics)
    else:
        return _format_grouped_by_file(diagnostics)


def _format_summary(diagnostics: list[Diagnostic], group_by: Literal["file", "error"]) -> str:
    """Format diagnostics as a summary with counts and messages."""
    if group_by == "error":
        # Group by error code with message from first occurrence
        grouped: dict[str, list[Diagnostic]] = defaultdict(list)
        for d in diagnostics:
            grouped[d["rule"]].append(d)

        summary_items = [
            {
                "key": key,
                "message": diags[0]["message"],
                "count": len(diags)
            }
            for key, diags in sorted(grouped.items())
        ]
    else:
        # Group by file - just show key and count
        file_counts: dict[str, int] = defaultdict(int)
        for d in diagnostics:
            file_counts[d["file"]] += 1

        summary_items = [
            {"key": key, "count": count}
            for key, count in sorted(file_counts.items())
        ]

    return encode(summary_items)


def _format_grouped_by_error(diagnostics: list[Diagnostic]) -> str:
    """Group diagnostics by error/rule ID with inline metadata."""
    grouped: dict[str, list[Diagnostic]] = defaultdict(list)

    for d in diagnostics:
        grouped[d["rule"]].append(d)

    output_parts = []
    for rule in sorted(grouped.keys()):
        diagnostics_for_rule = grouped[rule]

        # Get message from first occurrence and count
        message = diagnostics_for_rule[0]["message"]
        count = len(diagnostics_for_rule)

        # Create compact location entries without message
        locations = [
            {
                "location": f"{d['file']}:{d['line']},{d['col']}",
                "severity": d["severity"]
            }
            for d in diagnostics_for_rule
        ]

        # Inline header with message and count
        output_parts.append(f"{rule} ({message}, count: {count}):")
        output_parts.append(encode(locations))
        output_parts.append("")

    return "\n".join(output_parts).rstrip()


def _format_grouped_by_file(diagnostics: list[Diagnostic]) -> str:
    """Group diagnostics by file path."""
    grouped: dict[str, list[dict]] = defaultdict(list)

    for d in diagnostics:
        location = f"{d['file']}:{d['line']},{d['col']}"
        diagnostic_compact = {
            "location": location,
            "rule": d["rule"],
            "severity": d["severity"],
            "message": d["message"]
        }
        grouped[d["file"]].append(diagnostic_compact)

    output_parts = []
    for file_path in sorted(grouped.keys()):
        diagnostics_for_file = grouped[file_path]
        output_parts.append(f"{file_path}:")
        output_parts.append(encode(diagnostics_for_file))
        output_parts.append("")

    return "\n".join(output_parts).rstrip()
