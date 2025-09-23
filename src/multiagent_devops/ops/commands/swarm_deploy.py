#!/usr/bin/env python3
"""
ops swarm-deploy command: Deploy agent swarm for tasks
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from multiagent_devops.models import AgentSwarm, Task

def main():
    parser = argparse.ArgumentParser(description="Deploy agent swarm for spec tasks")
    parser.add_argument("--spec-path", required=True, help="Path to spec directory")
    parser.add_argument("--agents", help="Comma-separated list of agents (default: @copilot)")
    args = parser.parse_args()

    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        print(f"Error: Spec path {args.spec_path} does not exist", file=sys.stderr)
        sys.exit(1)

    tasks_md = spec_path / "tasks.md"
    if not tasks_md.exists():
        print(f"Error: tasks.md not found in {spec_path}", file=sys.stderr)
        sys.exit(1)

    agents = args.agents.split(',') if args.agents else ["@copilot"]
    print(f"Deploying swarm with agents: {agents}")

    # Parse tasks from tasks.md (placeholder)
    tasks = []
    try:
        with open(tasks_md, 'r') as f:
            content = f.read()
            # Simple parsing - look for task lines
            for line in content.split('\n'):
                if line.strip().startswith('- [ ] T'):
                    # Extract task info (simplified)
                    parts = line.strip().split()
                    task_id = None
                    agent = "@copilot"  # default
                    for part in parts:
                        if part.startswith('T') and part[1:].isdigit():
                            task_id = part
                        elif part.startswith('@'):
                            agent = part
                    if task_id:
                        tasks.append(Task(
                            id=task_id,
                            description=line.strip(),
                            assigned_agent=agent
                        ))
    except Exception as e:
        print(f"Error parsing tasks: {e}", file=sys.stderr)
        sys.exit(1)

    if not tasks:
        print("Warning: No tasks found in tasks.md", file=sys.stderr)

    # Create swarm
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    swarm = AgentSwarm(
        id=f"swarm-{today}-{spec_path.name}",
        agents=agents,
        tasks=tasks,
        status="deployed"
    )

    print(f"Swarm deployed: {swarm.id}")
    print(f"Tasks assigned: {len(tasks)}")

    # Simulate monitoring URL
    monitoring_url = f"http://localhost:8000/monitor/{swarm.id}"
    print(f"Monitoring URL: {monitoring_url}")

    # Save swarm info
    swarm_file = spec_path / "swarm_status.json"
    with open(swarm_file, 'w') as f:
        json.dump({
            "swarm_id": swarm.id,
            "agents": swarm.agents,
            "tasks_assigned": len(tasks),
            "monitoring_url": monitoring_url,
            "status": "deployed"
        }, f, indent=2)

    print(f"Swarm status saved to {swarm_file}")

if __name__ == "__main__":
    main()