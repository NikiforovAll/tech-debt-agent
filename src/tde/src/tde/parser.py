"""Parse dotnet format JSON reports into structured diagnostics."""

import re
from pathlib import Path
from typing import Any, TypedDict


class Diagnostic(TypedDict):
    """Structure for a single code diagnostic."""
    file: str
    line: int
    col: int
    severity: str
    rule: str
    message: str


def parse_format_description(description: str) -> tuple[str, str]:
    """Parse FormatDescription to extract severity and message.

    Example: "warning IDE0055: Fix formatting" -> ("Warning", "Fix formatting")
    """
    match = re.match(r'^(\w+)\s+\w+:\s*(.+)$', description)
    if match:
        severity = match.group(1).capitalize()
        message = match.group(2)
        return severity, message
    return "Unknown", description


def parse_report(report_data: list[dict[str, Any]] | dict[str, Any], base_path: Path | None = None) -> list[Diagnostic]:
    """Parse dotnet format JSON report into diagnostics.

    Args:
        report_data: The JSON report from dotnet format (can be list or dict)
        base_path: Optional base path to make file paths relative

    Returns:
        List of diagnostics
    """
    diagnostics: list[Diagnostic] = []

    if isinstance(report_data, dict):
        documents = report_data.get("DocumentDiagnostics", [])
    else:
        documents = report_data

    for doc in documents:
        file_path = doc.get("FilePath", "")

        if base_path and file_path:
            try:
                file_path = str(Path(file_path).relative_to(base_path))
            except ValueError:
                pass

        file_changes = doc.get("FileChanges", [])

        for change in file_changes:
            format_desc = change.get("FormatDescription", "")
            severity, message = parse_format_description(format_desc)

            diagnostic: Diagnostic = {
                "file": file_path,
                "line": change.get("LineNumber", 0),
                "col": change.get("CharNumber", 0),
                "severity": severity,
                "rule": change.get("DiagnosticId", ""),
                "message": message
            }

            diagnostics.append(diagnostic)

    return diagnostics
