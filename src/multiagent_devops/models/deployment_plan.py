"""
DeploymentPlan model: Configuration for CI/CD and deployment targets
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class DeploymentTarget(str, Enum):
    """Supported deployment targets"""
    DOCKER = "docker"
    AZURE = "azure"
    AWS = "aws"
    SCRIPT = "script"


class Environment(str, Enum):
    """Deployment environments"""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class DeploymentPlan(BaseModel):
    """
    Configuration for CI/CD and deployment targets.

    Defines how and where to deploy the application,
    including target platform and environment settings.
    """

    target: DeploymentTarget = Field(..., description="Deployment target platform")
    environment: Environment = Field(default=Environment.DEV, description="Deployment environment")
    config: Dict[str, Any] = Field(default_factory=dict, description="Target-specific configuration")
    rollback_enabled: bool = Field(default=True, description="Whether rollback is enabled")

    @validator('target')
    def validate_target(cls, v):
        """Validate deployment target is supported"""
        if v not in [target.value for target in DeploymentTarget]:
            supported = [target.value for target in DeploymentTarget]
            raise ValueError(f"Unsupported deployment target: {v}. Supported: {supported}")
        return v

    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment is supported"""
        if v not in [env.value for env in Environment]:
            supported = [env.value for env in Environment]
            raise ValueError(f"Unsupported environment: {v}. Supported: {supported}")
        return v

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with optional default"""
        return self.config.get(key, default)

    def set_config_value(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value

    def validate_config(self) -> bool:
        """
        Validate that the configuration is complete for the target.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.target == DeploymentTarget.DOCKER:
            required_keys = ["image_name", "container_port"]
            missing = [key for key in required_keys if key not in self.config]
            if missing:
                raise ValueError(f"Docker deployment missing required config: {missing}")

        elif self.target == DeploymentTarget.AZURE:
            required_keys = ["resource_group", "app_service_name"]
            missing = [key for key in required_keys if key not in self.config]
            if missing:
                raise ValueError(f"Azure deployment missing required config: {missing}")

        elif self.target == DeploymentTarget.AWS:
            required_keys = ["region", "cluster_name"]
            missing = [key for key in required_keys if key not in self.config]
            if missing:
                raise ValueError(f"AWS deployment missing required config: {missing}")

        elif self.target == DeploymentTarget.SCRIPT:
            if "script_path" not in self.config:
                raise ValueError("Script deployment missing required config: script_path")

        return True

    def get_deployment_commands(self) -> Dict[str, str]:
        """
        Generate deployment commands based on target and config.

        Returns:
            Dictionary of command names to command strings
        """
        commands = {}

        if self.target == DeploymentTarget.DOCKER:
            image_name = self.get_config_value("image_name", "myapp")
            container_port = self.get_config_value("container_port", 8000)
            host_port = self.get_config_value("host_port", container_port)

            commands["build"] = f"docker build -t {image_name} ."
            commands["run"] = f"docker run -d -p {host_port}:{container_port} {image_name}"
            if self.rollback_enabled:
                commands["rollback"] = f"docker stop $(docker ps -q --filter ancestor={image_name})"

        elif self.target == DeploymentTarget.AZURE:
            resource_group = self.get_config_value("resource_group")
            app_service_name = self.get_config_value("app_service_name")

            commands["deploy"] = f"az webapp up --name {app_service_name} --resource-group {resource_group}"
            if self.rollback_enabled:
                commands["rollback"] = f"az webapp deployment slot swap --slot staging --name {app_service_name} --resource-group {resource_group}"

        elif self.target == DeploymentTarget.AWS:
            region = self.get_config_value("region", "us-east-1")
            cluster_name = self.get_config_value("cluster_name")

            commands["deploy"] = f"aws ecs update-service --cluster {cluster_name} --service my-service --force-new-deployment --region {region}"
            if self.rollback_enabled:
                commands["rollback"] = f"aws ecs update-service --cluster {cluster_name} --service my-service --task-definition my-task-def-rollback --region {region}"

        elif self.target == DeploymentTarget.SCRIPT:
            script_path = self.get_config_value("script_path")
            commands["deploy"] = f"bash {script_path}"
            if self.rollback_enabled:
                rollback_script = self.get_config_value("rollback_script")
                if rollback_script:
                    commands["rollback"] = f"bash {rollback_script}"

        return commands

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "target": self.target.value,
            "environment": self.environment.value,
            "config": self.config,
            "rollback_enabled": self.rollback_enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeploymentPlan':
        """Create from dictionary"""
        return cls(
            target=data["target"],
            environment=data.get("environment", "dev"),
            config=data.get("config", {}),
            rollback_enabled=data.get("rollback_enabled", True)
        )

    @classmethod
    def create_default(cls, target: str = "docker") -> 'DeploymentPlan':
        """Create a default deployment plan for the given target"""
        configs = {
            "docker": {
                "image_name": "multiagent-devops-app",
                "container_port": 8000,
                "host_port": 8000
            },
            "azure": {
                "resource_group": "multiagent-devops-rg",
                "app_service_name": "multiagent-devops-app"
            },
            "aws": {
                "region": "us-east-1",
                "cluster_name": "multiagent-devops-cluster"
            },
            "script": {
                "script_path": "./deploy.sh"
            }
        }

        return cls(
            target=target,
            environment="dev",
            config=configs.get(target, {}),
            rollback_enabled=True
        )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True