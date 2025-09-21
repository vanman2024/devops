# Versioning

## Current Version
**multiagent-devops**: Check `pip show multiagent-devops` or [PyPI](https://pypi.org/project/multiagent-devops/)

## How It Works
This repository uses **automatic semantic versioning** based on commit messages:

- `feat:` → **minor** version bump (1.4.0 → 1.5.0)
- `fix:` → **patch** version bump (1.4.0 → 1.4.1) 
- `BREAKING CHANGE:` → **major** version bump (1.4.0 → 2.0.0)

## Examples
```bash
git commit -m "feat: add new ops command"        # → 1.4.0 → 1.5.0
git commit -m "fix: resolve qa script error"    # → 1.4.0 → 1.4.1
git commit -m "feat!: redesign ops CLI

BREAKING CHANGE: removes old commands"           # → 1.4.0 → 2.0.0
```

## Installation
```bash
# Install latest version
pip install --upgrade multiagent-devops

# Install specific version  
pip install multiagent-devops==1.4.0
```

## Release Process
1. Commit with conventional format
2. Push to main branch
3. GitHub Actions automatically creates release
4. PyPI package updated automatically

**No manual version bumping needed** - just use proper commit messages.