from langchain_core.pydantic_v1 import BaseModel
from typing import Optional

# model client settings
class model_client_config(BaseModel):
  model: str = "gpt-4-vision-preview"
  temperature: float = 0
  max_tokens: Optional[int] = 1024