# Quick Start Guide

Get started with Technical Debt Agent in minutes.

## Setup

```bash
# Clone the repository
cd techdebt-agent

# Install dependencies
uv sync

# Verify installation
uv run --package tde tde --help
uv run --package tda tda --help
```

## TDE - Tech Debt Extractor

Direct extraction of code diagnostics.

### Basic Usage

```bash
# Extract style diagnostics (default: grouped by error)
uv run --package tde tde style ../path/to/project

# Extract analyzer diagnostics
uv run --package tde tde analyzers ../path/to/project
```

### Grouping Options

```bash
# Group by error code (default)
uv run --package tde tde style ../path/to/project --group-by error

# Group by file
uv run --package tde tde style ../path/to/project --group-by file
```

### Summary Mode

```bash
# Show only high-level counts
uv run --package tde tde style ../path/to/project --summary

# Summary grouped by file
uv run --package tde tde analyzers ../path/to/project --summary --group-by file
```

### File Filtering

```bash
# Include specific patterns
uv run --package tde tde style ../path/to/project --include "**/*.cs"

# Multiple includes
uv run --package tde tde style ../path/to/project \
  --include "Controllers/**/*.cs" \
  --include "Services/**/*.cs"
```

### Diagnostic Filtering

```bash
# Filter to specific diagnostic IDs (style)
uv run --package tde tde style ../path/to/project --diagnostics IDE0055

# Multiple diagnostics
uv run --package tde tde style ../path/to/project \
  --diagnostics IDE0055 \
  --diagnostics IDE1006

# Filter analyzer diagnostics
uv run --package tde tde analyzers ../path/to/project \
  --diagnostics CA1031 \
  --diagnostics CA2007

# Combine with other options
uv run --package tde tde style ../path/to/project \
  --diagnostics IDE0055 \
  --summary \
  --group-by file
```

### Severity Filtering

```bash
# Filter by severity level (style)
uv run --package tde tde style ../path/to/project --severity error

# Filter analyzer diagnostics by severity
uv run --package tde tde analyzers ../path/to/project --severity warn

# Combine severity with other filters
uv run --package tde tde style ../path/to/project \
  --severity error \
  --diagnostics IDE0055 \
  --summary

# Available severity levels: error, hidden, info, warn
uv run --package tde tde analyzers ../path/to/project --severity info
```

### Example Output

**Grouped by error (default):**
```
IDE0055:
{key,message,count}: IDE0055,Fix formatting,2
[2,]{location,severity}:
 Controllers/ValuesController.cs:10,45,Warning
 Services/Calculator.cs:7,13,Warning

CA1031:
{key,message,count}: CA1031,Do not catch general exception types,1
[1,]{location,severity}:
 Models/User.cs:25,5,Warning
```

**Summary mode (grouped by error - default):**
```
[3,]{key,message,count}:
 CA1031,Do not catch general exception types,5
 IDE0055,Fix formatting,12
 IDE1006,Naming rule violation,3
```

**Summary mode (grouped by file):**
```
[2,]{key,count}:
 Controllers/ValuesController.cs,8
 Services/Calculator.cs,5
```

## TDA - Tech Debt Agent

AI-powered conversational analysis using Claude.

### Basic Queries

```bash
# Ask for summary
uv run --package tda tda "Give me a summary of style diagnostics in ../path/to/project"

# Ask about specific issues
uv run --package tda tda "What are the most common analyzer diagnostics in ../path/to/project?"

# Ask for recommendations
uv run --package tda tda "Which files have the most style issues in ../path/to/project?"
```

### Using Working Directory

```bash
# Set working directory
uv run --package tda tda "Give me a summary of style diagnostics" --cwd ../path/to/project

# Compare different diagnostic types
uv run --package tda tda \
  "Compare style vs analyzer diagnostics and tell me which should be prioritized" \
  --cwd ../path/to/project
```

### Advanced Queries

```bash
# Request specific grouping
uv run --package tda tda \
  "Show me analyzer diagnostics grouped by file" \
  --cwd ../path/to/project

# Request summary
uv run --package tda tda \
  "Give me a high-level summary of all diagnostics" \
  --cwd ../path/to/project

# Analytical questions
uv run --package tda tda \
  "Which diagnostic rules appear most frequently and what do they mean?" \
  --cwd ../path/to/project
```

## Common Workflows

### 1. Initial Codebase Assessment

```bash
# Get high-level overview
uv run --package tde tde style ../my-project --summary
uv run --package tde tde analyzers ../my-project --summary

# Or use agent for interpretation
uv run --package tda tda \
  "Analyze the codebase and give me a summary of the most critical issues" \
  --cwd ../my-project
```

### 2. Deep Dive into Specific Files

```bash
# Extract diagnostics grouped by file
uv run --package tde tde style ../my-project --group-by file

# Filter to specific areas
uv run --package tde tde style ../my-project \
  --group-by file \
  --include "Controllers/**/*.cs"
```

### 3. Pre-Commit Checks

```bash
# Quick style check
uv run --package tde tde style . --summary

# Exit codes: 0 = no issues, 2 = issues found, 1 = error
# Useful for CI/CD pipelines
```

### 4. AI-Assisted Analysis

```bash
# Get recommendations
uv run --package tda tda \
  "What should I focus on first to improve code quality?" \
  --cwd ../my-project

# Understand specific diagnostics
uv run --package tda tda \
  "Explain what IDE0055 means and show me examples from the codebase" \
  --cwd ../my-project
```

## Understanding TOON Output

TOON (Terminal Object Notation) is optimized for LLM consumption with 30-60% fewer tokens than JSON.

**Format structure:**
```
[count,]{column1,column2,...}:
 value1,value2,...
 value1,value2,...
```

**Key benefits:**
- Compact and readable
- Type information preserved
- Easy to parse programmatically
- Efficient for token-constrained contexts

## Tips

1. **Use `--summary` first** to get overview before diving into details
2. **Group by file** when you want to focus on specific components
3. **Group by error** (default) to understand patterns across codebase
4. **Use TDA for questions** that require interpretation or recommendations
5. **Use TDE for raw data** when you need structured output for processing

## Troubleshooting

**"Directory not found" error:**
```bash
# Ensure path exists and is a directory (not a file)
ls ../path/to/project
```

**No diagnostics found:**
```bash
# Verify dotnet format is installed
dotnet format --version

# Ensure the directory contains a .NET solution or project
ls ../path/to/project/*.sln
```

**Agent not responding:**
```bash
# Ensure ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY

# Check you have API credits available
```

## Next Steps

- Read [CLAUDE.md](CLAUDE.md) for architecture details
- See [README.md](README.md) for installation and overview
- Explore the source code in `src/tde/` and `src/tda/`
