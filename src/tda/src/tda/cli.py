"""CLI entrypoint for Technical Debt Agent."""

import anyio
import click

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

from .agent import techdebt_server


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
    """
    anyio.run(run_agent, query, cwd)


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
