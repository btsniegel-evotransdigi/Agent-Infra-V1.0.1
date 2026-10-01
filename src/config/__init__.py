"""
Configuration package for Agent-Infra-V1.0.1
"""

import yaml
import os
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to YAML file"""
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def get_config_path(config_name: str) -> str:
    """Get path to configuration file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, "src", "config", config_name)


# Load default configurations
def load_standards_config() -> Dict[str, Any]:
    """Load standards configuration"""
    config_path = get_config_path("standards_config.yaml")
    if os.path.exists(config_path):
        return load_config(config_path)
    return {}


def load_evotransdigi_config() -> Dict[str, Any]:
    """Load EvoTransDigi configuration"""
    config_path = get_config_path("evotransdigi_config.yaml")
    if os.path.exists(config_path):
        return load_config(config_path)
    return {}
