"""CLI entrypoint for Technical Debt Extractor."""

import logging
import os
import sys
from pathlib import Path

import click

from .formatter import format_as_toon
from .parser import parse_report
from .runner import DotnetFormatRunner


def setup_logging() -> str:
    """Configure logging with file and console handlers.

    Returns:
        Path to the log file
    """
    import tempfile
    from logging.handlers import RotatingFileHandler

    log_level = os.getenv("TDE_LOG_LEVEL", "WARNING")
    log_dir = tempfile.gettempdir()
    log_file = os.path.join(log_dir, "tde.log")

    # Create handlers
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )
    console_handler = logging.StreamHandler()

    # Set format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))

    # Configure root logger
    logging.root.setLevel(getattr(logging, log_level.upper(), logging.WARNING))
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)

    return log_file


@click.group()
def main():
    """Technical Debt Extractor - Run dotnet format and output diagnostics in TOON format.

    Logs are written to: {tempdir}/tde.log
    Set TDE_LOG_LEVEL environment variable to control verbosity (DEBUG, INFO, WARNING, ERROR)
    """
    setup_logging()


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--include",
    multiple=True,
    help="File patterns to include (can be specified multiple times)"
)
@click.option(
    "--group-by",
    type=click.Choice(["file", "error"]),
    default="error",
    help="Group diagnostics by 'file' or 'error' (rule ID)"
)
@click.option(
    "--summary",
    is_flag=True,
    help="Show only high-level counts instead of full details"
)
@click.option(
    "--diagnostics",
    multiple=True,
    help="Diagnostic IDs to include (can be specified multiple times, e.g., IDE0055 IDE1006)"
)
@click.option(
    "--severity",
    type=click.Choice(["error", "hidden", "info", "warn"]),
    help="Filter diagnostics by severity level"
)
def style(path: Path, include: tuple[str, ...], group_by: str, summary: bool, diagnostics: tuple[str, ...], severity: str | None):
    """Run code style analyzers and report diagnostics."""
    try:
        runner = DotnetFormatRunner(path)
        result = runner.run_style(
            include=list(include) if include else None,
            no_restore=True,
            diagnostics=list(diagnostics) if diagnostics else None,
            severity=severity
        )

        diagnostic_list = parse_report(result["report"], base_path=path.resolve())
        toon_output = format_as_toon(diagnostic_list, group_by=group_by, summary=summary)

        click.echo(toon_output)

        sys.exit(result["exit_code"])

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--include",
    multiple=True,
    help="File patterns to include (can be specified multiple times)"
)
@click.option(
    "--group-by",
    type=click.Choice(["file", "error"]),
    default="error",
    help="Group diagnostics by 'file' or 'error' (rule ID)"
)
@click.option(
    "--summary",
    is_flag=True,
    help="Show only high-level counts instead of full details"
)
@click.option(
    "--diagnostics",
    multiple=True,
    help="Diagnostic IDs to include (can be specified multiple times, e.g., CA1031 CA2007)"
)
@click.option(
    "--severity",
    type=click.Choice(["error", "hidden", "info", "warn"]),
    help="Filter diagnostics by severity level"
)
def analyzers(path: Path, include: tuple[str, ...], group_by: str, summary: bool, diagnostics: tuple[str, ...], severity: str | None):
    """Run 3rd party analyzers and report diagnostics."""
    try:
        runner = DotnetFormatRunner(path)
        result = runner.run_analyzers(
            include=list(include) if include else None,
            no_restore=True,
            diagnostics=list(diagnostics) if diagnostics else None,
            severity=severity
        )

        diagnostic_list = parse_report(result["report"], base_path=path.resolve())
        toon_output = format_as_toon(diagnostic_list, group_by=group_by, summary=summary)

        click.echo(toon_output)

        sys.exit(result["exit_code"])

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
