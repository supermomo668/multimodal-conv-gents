from typing import List, Optional, Dict, Type, Union
import pandas as pd
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from thought_agents.utils.registry import parser_registry

@parser_registry.register("scorer.task")
class TASK_SCORER(BaseModel):
  is_task_completed: Optional[bool] = Field(..., description="is the task of interest completed")
  progress_score: Optional[float] = Field(..., description="a score between 0 and 1 on the best estimated progress of the task completion, if any")
  accuracy_score: Optional[float] = Field(..., description="a score between 0 and 1 on the precision & correctness of completion, if any")
  explanation: str = Field(..., description="An explanation of the score based on the progress and accuracy of the task completion, if any")

  
# settings to Scoring of the chat model
@parser_registry.register("scorer.web_browse")
class WEB_BROWSE_SCORER(TASK_SCORER):
  is_image_available: Optional[bool] = Field(..., description="is there an image or screenshot in the input")
  