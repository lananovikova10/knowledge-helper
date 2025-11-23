"""Configuration management for YouTrack KB Helper"""

import os
import yaml
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from environment variables and optional config file

        Args:
            config_file: Path to YAML configuration file (optional)
        """
        # Load environment variables from .env file if it exists
        # Then load .env.local which overrides .env (useful for local development)
        load_dotenv()  # Load .env
        load_dotenv('.env.local', override=True)  # Load .env.local and override .env values

        # YouTrack settings (required)
        self.youtrack_base_url = os.getenv("YOUTRACK_BASE_URL")
        self.youtrack_token = os.getenv("YOUTRACK_TOKEN")

        # Analysis settings with defaults
        self.stale_threshold_days = int(os.getenv("STALE_THRESHOLD_DAYS", "180"))
        self.batch_size = 100
        self.output_format = "table"
        self.reports_dir = "./reports"
        self.verbose = False

        # Load additional settings from YAML if provided
        if config_file and Path(config_file).exists():
            self._load_yaml_config(config_file)

    def _load_yaml_config(self, config_file: str):
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        if config_data:
            # Analysis settings
            if 'analysis' in config_data:
                analysis = config_data['analysis']
                self.stale_threshold_days = analysis.get('stale_threshold_days', self.stale_threshold_days)
                self.batch_size = analysis.get('batch_size', self.batch_size)

            # Output settings
            if 'output' in config_data:
                output = config_data['output']
                self.output_format = output.get('format', self.output_format)
                self.reports_dir = output.get('reports_dir', self.reports_dir)
                self.verbose = output.get('verbose', self.verbose)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that required configuration is present

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.youtrack_base_url:
            return False, "YOUTRACK_BASE_URL is not set. Please set it in .env file or environment."

        if not self.youtrack_token:
            return False, "YOUTRACK_TOKEN is not set. Please set it in .env file or environment."

        return True, None

    def __repr__(self):
        """String representation (hiding token for security)"""
        return (f"Config(base_url={self.youtrack_base_url}, "
                f"stale_threshold_days={self.stale_threshold_days}, "
                f"batch_size={self.batch_size})")
