import yaml
import os

class Config:
    def __init__(self, config_file):
        self.config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)