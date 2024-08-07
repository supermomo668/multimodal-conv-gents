from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Any, Dict, List
from hydra.utils import to_absolute_path

import autogen

# model client settings
class model_client_config(BaseModel):
  model: str = "gpt-4-vision-preview"
  temperature: float = 0
  max_tokens: Optional[int] = 1024
  
class AutogenLLMConfig(BaseModel):
    cache_seed: int = 42
    temperature: float = 0
    timeout: int = 120
    config_list: Optional[List] = Field(default_factory=list)
    filter_dict: Dict = Field(default_factory=lambda: {"model": ["gemini-pro"]})
    config_list_path: str = "conf/OAI_CONFIG_LIST.txt"
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
      super().__init__(**data)
      self.config_list = self.initialize_config_list(
          self.config_list_path, self.filter_dict
      )

    def initialize_config_list(self, config_list_path: str, filter_dict: Dict) -> List:
      try:
        config_list = autogen.config_list_from_json(
          to_absolute_path(config_list_path),
          filter_dict=filter_dict,
        )
        return config_list
      except Exception as e:
        raise ValueError(f"Failed to initialize config_list: {e}")

