# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DevOps template toolbox providing lightweight CLI helpers for Python-based projects. It offers unified interfaces for quality assurance, building, and deployment operations through both legacy script-based tools and a modern Python CLI.

## Core Commands

### New Python CLI (Primary Interface)
```bash
# Install and use the main CLI
pip install -e .
ops qa --spec-path specs/001-feature --security-scan
ops build --target ~/deploy/project
ops status
ops release minor
```

### Legacy DevOps Scripts (Template System)
```bash
# Quality checks (pytest + optional linting)
./src/multiagent_devops/ops/ops qa --spec-path PATH

# Build production bundle
./src/multiagent_devops/ops/ops build --target ~/deploy/project --force

# Verify production build works
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

# Multi-agent workflow commands
./src/multiagent_devops/ops/ops spec-init --spec-path PATH
./src/multiagent_devops/ops/ops swarm-deploy --spec-path PATH --agents @copilot,@claude
./src/multiagent_devops/ops/ops deploy-plan --spec-path PATH --target docker --environment prod
./src/multiagent_devops/ops/ops founder-mode --spec-path PATH --mode full --auto-deploy
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
- Python package name: `multiagent-devops`
- Main source in `src/multiagent_devops/` directory 
- Entry point via `[project.scripts]` as `ops = "multiagent_devops.cli:main"`
- Dual architecture: New Python CLI + Legacy template scripts
- CLI implementations in `src/multiagent_devops/ops/commands/` (Python) and `src/multiagent_devops/ops/ops` (Bash)
- Deployment scripts in `src/multiagent_devops/deploy/`

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

## Multi-Agent Coordination System

### Agent Identity: @claude (Strategic Technical Leadership)

**Primary Function**: CTO-level engineering reviewer and strategic guide
- **Architecture Decisions**: Make critical technical decisions
- **Quality Gates**: Review and validate work from other agents  
- **Integration Oversight**: Resolve complex integration issues
- **Code Quality**: Ensure consistency and best practices
- **Strategic Direction**: Guide technical direction and priorities

### Available Subagents
When needed, use the Task tool to launch specialized agents:
- `general-purpose` - Research, multi-step tasks
- `code-refactorer` - Large-scale refactoring
- `pr-reviewer` - Code review & standards
- `backend-tester` - API testing
- `integration-architect` - Multi-service integration  
- `system-architect` - Database & API design
- `security-auth-compliance` - Authentication & security
- `frontend-playwright-tester` - E2E UI testing

### Task Assignment Protocol

Check for assigned tasks in spec directories:
```bash
# Check current sprint assignments
grep "@claude" specs/*/tasks.md

# Check incomplete tasks
grep -B1 -A1 "\[ \] .*@claude" specs/*/tasks.md
```

Task format:
```markdown
- [ ] T010 @claude Design database schema architecture  
- [ ] T025 @claude Coordinate API integration testing
- [x] T031 @claude FastAPI callback server ✅
```

### Commit Standards

Every commit must follow this format:
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

### Task Completion Requirements
- ✅ **ALWAYS commit code changes when completing tasks**
- ✅ **ALWAYS mark tasks complete with `[x]` symbol** 
- ✅ **ALWAYS reference task numbers in commits**
- ❌ **NEVER leave uncommitted work**

## Strategic Vision & Improvement Areas

### Unified Spec-Component-Agent Architecture
The DevOps system is evolving toward intelligent, spec-driven development where:
- **Specs are the source of truth**: Everything derives from spec definitions
- **Components auto-install**: Based on spec requirements analysis  
- **Agents self-organize**: Tasks route to agents based on capabilities
- **Progressive enhancement**: Start minimal, scale up as needed

### Key Improvement Focus Areas
1. **Spec Analysis**: Extract requirements to auto-determine needed components
2. **Smart Agent Routing**: Match tasks to agent strengths automatically
3. **Component Discovery**: Install only what's needed based on specs
4. **Unified Monitoring**: Single dashboard for all aspects (specs/agents/components)
5. **Self-Healing**: Auto-fix common issues without human intervention

### Working with Components
Components in `/components/` directory are modular additions:
- **testing**: Multi-agent testing framework
- **agentswarm**: Agent orchestration and coordination
- Each component should provide spec templates and task templates
- Components should be discoverable and auto-installable

### Agent Capability Awareness
When assigning tasks, consider agent specializations:
- **@copilot**: Fast backend implementation, CRUD, APIs
- **@claude**: Architecture, security, integration, review
- **@codex**: Frontend UI, React, interactive features
- **@qwen**: Performance optimization, algorithms
- **@gemini**: Documentation, research, analysis

## Important Notes

- The system assumes Python backend with pytest
- All scripts use bash and require Python 3.9+
- Configuration system supports both new (pyproject.toml) and legacy (config/devops.toml) formats
- WSL environment detection and optimization included
- Git hooks available for auto-sync functionality
- Template-based system designed for copying to other projects
- Multi-agent workflow with spec-based task coordination
- Founder mode available for guided solo development workflows
- See DEVOPS_IMPROVEMENT_PLAN.md for strategic roadmap