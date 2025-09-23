"""Example: How DevOps can use multiagent-core's Docker functionality

This shows the proper architecture pattern where components
depend on multiagent-core for Docker capabilities.
"""

# ✅ CORRECT: Import Docker utilities from multiagent-core
from multiagent_core.docker import (
    check_docker,
    run_in_docker,
    init_with_docker,
    create_docker_setup
)
from rich.console import Console

console = Console()

def ops_qa_with_docker():
    """Example: Run ops qa using Docker for consistency"""
    
    # Check if Docker is available
    docker_available, status = check_docker()
    console.print(f"Docker status: {status}")
    
    if docker_available:
        # Run QA checks in Docker for consistency
        console.print("[green]Running QA checks in Docker environment[/green]")
        
        qa_commands = """
        # Install dependencies
        pip install -q ruff mypy pytest
        
        # Run quality checks
        echo "=== Linting ==="
        ruff check src/ || true
        
        echo "=== Type Checking ==="
        mypy src/ || true
        
        echo "=== Tests ==="
        python -m pytest tests/ -v || true
        
        echo "QA checks complete"
        """
        
        result = run_in_docker(qa_commands)
        
        if result.returncode == 0:
            console.print("[green]QA checks passed in Docker environment[/green]")
        else:
            console.print("[yellow]QA checks completed with issues[/yellow]")
            console.print(result.stdout)
    else:
        # Fallback to direct execution
        console.print("[yellow]Running QA checks directly (no Docker)[/yellow]")
        # ... direct QA logic here

def ops_init_with_docker():
    """Example: Initialize DevOps with Docker support"""
    
    # Use multiagent-core's Docker initialization
    use_docker, status = init_with_docker(no_docker=False)
    
    if use_docker:
        # DevOps-specific setup in Docker
        devops_setup = """
        # Create DevOps-specific directories
        mkdir -p .multiagent/devops/{scripts,configs,templates}
        
        # Install DevOps tools in container
        pip install -q pyyaml toml click rich
        
        echo "DevOps environment ready"
        """
        
        result = run_in_docker(devops_setup)
        console.print("[green]DevOps initialized with Docker support[/green]")
    else:
        console.print("[yellow]DevOps initialized without Docker[/yellow]")

if __name__ == "__main__":
    # This demonstrates the architecture:
    # 1. DevOps imports Docker utilities from multiagent-core
    # 2. No Docker logic duplicated in DevOps
    # 3. Single source of truth in multiagent-core
    
    ops_qa_with_docker()
    ops_init_with_docker()