#!/usr/bin/env python3
"""
ops deploy-plan command: Create and execute deployment plan
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from multiagent_devops.models import DeploymentPlan

def main():
    parser = argparse.ArgumentParser(description="Create and execute deployment plan")
    parser.add_argument("--spec-path", required=True, help="Path to spec directory")
    parser.add_argument("--target", required=True, choices=["docker", "azure", "aws", "script"],
                       help="Deployment target")
    parser.add_argument("--environment", required=True, choices=["dev", "staging", "prod"],
                       help="Target environment")
    args = parser.parse_args()

    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        print(f"Error: Spec path {spec_path} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Creating deployment plan for {args.target} in {args.environment}")

    # Create deployment plan
    plan = DeploymentPlan(
        target=args.target,
        environment=args.environment,
        config={
            "rollback_enabled": True,
            "auto_scale": args.environment == "prod",
            "monitoring": True
        }
    )

    print(f"Plan created: {plan.target} -> {plan.environment}")

    # Generate target-specific config
    if plan.target == "docker":
        config = {
            "image": f"myapp:{spec_path.name}",
            "ports": ["8000:8000"],
            "volumes": ["/data"],
            "environment": {
                "ENV": plan.environment,
                "DEBUG": "true" if plan.environment == "dev" else "false"
            }
        }
    elif plan.target == "azure":
        config = {
            "resource_group": f"rg-{spec_path.name}-{plan.environment}",
            "app_service_plan": "B1",
            "runtime": "python:3.9",
            "environment_variables": {
                "ENV": plan.environment
            }
        }
    elif plan.target == "aws":
        config = {
            "region": "us-east-1",
            "instance_type": "t3.micro",
            "ami": "ami-12345678",
            "security_groups": [f"sg-{spec_path.name}"]
        }
    else:  # script
        config = {
            "script_path": "deploy/production/deploy.sh",
            "rollback_script": "deploy/production/rollback.sh"
        }

    # Save deployment plan
    plan_file = spec_path / "deployment_execution.json"
    with open(plan_file, 'w') as f:
        json.dump({
            "deployment_id": f"deploy-{spec_path.name}-{plan.environment}",
            "target_config": config,
            "rollback_plan": {
                "enabled": plan.rollback_enabled,
                "backup_strategy": "snapshot",
                "rollback_timeout": 300
            },
            "status": "planned"
        }, f, indent=2)

    print(f"Deployment plan saved to {plan_file}")
    print("Ready for execution")

if __name__ == "__main__":
    main()