"""Agent configuration for Technical Debt Agent."""

from claude_agent_sdk import create_sdk_mcp_server

from .tools import extract_style_diagnostics, extract_analyzers_diagnostics


def create_techdebt_server():
    """Create and return the Technical Debt MCP server with tools.

    Returns:
        Configured MCP server with techdebt extraction tools
    """
    server = create_sdk_mcp_server(
        name="techdebt-tools",
        version="0.1.0",
        tools=[
            extract_style_diagnostics,
            extract_analyzers_diagnostics
        ]
    )
    return server


# Create the server instance to be used by CLI
techdebt_server = create_techdebt_server()
