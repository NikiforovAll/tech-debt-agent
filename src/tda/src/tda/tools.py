"""Tools for Technical Debt Agent - wraps tde functionality."""

from pathlib import Path
from typing import Any

from claude_agent_sdk import tool
from tde.formatter import format_as_toon
from tde.parser import parse_report
from tde.runner import DotnetFormatRunner


@tool("extract_style_diagnostics", "Extract code style diagnostics from a .NET project", {
    "path": str,
    "group_by": str,
    "summary": bool,
    "diagnostics": list[str],
    "severity": str
})
async def extract_style_diagnostics(args: dict[str, Any]) -> dict[str, Any]:
    """Extract code style diagnostics using dotnet format style.

    Args:
        args: Dictionary containing:
            - path: Directory path to the .NET project
            - group_by: How to group results ("error" or "file")
            - summary: Whether to show only summary counts
            - diagnostics: List of diagnostic IDs to filter (e.g., ["IDE0055", "IDE1006"])
            - severity: Severity level to filter (error, hidden, info, warn)

    Returns:
        Tool response with diagnostics in TOON format
    """
    try:
        path = Path(args["path"])
        group_by = args.get("group_by", "error")
        summary = args.get("summary", False)
        diagnostics_filter = args.get("diagnostics")
        severity = args.get("severity")

        runner = DotnetFormatRunner(path)
        result = runner.run_style(
            include=None,
            no_restore=True,
            diagnostics=diagnostics_filter if diagnostics_filter else None,
            severity=severity
        )

        diagnostics = parse_report(result["report"], base_path=path.resolve())
        toon_output = format_as_toon(diagnostics, group_by=group_by, summary=summary)

        return {
            "content": [{
                "type": "text",
                "text": f"Style diagnostics for {path}:\n\n{toon_output}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error extracting style diagnostics: {str(e)}"
            }],
            "is_error": True
        }


@tool("extract_analyzers_diagnostics", "Extract 3rd party analyzer diagnostics from a .NET project", {
    "path": str,
    "group_by": str,
    "summary": bool,
    "diagnostics": list[str],
    "severity": str
})
async def extract_analyzers_diagnostics(args: dict[str, Any]) -> dict[str, Any]:
    """Extract 3rd party analyzer diagnostics using dotnet format analyzers.

    Args:
        args: Dictionary containing:
            - path: Directory path to the .NET project
            - group_by: How to group results ("error" or "file")
            - summary: Whether to show only summary counts
            - diagnostics: List of diagnostic IDs to filter (e.g., ["CA1031", "CA2007"])
            - severity: Severity level to filter (error, hidden, info, warn)

    Returns:
        Tool response with diagnostics in TOON format
    """
    try:
        path = Path(args["path"])
        group_by = args.get("group_by", "error")
        summary = args.get("summary", False)
        diagnostics_filter = args.get("diagnostics")
        severity = args.get("severity")

        runner = DotnetFormatRunner(path)
        result = runner.run_analyzers(
            include=None,
            no_restore=True,
            diagnostics=diagnostics_filter if diagnostics_filter else None,
            severity=severity
        )

        diagnostics = parse_report(result["report"], base_path=path.resolve())
        toon_output = format_as_toon(diagnostics, group_by=group_by, summary=summary)

        return {
            "content": [{
                "type": "text",
                "text": f"Analyzer diagnostics for {path}:\n\n{toon_output}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error extracting analyzer diagnostics: {str(e)}"
            }],
            "is_error": True
        }
