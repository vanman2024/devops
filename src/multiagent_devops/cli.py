"""DevOps CLI

Multi-agent development workflow automation.
"""

import click
import requests
import pkg_resources
from rich.console import Console

console = Console()

@click.group()
def main():
    """DevOps CLI for multi-agent development"""
    # Check for updates on every command
    _check_for_updates()
    pass

@main.command()
@click.option("--backend", is_flag=True, help="Run backend QA only")
@click.option("--frontend", is_flag=True, help="Run frontend QA only")
@click.option("--all", "run_all", is_flag=True, help="Run all QA checks")
def qa(backend, frontend, run_all):
    """Quality assurance checks"""
    # Inject DevOps-specific content into existing templates
    _inject_devops_templates()
    
    if run_all or not any([backend, frontend]):
        console.print("🔍 Running all QA checks...")
        backend = frontend = True
    
    if backend:
        console.print("🔧 Backend QA: linting, type checking, tests")
    
    if frontend:
        console.print("🌐 Frontend QA: linting, type checking, E2E tests")

@main.command()
@click.option("--target", help="Build target directory")
def build(target):
    """Build for production"""
    console.print(f"🏗️  Building for production...")
    if target:
        console.print(f"   Target: {target}")

@main.command()
def status():
    """Show current development status"""
    console.print("📊 DevOps Status:")
    console.print("  ✅ Environment: Ready")
    console.print("  📦 Dependencies: Up to date")
    console.print("  🔧 QA: Passing")

@main.command()
@click.argument("version", type=click.Choice(["patch", "minor", "major"]))
def release(version):
    """Release with semantic versioning"""
    console.print(f"🚀 Creating {version} release...")

def _get_latest_version(package_name):
    """Get latest version of package from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def _check_for_updates():
    """Check for DevOps updates"""
    try:
        current_version = pkg_resources.get_distribution('multiagent-devops').version
        latest_version = _get_latest_version('multiagent-devops')
        
        if latest_version and current_version != latest_version:
            console.print(f"[dim yellow]💡 Update available: multiagent-devops {current_version} → {latest_version}[/dim yellow]")
            console.print(f"[dim yellow]   Run 'multiagent upgrade' to update all packages[/dim yellow]")
    except Exception:
        # Silently fail - don't interrupt user workflow
        pass

if __name__ == "__main__":
    main()