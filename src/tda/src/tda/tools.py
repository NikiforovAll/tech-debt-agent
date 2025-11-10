"""Tools for Technical Debt Agent - wraps tde functionality."""

import logging
from pathlib import Path
from typing import Any

from claude_agent_sdk import tool
from tde.formatter import format_as_toon
from tde.parser import parse_report
from tde.runner import DotnetFormatRunner


logger = logging.getLogger(__name__)


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
    logger.info(f"extract_style_diagnostics called for path: {args.get('path')}")
    try:
        path = Path(args["path"])
        group_by = args.get("group_by", "error")
        summary = args.get("summary", False)

        # Handle diagnostics parameter - normalize 'all' to None
        diagnostics_raw = args.get("diagnostics")
        if diagnostics_raw == "all" or diagnostics_raw == []:
            diagnostics_filter = None
        elif isinstance(diagnostics_raw, list):
            diagnostics_filter = diagnostics_raw
        else:
            diagnostics_filter = None

        # Handle severity parameter - normalize 'all' to None, validate others
        severity_raw = args.get("severity")
        valid_severities = {"info", "warn", "error", "hidden"}
        if severity_raw == "all" or not severity_raw:
            severity = None
        elif severity_raw.lower() in valid_severities:
            severity = severity_raw.lower()
        else:
            severity = None

        logger.debug(f"Normalized - diagnostics: {diagnostics_filter}, severity: {severity}")

        runner = DotnetFormatRunner(path)
        result = runner.run_style(
            include=None,
            no_restore=True,
            diagnostics=diagnostics_filter if diagnostics_filter else None,
            severity=severity
        )

        diagnostics = parse_report(result["report"], base_path=path.resolve())
        logger.info(f"Parsed {len(diagnostics)} style diagnostics")

        toon_output = format_as_toon(diagnostics, group_by=group_by, summary=summary)
        response_text = f"Style diagnostics for {path}:\n\n{toon_output}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        logger.exception("Failed to extract style diagnostics")
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
    logger.info(f"extract_analyzers_diagnostics called for path: {args.get('path')}")
    try:
        path = Path(args["path"])
        group_by = args.get("group_by", "error")
        summary = args.get("summary", False)

        # Handle diagnostics parameter - normalize 'all' to None
        diagnostics_raw = args.get("diagnostics")
        if diagnostics_raw == "all" or diagnostics_raw == []:
            diagnostics_filter = None
        elif isinstance(diagnostics_raw, list):
            diagnostics_filter = diagnostics_raw
        else:
            diagnostics_filter = None

        # Handle severity parameter - normalize 'all' to None, validate others
        severity_raw = args.get("severity")
        valid_severities = {"info", "warn", "error", "hidden"}
        if severity_raw == "all" or not severity_raw:
            severity = None
        elif severity_raw.lower() in valid_severities:
            severity = severity_raw.lower()
        else:
            severity = None

        logger.debug(f"Normalized - diagnostics: {diagnostics_filter}, severity: {severity}")

        runner = DotnetFormatRunner(path)
        result = runner.run_analyzers(
            include=None,
            no_restore=True,
            diagnostics=diagnostics_filter if diagnostics_filter else None,
            severity=severity
        )

        diagnostics = parse_report(result["report"], base_path=path.resolve())
        logger.info(f"Parsed {len(diagnostics)} analyzer diagnostics")

        toon_output = format_as_toon(diagnostics, group_by=group_by, summary=summary)
        response_text = f"Analyzer diagnostics for {path}:\n\n{toon_output}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        logger.exception("Failed to extract analyzer diagnostics")
        return {
            "content": [{
                "type": "text",
                "text": f"Error extracting analyzer diagnostics: {str(e)}"
            }],
            "is_error": True
        }
