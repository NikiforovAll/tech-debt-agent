"""CLI entrypoint for Technical Debt Agent."""

import anyio
import click
import logging
import os

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

from .agent import techdebt_server


def setup_logging() -> str:
    """Configure logging with file and console handlers.

    Returns:
        Path to the log file
    """
    import tempfile
    from logging.handlers import RotatingFileHandler

    log_level = os.getenv("TDA_LOG_LEVEL", "INFO")
    log_dir = tempfile.gettempdir()
    log_file = os.path.join(log_dir, "tda.log")

    # Clear any existing handlers
    logging.root.handlers.clear()

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

    # Set level on handlers
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Configure root logger
    logging.root.setLevel(logging.DEBUG)  # Capture all levels
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)

    return log_file


@click.command()
@click.argument("query")
@click.option(
    "--cwd",
    type=click.Path(exists=True, file_okay=False),
    default=".",
    help="Working directory for the agent"
)
def main(query: str, cwd: str):
    """Technical Debt Agent - AI agent for codebase analysis.

    Query Claude about technical debt in your .NET projects.

    Examples:

        tda "Give me a summary of style diagnostics in ../path/to/project"

        tda "What are the most common analyzer diagnostics?" --cwd /path/to/project

    Logs are written to: {tempdir}/tda.log
    Set TDA_LOG_LEVEL environment variable to control verbosity (DEBUG, INFO, WARNING, ERROR)
    """
    log_file = setup_logging()
    os.environ['TDA_LOG_FILE'] = log_file

    anyio.run(run_agent, query, cwd)

    # Print log file location at the end
    click.echo(f"Logs: {log_file}", err=True)


async def run_agent(query: str, cwd: str):
    """Run the agent with the given query."""
    options = ClaudeAgentOptions(
        mcp_servers={"techdebt": techdebt_server},
        allowed_tools=[
            "mcp__techdebt__extract_style_diagnostics",
            "mcp__techdebt__extract_analyzers_diagnostics"
        ],
        cwd=cwd,
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(query)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        click.echo(block.text)
            elif isinstance(message, ResultMessage):
                if message.total_cost_usd:
                    click.echo(f"\n[Cost: ${message.total_cost_usd:.4f}]", err=True)


if __name__ == "__main__":
    main()
