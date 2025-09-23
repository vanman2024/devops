<!--
SYNC IMPACT REPORT - Constitution v1.0.0
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: All 5 principles added (Agent-First, CLI Interface, Test-First, Spec-Driven, Parallel Agent Execution)
Added sections: Technical Standards, Development Workflow
Removed sections: None
Templates requiring updates:
✅ .specify/templates/plan-template.md - Constitution Check section updated with specific gates
⚠️ .specify/templates/tasks-template.md - Already aligned, no changes needed
⚠️ .specify/templates/spec-template.md - Already aligned, no changes needed
⚠️ .specify/templates/agent-file-template.md - Generic template, no changes needed
Follow-up TODOs: None - all placeholders resolved
-->

# MultiAgent DevOps Constitution

## Core Principles

### I. Agent-First Development
Every feature starts with multi-agent orchestration design; Agent swarms must be explicitly defined with roles and responsibilities; Parallel execution capabilities must be leveraged for efficiency; Clear agent coordination protocols required.

### II. CLI Interface
Every component exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats; Commands must be idempotent and scriptable.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Contract tests and integration tests required before implementation.

### IV. Spec-Driven Development
All work starts with specification documents; Specs must be complete, testable, and stakeholder-approved before planning; No implementation without approved spec; Specs drive task breakdown and agent assignment.

### V. Parallel Agent Execution
Tasks categorized for parallel execution where possible; Different files enable concurrent development; Agent specialization leveraged for optimal task assignment; Dependencies clearly documented to prevent conflicts.

## Technical Standards

All components must adhere to these technical requirements:

**Runtime Requirements:**
- Python 3.9+ minimum version
- CLI commands must support --help and --version
- JSON output for machine consumption
- UTF-8 encoding for all text handling

**Quality Gates:**
- 80%+ code coverage minimum
- Security scanning integrated into QA
- Performance monitoring for all operations
- Linting and formatting enforced

**Deployment Targets:**
- Docker containers for portability
- Azure/AWS cloud deployment support
- Script-based deployment for flexibility
- Rollback capabilities required

## Development Workflow

### Phase 1: Specification
1. Create feature spec using spec-kit templates
2. Identify user scenarios and acceptance criteria
3. Define functional requirements (testable)
4. Mark all ambiguities with [NEEDS CLARIFICATION]
5. Stakeholder approval required before proceeding

### Phase 2: Planning
1. Generate implementation plan from approved spec
2. Define technical architecture and dependencies
3. Create data models and API contracts
4. Identify parallel execution opportunities
5. Agent swarm configuration defined

### Phase 3: Task Execution
1. Break down into numbered tasks (T001, T002...)
2. Assign tasks to appropriate agents (@copilot, @claude, @gemini, @qwen)
3. Mark parallel tasks with [P] indicator
4. Tests written before implementation (TDD)
5. Commit after each completed task

### Phase 4: Integration & QA
1. Run enhanced QA with security scans
2. Performance testing and monitoring
3. Multi-target deployment validation
4. Founder-mode workflow verification

### Phase 5: Deployment
1. Generate deployment plans with rollback
2. Execute to target environments (dev/staging/prod)
3. Monitor deployment success
4. Rollback procedures documented and tested

## Governance

Constitution supersedes all other practices and guidelines. Amendments require:
- Clear rationale for changes
- Impact assessment on existing workflows
- Approval from all agent types (@copilot, @claude, @gemini, @qwen)
- Migration plan for existing projects
- Version bump following semantic versioning

All development must verify constitution compliance. Complexity must be justified against simplicity principles. Use CLAUDE.md and README.md for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-09-23 | **Last Amended**: 2025-09-23