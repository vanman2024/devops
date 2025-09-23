# DevOps Project Context for Qwen Code

## Project Overview

This is a DevOps template toolbox providing lightweight CLI helpers for Python-based projects. It offers unified interfaces for quality assurance, building, and deployment operations through both legacy script-based tools and a modern Python CLI.

The project is designed as a multi-agent development workflow automation system with the following key features:
- Quality assurance checks (linting, type checking, testing)
- Production build system
- Deployment automation
- Semantic versioning
- Multi-agent coordination system
- Performance monitoring capabilities

## Project Type
**Python-based DevOps Automation Tool**

This is a Python project using setuptools for packaging. The main package is `multiagent-devops` which provides CLI tools for development operations.

## Core Technologies
- **Language**: Python 3.9+
- **Package Management**: pip, setuptools
- **CLI Framework**: Click
- **Dependencies**: 
  - click>=8.0.0
  - rich>=10.0.0
  - pyyaml>=6.0
  - toml>=0.10.2
  - requests>=2.25.0
- **Testing**: pytest
- **Code Quality**: black, flake8, mypy

## Project Structure
```
devops/
├── src/multiagent_devops/      # Main Python package
│   ├── cli.py                  # Main CLI entry point
│   ├── ops/                    # Operations CLI system
│   │   ├── ops                 # Main operations CLI script
│   │   └── commands/           # Specialized command implementations
│   ├── deploy/                 # Deployment system
│   │   ├── deploy              # Deployment interface
│   │   └── commands/           # Deployment script implementations
│   ├── models/                 # Data models
│   ├── scripts/                # Utility scripts
│   └── __init__.py
├── components/                 # Linked components
│   ├── agentswarm/
│   └── testing/
├── specs/                      # Specification directories
│   └── 001-copilot-or-claude/
├── pyproject.toml              # Project configuration
├── README.md                   # Project documentation
├── CLAUDE.md                   # Development instructions
├── VERSION                     # Current version info
├── VERSIONS.md                 # Versioning documentation
└── run-component.py            # Component runner
```

## Building and Running

### Installation
```bash
# Install in development mode
pip install -e .

# Install latest version
pip install --upgrade multiagent-devops
```

### Core Commands

#### New Python CLI (Primary Interface)
```bash
# Quality assurance checks
ops qa

# Build for production
ops build --target ~/deploy/project

# Show current development status
ops status

# Create semantic version release
ops release [patch|minor|major]
```

#### Legacy DevOps Scripts (Template System)
```bash
# Quality checks
./src/multiagent_devops/ops/ops qa --spec-path PATH

# Build production bundle
./src/multiagent_devops/ops/ops build --target ~/deploy/project --force

# Verify production build
./src/multiagent_devops/ops/ops verify-prod

# Check project status
./src/multiagent_devops/ops/ops status

# Environment diagnostics
./src/multiagent_devops/ops/ops env doctor

# Security scans
./src/multiagent_devops/ops/ops security --all

# Release management
./src/multiagent_devops/ops/ops release [patch|minor|major]
./src/multiagent_devops/ops/ops rollback v1.2.3
```

### Testing
```bash
# Run tests with pytest
pytest tests/

# Run tests with specific markers
pytest tests/ -m "not slow"

# Run tests via the ops CLI
ops qa
```

### Code Quality
```bash
# Linting
ruff check src/ --fix

# Formatting
black src/

# Type checking
mypy src/
```

## Development Conventions

### Version Management
The project uses automatic semantic versioning based on commit messages:
- `feat:` → minor version bump (1.4.0 → 1.5.0)
- `fix:` → patch version bump (1.4.0 → 1.4.1)
- `BREAKING CHANGE:` → major version bump (1.4.0 → 2.0.0)

### Commit Standards
Every commit should follow this format:
```bash
git commit -m "[WORKING] feat: Add authentication system

Related to #123

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: @qwen <noreply@anthropic.com>
Co-Authored-By: @gemini <noreply@anthropic.com>
Co-Authored-By: @codex <noreply@anthropic.com>
Co-Authored-By: @copilot <noreply@anthropic.com>"
```

**State Markers:**
- `[STABLE]` - Production ready, fully tested
- `[WORKING]` - Functional but needs more testing
- `[WIP]` - Work in progress, may have issues
- `[HOTFIX]` - Emergency fix

### Multi-Agent Coordination
The project supports multi-agent workflows with spec-based task coordination:
- Task assignments are tracked in spec directories
- Use `@claude`, `@qwen`, `@gemini`, etc. to assign tasks
- Tasks should be marked as complete with `[x]` symbol

### Performance Monitoring
The system includes built-in performance monitoring capabilities:
- Timing wrapper for any command with `--with-timing`
- Resource usage monitoring and alerts
- I/O performance testing and validation
- System health checks for disk usage and memory

## Configuration
Primary configuration is in `pyproject.toml` which contains:
- Project metadata and dependencies
- DevOps settings in various sections:
  - `[deploy]`: Target directories and staging paths
  - `[qa]`: Lint, typecheck, and test preferences
  - `[release]`: Changelog and versioning settings
  - `[env]`: Environment-specific settings

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
- Template-based system designed for copying to other projects
- Multi-agent workflow with spec-based task coordination
- Founder mode available for guided solo development workflows