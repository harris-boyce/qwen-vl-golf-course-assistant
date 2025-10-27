"""
Configuration management for the golf assistant.

This module handles loading and managing configuration from files and environment variables.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        # Load environment variables
        load_dotenv()
        
        self.config_data = {}
        
        if config_path and config_path.exists():
            self.load_from_file(config_path)
        else:
            self.load_defaults()
    
    def load_from_file(self, config_path: Path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.load_defaults()
    
    def load_defaults(self):
        """Load default configuration."""
        self.config_data = {
            'scraper': {
                'timeout': 30,
                'user_agent': 'Mozilla/5.0 (compatible; GolfCourseBot/1.0)',
                'retry_attempts': 3
            },
            'imagery': {
                'cache_dir': 'data/cache',
                'default_buffer_meters': 500,
                'source': 'NAIP'
            },
            'agent': {
                'model_name': 'Qwen/Qwen-VL-Chat',
                'device': 'auto',
                'load_model': False
            },
            'output': {
                'format': 'json',
                'save_path': 'outputs',
                'validate_schema': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'scraper.timeout')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get value from environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
        
        Returns:
            Environment variable value
        """
        return os.getenv(key, default)
    
    def save(self, output_path: Path):
        """
        Save current configuration to file.
        
        Args:
            output_path: Path to save configuration
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")


# Global configuration instance
_config = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def init_config(config_path: Optional[Path] = None) -> Config:
    """
    Initialize global configuration.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Config instance
    """
    global _config
    _config = Config(config_path)
    return _config
