# DevOps Template Toolbox

Drop this repository into a project when you want lightweight CLI helpers for:

- Running QA (`devops/ops/ops qa`, `ops/commands/test.sh`)
- Building production bundles (`devops/deploy/commands/build-production.sh`)
- Deploying bundles to a directory (`devops/deploy/deploy production <path>`)

## Quick Start
```bash
# Quality checks (pytest + optional linting)
./devops/ops/ops qa

# Build a production bundle locally
./devops/deploy/commands/build-production.sh ./build/your-app --force

# Deploy bundle to a target (defaults from config/devops.toml)
./devops/deploy/deploy production ~/deploy/your-app
```

Set project-specific defaults in `config/devops.toml`. Example:
```toml
[package]
name = "your_app"
path = "src"
test_command = "pytest tests/backend -m 'not slow'"

[package.manifest]
version = "VERSION"
requirements = "requirements.txt"
install = "install.sh"
cli = "your-app"

[deploy]
target = "~/deploy/your-app"
```

The tooling assumes a Python backend (pytest) but can be extended—edit `ops/ops`
and `ops/commands/testing/run_tests.py` to add categories or change defaults.

## Solo Founder Workflow

The DevOps Template Toolbox now includes enhanced support for solo founders through the new Python CLI with spec-driven development:

### Spec-Driven Development
```bash
# Initialize a new feature spec
ops spec-init --spec-path specs/001-my-feature

# Deploy agent swarms to work on tasks
ops swarm-deploy --spec-path specs/001-my-feature --agents @copilot,@claude,@qwen

# Run comprehensive QA checks against spec requirements
ops qa --spec-path specs/001-my-feature

# Generate and execute deployment plans
ops deploy-plan --spec-path specs/001-my-feature --target docker --environment prod
```

### Agent Orchestration
- Deploy AI agent swarms to parallelize development tasks
- Monitor agent progress through centralized logging
- Coordinate multi-agent workflows with real-time status updates

### Multi-Target Deployment
- Deploy to Docker containers, cloud providers (Azure/AWS), or custom scripts
- Built-in rollback capabilities for failed deployments
- Environment-specific configurations (dev/staging/prod)

### Founder Mode
```bash
# Guided workflow for solo founders
ops founder-mode --spec-path specs/001-my-feature --mode full --auto-deploy
```

Founder mode provides step-by-step guidance through the development lifecycle, making it easy for non-experts to build, test, and deploy applications.

## Performance Monitoring

### New Features
- **Performance Monitoring**: Built-in timing and resource monitoring
- **Benchmark Operations**: I/O performance testing and validation
- **System Health Checks**: Automated disk usage and memory monitoring

### Usage
```bash
# Run performance monitoring
./ops/commands/performance-monitor.sh

# Use timing wrapper for any command
./ops/ops qa --with-timing
```

### Performance Enhancements
- Added `measure_time()` utility for operation timing
- Automatic performance threshold validation
- Resource usage monitoring and alerts
- Optimized error handling with fallback values
