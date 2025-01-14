from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import yaml
import os

class Settings(BaseSettings):
    # Load configuration from YAML file
    config_file: str = os.getenv("CONFIG_FILE", "app/config/default.yaml")
    
    @property
    def config(self) -> Dict[str, Any]:
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)
    

settings = Settings()