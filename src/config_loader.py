import json
import os

class ConfigLoader:
    def __init__(self, config_file="config/sites.json"):
        self.config_file = config_file
        self.configs = self._load_configs()
    
    def _load_configs(self):
        """Load configurations from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Config file not found: {self.config_file}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in config file: {self.config_file}")
    
    def get_config(self, site_name):
        """Get configuration for a specific site"""
        config = self.configs.get(site_name)
        if not config:
            raise Exception(f"Configuration not found for site: {site_name}")
        return config
    
    def get_all_sites(self):
        """Get list of all available sites"""
        return list(self.configs.keys())