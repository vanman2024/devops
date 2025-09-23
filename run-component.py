#!/usr/bin/env python3
"""Run locally linked components"""
import sys
import os
from pathlib import Path

# Add component paths
COMPONENTS = {
    'agentswarm': 'components/agentswarm',
    'devops': 'components/devops',
    'testing': 'components/testing',
}

if len(sys.argv) < 2:
    print("Usage: ./run-component.py <component> [args...]")
    print(f"Available: {', '.join(COMPONENTS.keys())}")
    sys.exit(1)

component = sys.argv[1]
if component not in COMPONENTS:
    print(f"Unknown component: {component}")
    sys.exit(1)

# Add to path and run
component_path = Path(COMPONENTS[component]).resolve()
sys.path.insert(0, str(component_path))

# Import and run the component's main
if component == 'agentswarm':
    from agentswarm import main
    main.run(sys.argv[2:])
elif component == 'devops':
    from devops import main
    main.run(sys.argv[2:])
elif component == 'testing':
    from testing import main
    main.run(sys.argv[2:])
