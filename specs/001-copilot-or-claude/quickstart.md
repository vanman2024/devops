# Quickstart: MultiAgent DevOps Solo Founder Integration

This guide shows how to use the enhanced multiagent-devops component in the solo founder workflow.

## Prerequisites
- MultiAgent DevOps installed (`pip install multiagent-devops`)
- Spec-kit project with specs/ directory
- AI CLI (Claude Code, Copilot, etc.)

## Workflow Overview
1. **Spec**: Create feature spec with spec-kit
2. **Install**: Use devops for smart setup
3. **Coordinate**: Deploy agent swarms and monitor

## Step-by-Step Usage

### 1. Initialize DevOps for a Spec
```bash
# Parse spec and generate plans
ops spec-init --spec-path specs/001-feature

# Output: Deployment plan, CI/CD pipeline, QA checks
```

### 2. Deploy Agent Swarm
```bash
# Deploy agents to work on tasks
ops swarm-deploy --spec-path specs/001-feature --agents @copilot,@claude

# Monitor progress in real-time
tail -f /tmp/agent-swarm-logs/*.log
```

### 3. Run Quality Assurance
```bash
# Comprehensive QA against spec criteria
ops qa --spec-path specs/001-feature

# Includes: unit tests, integration tests, security scans, performance monitoring
```

### 4. Deploy to Target
```bash
# Deploy with rollback capability
ops deploy-plan --spec-path specs/001-feature --target docker --environment prod

# Rollback if needed
ops deploy-rollback --deployment-id <id>
```

### 5. Founder Mode (Guided Workflow)
```bash
# Interactive prompts for non-experts
ops founder-mode

# Follows "Spec -> Install -> Coordinate" workflow with guidance
```

## Example: User Authentication Feature

```bash
# 1. Create spec
specify create-spec user-auth

# 2. Initialize devops
ops spec-init --spec-path specs/001-user-auth

# 3. Deploy swarm
ops swarm-deploy --spec-path specs/001-user-auth

# 4. QA and deploy
ops qa --spec-path specs/001-user-auth
ops deploy-plan --target azure --environment staging
```

## Troubleshooting

### Common Issues
- **Spec not found**: Ensure spec directory exists and contains spec.md/tasks.md
- **Agent assignment failed**: Check @symbols in tasks.md are valid
- **QA failures**: Review spec acceptance criteria and test results
- **Deployment failed**: Check target configuration and logs

### Logs and Monitoring
- Agent logs: `/tmp/agent-swarm-logs/`
- QA reports: `specs/001-feature/qa-report.json`
- Deployment logs: `specs/001-feature/deploy.log`

## Next Steps
- Integrate with your AI CLI for seamless coordination
- Customize deployment targets in config files
- Extend QA checks for your specific needs