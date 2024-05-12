from typing import List, Optional, Dict, Type, Union
import pandas as pd
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, field_validator, ValidationError
from langchain_core.pydantic_v1 import BaseModel as langchainBaseModel, Field

from utils.registry import parser_registry, prompt_registry
from .parser import EVAL_SCORER

# model client settings
class model_client_config(BaseModel):
  model: str = "gpt-4-vision-preview"
  temperature: float = 0
  max_tokens: Optional[int] = 1024
  
class gptv_config(model_client_config):
  detail: str = "high"
  

class vqa_json_chain_config(BaseModel):
  CLIENT_CONFIG: Optional[model_client_config] = model_client_config()
  JSON_FORMAT: Type[BaseModel] = Field(description="the json structure of the output")
  use_portkey: bool = True

class vqa_json_eval_chain_config(vqa_json_chain_config):
  JSON_FORMAT: Type[Union[EVAL_SCORER, BaseModel]] = Field(
    default=EVAL_SCORER, description="SCORER must be a subclass of EVAL_SCORER")
  @field_validator('PARSING', mode="before")
  def validate_scorer(cls, value):
    if issubclass(value, BaseModel) or issubclass(value, langchainBaseModel):
      return value  # Accepts any subclass of EVAL_SCORER including EVAL_SCORER itself
    else:
      raise ValueError(f"SCORER must be a EVAL_SCORER or BaseModel subclass. got {value.__subclasses__()}")

class vqa_chain_input(BaseModel):
  query: str
  image: Optional[str] = None  # <todo>
    
# user friendly config for gptv_chain_config  
class gptv_chain_metric_config(vqa_json_chain_config):
  prompt_version: Optional[str] = Field(default="DEFAULT")
  scorer: Optional[str] = Field(default="DEFAULT")

  def __init__(self, **data):
    super().__init__(**data)
    # Update the SCORER field based on the string identifier from parser_registry
    self.SCORER = parser_registry.get(self.scorer)
    if self.SCORER is None:
      raise ValueError(f"No scorer found with name {self.scorer} found. select from:  {parser_registry.list}")