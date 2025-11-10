"""Execute dotnet format commands and handle JSON reports."""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Literal

from rich.console import Console


console = Console()
logger = logging.getLogger(__name__)


class DotnetFormatRunner:
    """Run dotnet format commands with JSON report generation."""

    def __init__(self, working_dir: str | Path):
        """Initialize runner with working directory.

        Args:
            working_dir: Path to the directory containing solution/project files
        """
        self.working_dir = Path(working_dir).resolve()
        if not self.working_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.working_dir}")

    def run_style(
        self,
        include: list[str] | None = None,
        no_restore: bool = False,
        diagnostics: list[str] | None = None,
        severity: str | None = None
    ) -> dict[str, Any]:
        """Run dotnet format style command.

        Args:
            include: List of file patterns to include
            no_restore: Skip implicit restore before formatting
            diagnostics: List of diagnostic IDs to filter (e.g., ['IDE0055', 'IDE1006'])
            severity: Severity level to filter (error, hidden, info, warn)

        Returns:
            Parsed JSON report containing violations
        """
        return self._run_format(
            command_type="style",
            include=include or ["**/*.cs"],
            no_restore=no_restore,
            diagnostics=diagnostics,
            severity=severity
        )

    def run_analyzers(
        self,
        include: list[str] | None = None,
        no_restore: bool = False,
        diagnostics: list[str] | None = None,
        severity: str | None = None
    ) -> dict[str, Any]:
        """Run dotnet format analyzers command.

        Args:
            include: List of file patterns to include
            no_restore: Skip implicit restore before formatting
            diagnostics: List of diagnostic IDs to filter (e.g., ['CA1031', 'CA2007'])
            severity: Severity level to filter (error, hidden, info, warn)

        Returns:
            Parsed JSON report containing violations
        """
        return self._run_format(
            command_type="analyzers",
            include=include or ["**/*.cs"],
            no_restore=no_restore,
            diagnostics=diagnostics,
            severity=severity
        )

    def _run_format(
        self,
        command_type: Literal["style", "analyzers"],
        include: list[str],
        no_restore: bool = False,
        diagnostics: list[str] | None = None,
        severity: str | None = None
    ) -> dict[str, Any]:
        """Run dotnet format command with JSON report.

        Args:
            command_type: Either 'style' or 'analyzers'
            include: File patterns to include
            no_restore: Skip implicit restore before formatting
            diagnostics: List of diagnostic IDs to filter
            severity: Severity level to filter (error, hidden, info, warn)

        Returns:
            Parsed JSON report

        Raises:
            subprocess.CalledProcessError: If dotnet format fails unexpectedly
        """
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            dir=self.working_dir
        ) as temp_report:
            report_path = Path(temp_report.name)

        try:
            cmd = [
                "dotnet",
                "format",
                command_type,
                "--verify-no-changes",
                "--verbosity", "quiet",
                "--report", str(report_path)
            ]

            if no_restore:
                cmd.append("--no-restore")

            if include:
                cmd.extend(["--include", *include])

            if diagnostics:
                cmd.extend(["--diagnostics", *diagnostics])

            if severity:
                cmd.extend(["--severity", severity])

            spinner_text = f"[cyan]Running dotnet format {command_type}..."

            if console.is_terminal:
                with console.status(spinner_text):
                    result = subprocess.run(
                        cmd,
                        cwd=self.working_dir,
                        capture_output=True,
                        text=True
                    )
            else:
                result = subprocess.run(
                    cmd,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True
                )

            logger.debug(f"Report path: {report_path}")
            logger.debug(f"Exit code: {result.returncode}")

            if result.stderr and result.returncode != 0 and result.returncode != 2:
                logger.warning(f"dotnet format stderr: {result.stderr}")

            if report_path.exists() and report_path.stat().st_size > 0:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                logger.debug(f"Loaded {len(report_data)} items from report")
            else:
                report_data = []
                logger.debug("Report file empty or missing, using empty list")

            return {
                "report": report_data,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        finally:
            if report_path.exists():
                try:
                    report_path.unlink()
                except Exception:
                    pass
