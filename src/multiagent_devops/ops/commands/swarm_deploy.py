#!/usr/bin/env python3
"""ops swarm-deploy command: Deploy agent swarm for tasks with logging and rollback."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

# Ensure the repository's src directory is importable when executed via subprocess
COMMAND_PATH = Path(__file__).resolve()
SRC_ROOT = COMMAND_PATH.parents[3]
sys.path.insert(0, str(SRC_ROOT))

from multiagent_devops.models import AgentSwarm, Task


class SwarmDeployError(Exception):
    """Raised when swarm deployment cannot be completed."""


def _timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _log_event(log_path: Path, event: str, **details) -> None:
    payload = {"event": event, "timestamp": _timestamp(), **details}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _parse_tasks(tasks_file: Path) -> List[Task]:
    try:
        content = tasks_file.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - filesystem edge
        raise SwarmDeployError(f"Unable to read {tasks_file}: {exc}") from exc

    tasks: List[Task] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [") and "@" in stripped:
            try:
                task_id = stripped.split("T", maxsplit=1)[1].split()[0]
                agent_alias = stripped.split("@", maxsplit=1)[1].split()[0]
            except Exception as exc:
                raise SwarmDeployError(f"Malformed task line: {stripped}") from exc
            tasks.append(
                Task(
                    id=f"T{task_id}",
                    description=stripped,
                    assigned_agent=f"@{agent_alias}",
                )
            )

    if not tasks:
        raise SwarmDeployError("No open tasks found in tasks.md")

    return tasks


def _write_status(spec_path: Path, swarm: AgentSwarm, monitoring_url: str, log_path: Path) -> Path:
    swarm_file = spec_path / "swarm_status.json"
    data = {
        "swarm_id": swarm.id,
        "agents": swarm.agents,
        "tasks_assigned": len(swarm.tasks),
        "monitoring_url": monitoring_url,
        "status": swarm.status,
        "log_path": str(log_path),
        "updated_at": _timestamp(),
    }
    swarm_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return swarm_file


def _write_monitoring(spec_path: Path, swarm: AgentSwarm, monitoring_url: str) -> Path:
    monitoring_file = spec_path / "swarm_monitoring.json"
    metrics = {
        "heartbeat": _timestamp(),
        "monitoring_url": monitoring_url,
        "metrics": {
            "agent_count": len(swarm.agents),
            "tasks_assigned": len(swarm.tasks),
        },
        "status": swarm.status,
    }
    monitoring_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return monitoring_file


def _rollback(artefacts: Iterable[Path], log_path: Path, swarm_id: str, reason: str) -> None:
    for artefact in artefacts:
        if artefact and artefact.exists():
            try:
                artefact.unlink()
            except OSError:
                pass
    _log_event(log_path, "rollback", swarm_id=swarm_id, reason=reason)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy agent swarm for spec tasks")
    parser.add_argument("--spec-path", required=True, help="Path to spec directory")
    parser.add_argument("--agents", help="Comma-separated list of agents (default: @copilot)")
    args = parser.parse_args()

    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        print(f"Error: Spec path {spec_path} does not exist", file=sys.stderr)
        sys.exit(1)

    tasks_md = spec_path / "tasks.md"
    if not tasks_md.exists():
        print(f"Error: tasks.md not found in {spec_path}", file=sys.stderr)
        sys.exit(1)

    agents = [agent.strip() for agent in (args.agents.split(",") if args.agents else ["@copilot"])]
    print(f"Deploying swarm with agents: {agents}")

    log_path = spec_path / "swarm_log.jsonl"
    swarm_id = f"swarm-{spec_path.name}"
    _log_event(log_path, "start", swarm_id=swarm_id, agents=agents)

    status_file: Path | None = None
    monitoring_file: Path | None = None

    try:
        tasks = _parse_tasks(tasks_md)
        swarm = AgentSwarm(id=swarm_id, agents=agents, tasks=tasks, status="deployed")

        print(f"Swarm deployed: {swarm.id}")
        print(f"Tasks assigned: {len(tasks)}")

        monitoring_url = f"http://localhost:8000/monitor/{swarm.id}"
        print(f"Monitoring URL: {monitoring_url}")

        status_file = _write_status(spec_path, swarm, monitoring_url, log_path)
        monitoring_file = _write_monitoring(spec_path, swarm, monitoring_url)

        _log_event(
            log_path,
            "completed",
            swarm_id=swarm.id,
            monitoring_url=monitoring_url,
            tasks_assigned=len(tasks),
        )

        print(f"Swarm status saved to {status_file}")
        print(f"Monitoring snapshot saved to {monitoring_file}")

    except SwarmDeployError as exc:
        _log_event(log_path, "error", swarm_id=swarm_id, message=str(exc))
        _rollback([status_file, monitoring_file], log_path, swarm_id, str(exc))
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
