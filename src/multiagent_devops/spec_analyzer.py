#!/usr/bin/env python3
"""
Spec Analyzer Architecture
Analyzes spec files to automatically discover components, recommend agents,
and generate deployment plans
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import yaml
import logging

from .agent_capabilities import AgentRouter, recommend_agents

logger = logging.getLogger(__name__)


@dataclass
class SpecAnalysis:
    """Results of spec analysis"""
    spec_path: Path
    title: str
    description: str
    components_needed: List[str] = field(default_factory=list)
    stack_detected: Dict[str, str] = field(default_factory=dict)
    agents_recommended: List[str] = field(default_factory=list)
    deployment_targets: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    tasks_count: int = 0
    complexity: str = "medium"  # low, medium, high
    estimated_effort: str = "1-2 weeks"  # Rough estimate


class SpecAnalyzer:
    """Analyzes specs to determine project requirements"""
    
    # Component detection patterns
    COMPONENT_PATTERNS = {
        "multiagent-auth": [
            r"\bauth(?:entication|orization)\b",
            r"\blogin\b",
            r"\bpassword\b",
            r"\boauth\b",
            r"\bjwt\b",
            r"\bsession\b",
            r"\buser\s+management\b",
            r"\baccess\s+control\b"
        ],
        "multiagent-payments": [
            r"\bpayment\b",
            r"\bstripe\b",
            r"\bpaypal\b",
            r"\bsubscription\b",
            r"\bbilling\b",
            r"\binvoice\b",
            r"\brefund\b",
            r"\btransaction\b"
        ],
        "multiagent-testing": [
            r"\btest(?:ing)?\b",
            r"\bqa\b",
            r"\bquality\s+assurance\b",
            r"\bcoverage\b",
            r"\be2e\b",
            r"\bintegration\s+test\b"
        ],
        "multiagent-websockets": [
            r"\breal[\s-]?time\b",
            r"\bwebsocket\b",
            r"\blive\s+update\b",
            r"\bstreaming\b",
            r"\bchat\b",
            r"\bnotification\b"
        ],
        "multiagent-database": [
            r"\bdatabase\b",
            r"\bpostgres(?:ql)?\b",
            r"\bmysql\b",
            r"\bmongodb?\b",
            r"\bschema\b",
            r"\bmigration\b"
        ],
        "multiagent-cache": [
            r"\bcach(?:e|ing)\b",
            r"\bredis\b",
            r"\bmemcached?\b",
            r"\bcdn\b",
            r"\bperformance\b"
        ],
        "multiagent-email": [
            r"\bemail\b",
            r"\bsmtp\b",
            r"\bsendgrid\b",
            r"\bmailgun\b",
            r"\bnewsletter\b",
            r"\bnotification\b"
        ],
        "multiagent-storage": [
            r"\bfile\s+upload\b",
            r"\bs3\b",
            r"\bblob\s+storage\b",
            r"\bimage\s+upload\b",
            r"\bmedia\b"
        ],
        "multiagent-analytics": [
            r"\banalytics\b",
            r"\bmetrics\b",
            r"\btracking\b",
            r"\bdashboard\b",
            r"\breporting\b",
            r"\bvisualization\b"
        ],
        "multiagent-search": [
            r"\bsearch\b",
            r"\belasticsearch\b",
            r"\bsolr\b",
            r"\bindex(?:ing)?\b",
            r"\bfull[\s-]?text\b"
        ]
    }
    
    # Stack detection patterns
    STACK_PATTERNS = {
        "backend": {
            "python": [r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"],
            "javascript": [r"\bnode(?:\.?js)?\b", r"\bexpress\b", r"\bnest\.?js\b"],
            "java": [r"\bjava\b", r"\bspring\b", r"\bspringboot\b"],
            "go": [r"\bgolang\b", r"\b(?<!mon)go\b", r"\bgin\b"],
            "ruby": [r"\bruby\b", r"\brails\b"]
        },
        "frontend": {
            "react": [r"\breact\b", r"\bnext\.?js\b"],
            "vue": [r"\bvue(?:\.?js)?\b", r"\bnuxt\b"],
            "angular": [r"\bangular\b"],
            "svelte": [r"\bsvelte\b", r"\bsveltekit\b"]
        },
        "database": {
            "postgresql": [r"\bpostgres(?:ql)?\b"],
            "mysql": [r"\bmysql\b", r"\bmariadb\b"],
            "mongodb": [r"\bmongodb?\b"],
            "redis": [r"\bredis\b"],
            "sqlite": [r"\bsqlite\b"]
        },
        "deployment": {
            "docker": [r"\bdocker\b", r"\bcontainer\b"],
            "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
            "serverless": [r"\bserverless\b", r"\blambda\b", r"\bvercel\b"],
            "vps": [r"\bvps\b", r"\bdigitalocean\b", r"\blinode\b"]
        }
    }
    
    def __init__(self):
        self.router = AgentRouter()
    
    def analyze_spec(self, spec_path: Path) -> SpecAnalysis:
        """
        Analyze a spec directory to determine requirements
        
        Args:
            spec_path: Path to spec directory
            
        Returns:
            SpecAnalysis object with results
        """
        analysis = SpecAnalysis(spec_path=spec_path, title="", description="")
        
        # Read spec.md file
        spec_file = spec_path / "spec.md"
        if spec_file.exists():
            content = spec_file.read_text()
            analysis = self._analyze_content(content, analysis)
        
        # Read tasks.md for task count and complexity
        tasks_file = spec_path / "tasks.md"
        if tasks_file.exists():
            tasks_content = tasks_file.read_text()
            analysis = self._analyze_tasks(tasks_content, analysis)
        
        # Read plan.md for additional context
        plan_file = spec_path / "plan.md"
        if plan_file.exists():
            plan_content = plan_file.read_text()
            analysis = self._enhance_from_plan(plan_content, analysis)
        
        # Calculate complexity and effort
        analysis = self._calculate_complexity(analysis)
        
        return analysis
    
    def _analyze_content(self, content: str, analysis: SpecAnalysis) -> SpecAnalysis:
        """Analyze spec content for components and stack"""
        content_lower = content.lower()
        
        # Extract title and description
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                analysis.title = line[2:].strip()
                break
        
        # Find first paragraph as description
        in_paragraph = False
        description_lines = []
        for line in lines[1:]:
            if line.strip() and not line.startswith('#'):
                in_paragraph = True
                description_lines.append(line.strip())
            elif in_paragraph and not line.strip():
                break
        analysis.description = ' '.join(description_lines)
        
        # Detect needed components
        for component, patterns in self.COMPONENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    if component not in analysis.components_needed:
                        analysis.components_needed.append(component)
                    break
        
        # Detect technology stack
        for category, technologies in self.STACK_PATTERNS.items():
            for tech, patterns in technologies.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower, re.IGNORECASE):
                        analysis.stack_detected[category] = tech
                        break
                if category in analysis.stack_detected:
                    break
        
        # Determine deployment targets based on content
        analysis.deployment_targets = self._determine_deployment_targets(
            content_lower, 
            analysis.stack_detected
        )
        
        # Extract requirements
        analysis.requirements = self._extract_requirements(content)
        
        return analysis
    
    def _analyze_tasks(self, content: str, analysis: SpecAnalysis) -> SpecAnalysis:
        """Analyze tasks file for count and agent recommendations"""
        tasks = []
        agent_mentions = set()
        
        for line in content.split('\n'):
            # Count tasks
            if re.match(r'^- \[([ x])\] T\d+', line):
                analysis.tasks_count += 1
                tasks.append(line)
                
                # Extract agent mentions
                agent_match = re.search(r'@(\w+)', line)
                if agent_match:
                    agent_mentions.add(f"@{agent_match.group(1)}")
        
        # If agents are already assigned, use those
        if agent_mentions:
            analysis.agents_recommended = list(agent_mentions)
        else:
            # Otherwise, recommend based on task descriptions
            task_descriptions = [self._extract_task_description(t) for t in tasks]
            analysis.agents_recommended = recommend_agents(task_descriptions)
        
        return analysis
    
    def _extract_task_description(self, task_line: str) -> str:
        """Extract description from a task line"""
        # Pattern: - [ ] T001 [P] @agent Description in path/to/file
        match = re.search(r'@\w+\s+(.+?)(?:\s+in\s+\S+)?$', task_line)
        if match:
            return match.group(1)
        return task_line
    
    def _enhance_from_plan(self, content: str, analysis: SpecAnalysis) -> SpecAnalysis:
        """Enhance analysis with information from plan.md"""
        content_lower = content.lower()
        
        # Look for performance requirements
        if re.search(r'performance|fast|speed|optimiz', content_lower):
            if '@qwen' not in analysis.agents_recommended:
                analysis.agents_recommended.append('@qwen')
        
        # Look for security requirements
        if re.search(r'security|auth|encrypt|secure', content_lower):
            if '@claude' not in analysis.agents_recommended:
                analysis.agents_recommended.append('@claude')
        
        # Look for UI/frontend requirements
        if re.search(r'ui|frontend|react|component|interactive', content_lower):
            if '@codex' not in analysis.agents_recommended:
                analysis.agents_recommended.append('@codex')
        
        return analysis
    
    def _determine_deployment_targets(self, 
                                     content: str, 
                                     stack: Dict[str, str]) -> List[str]:
        """Determine appropriate deployment targets"""
        targets = []
        
        # Docker is almost always appropriate
        if 'docker' in content or 'container' in content:
            targets.append('docker')
        elif stack.get('backend'):  # Any backend suggests containerization
            targets.append('docker')
        
        # Kubernetes for scale mentions
        if any(word in content for word in ['scale', 'kubernetes', 'k8s', 'cluster']):
            targets.append('kubernetes')
        
        # Serverless for specific frameworks
        if any(word in content for word in ['lambda', 'vercel', 'netlify', 'serverless']):
            targets.append('serverless')
        
        # VPS for simple deployments
        if any(word in content for word in ['vps', 'digitalocean', 'linode', 'simple']):
            targets.append('vps')
        
        # Default to docker if nothing specific
        if not targets:
            targets.append('docker')
        
        return targets
    
    def _extract_requirements(self, content: str) -> Dict[str, Any]:
        """Extract requirements from spec content"""
        requirements = {
            'functional': [],
            'non_functional': [],
            'security': False,
            'performance': False,
            'accessibility': False,
            'i18n': False
        }
        
        # Look for requirements sections
        in_requirements = False
        current_type = 'functional'
        
        for line in content.split('\n'):
            if 'requirement' in line.lower():
                in_requirements = True
            elif in_requirements and line.startswith('-'):
                req_text = line[1:].strip()
                if 'functional' in line.lower():
                    current_type = 'functional'
                elif 'non-functional' in line.lower():
                    current_type = 'non_functional'
                else:
                    requirements[current_type].append(req_text)
        
        # Check for specific requirement types
        content_lower = content.lower()
        requirements['security'] = bool(re.search(r'security|auth|encrypt', content_lower))
        requirements['performance'] = bool(re.search(r'performance|fast|optimiz', content_lower))
        requirements['accessibility'] = bool(re.search(r'accessibility|a11y|wcag', content_lower))
        requirements['i18n'] = bool(re.search(r'i18n|international|localization', content_lower))
        
        return requirements
    
    def _calculate_complexity(self, analysis: SpecAnalysis) -> SpecAnalysis:
        """Calculate project complexity and effort estimate"""
        complexity_score = 0
        
        # Factor in number of components
        complexity_score += len(analysis.components_needed) * 2
        
        # Factor in number of tasks
        if analysis.tasks_count < 20:
            complexity_score += 1
        elif analysis.tasks_count < 50:
            complexity_score += 3
        else:
            complexity_score += 5
        
        # Factor in stack diversity
        complexity_score += len(analysis.stack_detected) * 1.5
        
        # Factor in requirements
        if analysis.requirements.get('security'):
            complexity_score += 2
        if analysis.requirements.get('performance'):
            complexity_score += 2
        if analysis.requirements.get('accessibility'):
            complexity_score += 1
        if analysis.requirements.get('i18n'):
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score < 5:
            analysis.complexity = "low"
            analysis.estimated_effort = "3-5 days"
        elif complexity_score < 15:
            analysis.complexity = "medium"
            analysis.estimated_effort = "1-2 weeks"
        else:
            analysis.complexity = "high"
            analysis.estimated_effort = "3-4 weeks"
        
        return analysis
    
    def generate_analysis_report(self, analysis: SpecAnalysis) -> str:
        """Generate a human-readable analysis report"""
        report = []
        report.append(f"# Spec Analysis Report: {analysis.title}\n")
        report.append(f"**Path**: {analysis.spec_path}")
        report.append(f"**Description**: {analysis.description}\n")
        
        report.append("## Detected Technology Stack")
        for category, tech in analysis.stack_detected.items():
            report.append(f"- **{category.title()}**: {tech}")
        
        report.append("\n## Required Components")
        for component in analysis.components_needed:
            report.append(f"- {component}")
        
        report.append("\n## Recommended Agents")
        for agent in analysis.agents_recommended:
            capability = self.router.get_capability_summary(agent)
            if capability:
                report.append(f"- **{agent}**: {capability['name']} - Best for {', '.join(capability['best_for'][:2])}")
        
        report.append("\n## Deployment Targets")
        for target in analysis.deployment_targets:
            report.append(f"- {target}")
        
        report.append("\n## Project Metrics")
        report.append(f"- **Tasks Count**: {analysis.tasks_count}")
        report.append(f"- **Complexity**: {analysis.complexity}")
        report.append(f"- **Estimated Effort**: {analysis.estimated_effort}")
        
        if analysis.requirements:
            report.append("\n## Requirements")
            if analysis.requirements.get('security'):
                report.append("- ✅ Security requirements detected")
            if analysis.requirements.get('performance'):
                report.append("- ✅ Performance requirements detected")
            if analysis.requirements.get('accessibility'):
                report.append("- ✅ Accessibility requirements detected")
            if analysis.requirements.get('i18n'):
                report.append("- ✅ Internationalization requirements detected")
        
        return "\n".join(report)
    
    def export_to_json(self, analysis: SpecAnalysis) -> str:
        """Export analysis to JSON format"""
        data = {
            "spec_path": str(analysis.spec_path),
            "title": analysis.title,
            "description": analysis.description,
            "components_needed": analysis.components_needed,
            "stack_detected": analysis.stack_detected,
            "agents_recommended": analysis.agents_recommended,
            "deployment_targets": analysis.deployment_targets,
            "requirements": analysis.requirements,
            "tasks_count": analysis.tasks_count,
            "complexity": analysis.complexity,
            "estimated_effort": analysis.estimated_effort
        }
        return json.dumps(data, indent=2)


def analyze_spec(spec_path: Path) -> Dict[str, Any]:
    """
    Main function to analyze a spec
    
    Args:
        spec_path: Path to spec directory
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = SpecAnalyzer()
    analysis = analyzer.analyze_spec(spec_path)
    
    return {
        "components_needed": analysis.components_needed,
        "stack_detected": analysis.stack_detected,
        "agents_recommended": analysis.agents_recommended,
        "deployment_targets": analysis.deployment_targets,
        "complexity": analysis.complexity,
        "estimated_effort": analysis.estimated_effort
    }