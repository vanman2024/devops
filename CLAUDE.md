# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DevOps template toolbox providing lightweight CLI helpers for Python-based projects. It offers unified interfaces for quality assurance, building, and deployment operations through two main CLI tools: `ops` and `deploy`.

## Core Commands

### Quality Assurance & Development
```bash
# Quality checks (pytest + optional linting)
./devops/ops/ops qa

# Run backend tests only
./devops/ops/ops qa --backend

# Build production bundle
./devops/ops/ops build --target ~/deploy/project --force

# Verify production build works
./devops/ops/ops verify-prod

# Check project status
./devops/ops/ops status

# Environment diagnostics
./devops/ops/ops env doctor

# Release management
./devops/ops/ops release [patch|minor|major]
./devops/ops/ops rollback v1.2.3
```

### Deployment
```bash
# Deploy to production
./devops/deploy/deploy production ~/deploy/project

# Simple deployment
./devops/deploy/deploy simple ~/deploy/staging

# Build only
./devops/deploy/deploy build ~/test-build --force

# Export bundle
./devops/deploy/deploy export ~/export-dir
```

### Testing
- Uses pytest as the primary testing framework
- Test configurations defined in `pyproject.toml`
- Backend tests expected in `tests/backend/` or fallback to `tests/unit/` and `tests/integration/`
- Run tests via: `python3 run.py -m pytest tests/backend/ -m "not slow"`

### Code Quality
- **Linting**: `ruff check src/ --fix`
- **Formatting**: `black src/`
- **Type checking**: `mypy src/`
- Optional dependencies defined in `pyproject.toml` under `[project.optional-dependencies.dev]`

## Architecture

### Configuration System
- Primary config: `pyproject.toml` (contains project metadata, dependencies, and DevOps settings)
- Legacy fallback: `config/devops.toml`
- TOML parsing handled by embedded Python scripts using `tomllib`
- Configuration sections:
  - `[deploy]`: Target directories and staging paths
  - `[qa]`: Lint, typecheck, and test preferences
  - `[release]`: Changelog and versioning settings
  - `[env]`: Environment-specific settings (WSL detection, auto-bootstrap)

### CLI System Structure
- **ops/ops**: Main operations CLI (setup, qa, build, verify, sync, release, rollback)
- **deploy/deploy**: Deployment interface (production, simple, build, export)
- **ops/commands/**: Specialized command implementations
- **deploy/commands/**: Deployment script implementations

### Package Structure
- Python package name: `multi-agent-devops`
- Main source in `src/` directory (not currently present but expected)
- Entry point via `[project.scripts]` as `ops = "devops.cli:main"`
- Package discovery includes: `ops*`, `deploy*`, `ci*`

### Environment Management
- Automatic virtual environment detection (`.venv/` or `venv/`)
- Auto-bootstrap capability for creating virtual environments
- WSL compatibility checks and path validation
- Dependency management via pip and requirements files

### Version Management
- Semantic versioning via `pyproject.toml`
- Git tag-based releases with `v` prefix
- Conventional commits strategy for automated versioning
- Current version: 1.4.0

### Build & Deploy Pipeline
1. **QA Phase**: `ops qa` (lint, format, typecheck, test)
2. **Build Phase**: `ops build` or `deploy build` 
3. **Verification**: `ops verify-prod`
4. **Release**: `ops release [type]`
5. **Deployment**: `deploy production [target]`

## Development Workflow

1. Use `ops qa` for development-time quality checks
2. Use `ops build --target path` for testing production builds locally
3. Use `ops verify-prod` to validate production builds
4. Use `ops release` for version bumping and Git operations
5. Use `deploy production` for actual deployment operations

## Important Notes

- The system assumes Python backend with pytest
- All scripts use bash and require Python 3.9+
- Configuration system supports both new (pyproject.toml) and legacy (config/devops.toml) formats
- WSL environment detection and optimization included
- Git hooks available for auto-sync functionality
- Template-based system designed for copying to other projects