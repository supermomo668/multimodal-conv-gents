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
    config_list: Optional[List] = []
    filter_dict: Dict = {
      "model": ["gemini-pro"]
    }
    # ["gpt-4-vision-preview"] ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"]
    config_list_path: str = "conf/OAI_CONFIG_LIST.txt"
    
    @field_validator("config_list_path", mode="before")
    @classmethod
    def initialize_config_list(cls, v:list, values: Dict[str, Any]) -> List:
      try:
        config_list = autogen.config_list_from_json(
          to_absolute_path(v),
          filter_dict=values.data.get('filter_dict'),
        )
        values.data["config_list"] = config_list
        return v
      except Exception as e:
        raise ValueError(f"Failed to initialize config_list: {e}")
      

