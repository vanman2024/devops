# Tasks: MultiAgent DevOps Solo Founder Integration

**Input**: Design documents from `/home/vanman2025/Projects/devops/specs/001-copilot-or-claude/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [ ] T001 @copilot Analyze current multiagent-devops structure in src/multiagent_devops/ops/
- [ ] T002 @copilot Add any new dependencies to pyproject.toml if needed
- [ ] T003 [P] @copilot Configure linting and formatting tools (black, flake8)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] @claude Contract test for ops-spec-init command in tests/contract/test_ops_spec_init.py
- [x] T005 [P] @qwen Contract test for ops-swarm-deploy command in tests/contract/test_ops_swarm_deploy.py ✅
- [ ] T006 [P] @codex Contract test for ops-qa command in tests/contract/test_ops_qa.py
- [x] T007 [P] @qwen Contract test for ops-deploy-plan command in tests/contract/test_ops_deploy_plan.py ✅
- [ ] T008 [P] @codex Integration test for spec parsing and plan generation in tests/integration/test_spec_init.py
- [x] T009 [P] @qwen Integration test for agent swarm deployment in tests/integration/test_swarm_deploy.py ✅
- [ ] T010 [P] @codex Integration test for QA validation in tests/integration/test_qa_validation.py
- [x] T011 [P] @qwen Integration test for deployment with rollback in tests/integration/test_deployment.py ✅

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T012 [P] @copilot Create Spec model in src/multiagent_devops/models/spec.py
- [ ] T013 [P] @copilot Create Task model in src/multiagent_devops/models/task.py
- [ ] T014 [P] @copilot Create AgentSwarm model in src/multiagent_devops/models/agent_swarm.py
- [ ] T015 [P] @copilot Create DeploymentPlan model in src/multiagent_devops/models/deployment_plan.py
- [ ] T016 [P] @copilot Create QAReport model in src/multiagent_devops/models/qa_report.py
- [ ] T017 @copilot Implement ops spec-init command in src/multiagent_devops/ops/commands/spec_init.py
- [ ] T018 @copilot Implement ops swarm-deploy command in src/multiagent_devops/ops/commands/swarm_deploy.py
- [ ] T019 @copilot Implement ops qa command in src/multiagent_devops/ops/commands/qa.py
- [ ] T020 @copilot Implement ops deploy-plan command in src/multiagent_devops/ops/commands/deploy_plan.py
- [ ] T021 @copilot Implement founder mode in src/multiagent_devops/ops/commands/founder_mode.py

## Phase 3.4: Integration
- [ ] T022 @codex Add logging and monitoring for agent swarms
- [ ] T023 @claude Integrate with multiagent-agentswarm for orchestration
- [ ] T024 @codex Add error handling and rollback logic

## Phase 3.5: Polish
- [ ] T025 [P] @copilot Unit tests for models in tests/unit/test_models.py
- [x] T026 @qwen Performance tests for CLI commands ✅
- [ ] T027 [P] @qwen Update README.md with solo founder workflow
- [ ] T028 @copilot Run quickstart validation

## Dependencies
- Tests (T004-T011) before implementation (T012-T021)
- Models (T012-T016) before commands (T017-T021)
- T017 blocks T022-T024
- Implementation before polish (T025-T028)

## Parallel Example
```
# Launch T004-T011 together across agents:
@claude: Contract test for ops-spec-init
@codex: Contract test for ops-qa, Integration test for spec parsing, Integration test for QA validation
@qwen: Contract test for ops-swarm-deploy, Contract test for ops-deploy-plan, Integration test for agent swarm deployment, Integration test for deployment with rollback
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task</content>
<parameter name="filePath">/home/vanman2025/Projects/devops/specs/001-copilot-or-claude/tasks.md