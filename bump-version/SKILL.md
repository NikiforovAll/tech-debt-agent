---
name: bump-version
description: This skill should be used when the user wants to bump the version number in the workspace. It updates versions across all pyproject.toml files (root, tde, and tda packages) and the CHANGELOG.md to keep them synchronized.
---

# Bump Version Skill

Update package versions and changelog across the workspace using semantic versioning.

## Purpose

Bump package versions in the uv workspace by updating all pyproject.toml files (root workspace, tde, and tda packages) and CHANGELOG.md simultaneously. This ensures all packages maintain version synchronization and changelog is updated for the release.

## When to Use

Use this skill when:
- User requests to "bump the version"
- User asks to "update version to patch/minor/major"
- User wants to increment the package version
- Version needs to be updated before a release

## Usage

Execute the `bump_version.py` script from the workspace root with the bump type:

```bash
python bump-version/scripts/bump_version.py <major|minor|patch>
```

### Bump Types

- **major**: Increment major version (1.0.0 → 2.0.0), reset minor and patch to 0
- **minor**: Increment minor version (1.0.0 → 1.1.0), reset patch to 0
- **patch**: Increment patch version (1.0.0 → 1.0.1)

### What Gets Updated

The script updates:
1. Root `pyproject.toml` (workspace) - `version` field
2. `src/tde/pyproject.toml` (Tech-Debt Extractor package) - `version` field
3. `src/tda/pyproject.toml` (Tech-Debt Agent package) - `version` field
4. `CHANGELOG.md` - Creates new version section from `[Unreleased]` content

All pyproject.toml files are kept in sync with the same version number. The CHANGELOG.md has the `[Unreleased]` section converted to a dated version section, with a new empty `[Unreleased]` section added above it.

## Examples

Bump patch version (0.1.0 → 0.1.1):
```bash
python bump-version/scripts/bump_version.py patch
```

Bump minor version (0.1.0 → 0.2.0):
```bash
python bump-version/scripts/bump_version.py minor
```

Bump major version (0.1.0 → 1.0.0):
```bash
python bump-version/scripts/bump_version.py major
```

## Workflow

1. **Before bumping**: Ensure `CHANGELOG.md` has changes documented in the `[Unreleased]` section
   - Add entries under appropriate categories (Added, Changed, Fixed, etc.)
   - Follow Keep a Changelog format

2. **Ask user for bump type**: Use `AskUserQuestion` tool to clarify which version bump to perform
   ```python
   AskUserQuestion(
       questions=[{
           "question": "Which version bump should be performed?",
           "header": "Version bump",
           "options": [
               {"label": "Patch", "description": "Bug fixes and minor changes (0.1.1 → 0.1.2)"},
               {"label": "Minor", "description": "New features, backward compatible (0.1.1 → 0.2.0)"},
               {"label": "Major", "description": "Breaking changes (0.1.1 → 1.0.0)"}
           ],
           "multiSelect": false
       }]
   )
   ```

3. **Execute script**: Run with the user-confirmed bump type
   ```bash
   python bump-version/scripts/bump_version.py <patch|minor|major>
   ```

4. **Verify changes**: Check that all files were updated correctly
   - All three pyproject.toml files should have the new version
   - CHANGELOG.md should have a new dated section for the version
   - New empty `[Unreleased]` section should be at the top

5. **Commit**: Commit the version bump changes if appropriate

## Changelog Management

The CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/) format:

- **[Unreleased]**: Work-in-progress changes (gets converted to version section when bumping)
- **Categories**: Added, Changed, Deprecated, Removed, Fixed, Security

When bumping a version, the script:
1. Finds the `[Unreleased]` section
2. Converts it to a dated version section (e.g., `## [0.1.2] - 2025-01-10`)
3. Adds a new empty `[Unreleased]` section at the top

**Important**: Always document changes in `[Unreleased]` before bumping. The bump process doesn't add changelog entries—it only converts existing unreleased entries into a versioned section.
