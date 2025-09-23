#!/usr/bin/env python3
"""
ops spec-init command: Initialize devops for spec-kit spec
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure the repository's src directory is importable when executed via subprocess
COMMAND_PATH = Path(__file__).resolve()
SRC_ROOT = COMMAND_PATH.parents[3]
sys.path.insert(0, str(SRC_ROOT))

from multiagent_devops.models import Spec, DeploymentPlan

def main():
    parser = argparse.ArgumentParser(description="Initialize devops for spec-kit spec")
    parser.add_argument("--spec-path", required=True, help="Path to spec directory")
    args = parser.parse_args()

    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        print(f"Error: Spec path {spec_path} does not exist", file=sys.stderr)
        sys.exit(1)

    spec_md = spec_path / "spec.md"
    if not spec_md.exists():
        print(f"Error: spec.md not found in {spec_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing spec from {spec_md}")

    # Parse spec (placeholder implementation)
    try:
        spec = Spec.from_spec_file(str(spec_md))
        print(f"Spec loaded: {spec.title}")

        # Generate deployment plan
        plan = DeploymentPlan(
            target="docker",  # default
            environment="dev",
            config={"auto_rollback": True}
        )

        # Generate CI/CD pipeline (placeholder)
        ci_cd = {
            "stages": ["test", "build", "deploy"],
            "jobs": {
                "test": {"script": ["ops qa"]},
                "build": {"script": ["ops build"]},
                "deploy": {"script": ["ops deploy-plan"]}
            }
        }

        # Generate QA checks
        qa_checks = [
            "linting",
            "type_checking",
            "unit_tests",
            "integration_tests",
            "security_scan",
            "performance_test"
        ]

        print("Deployment plan generated")
        print("CI/CD pipeline configured")
        print(f"QA checks: {len(qa_checks)} configured")

        # Save plan to spec directory
        plan_file = spec_path / "deployment_plan.json"
        import json
        with open(plan_file, 'w') as f:
            json.dump({
                "deployment_plan": {
                    "target": plan.target,
                    "environment": plan.environment,
                    "config": plan.config
                },
                "ci_cd_pipeline": ci_cd,
                "qa_checks": qa_checks,
                "status": "success"
            }, f, indent=2)

        print(f"Plan saved to {plan_file}")

    except Exception as e:
        print(f"Error parsing spec: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
