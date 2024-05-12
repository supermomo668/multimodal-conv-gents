from typing import List, Optional, Dict, Type, Union
import pandas as pd
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from utils.registry import parser_registry

# settings to Scoring of the chat model
@parser_registry.register("EVAL_SCORER")
class EVAL_SCORER(BaseModel):
  is_task_completed: Optional[bool] = Field(..., description="is the task completed")
  is_image_available: Optional[bool] = Field(..., description="is there an image or screenshot in the input")
  score: Optional[float] = Field(..., description="a score between 0 and 1 on the best estimated progress of the task completion based on confirmation of task completion")
  explanation: str = Field(..., description="An explanation of the score based on the progress and accuracy of the task completion, if any")
  accuracy: Optional[float] = Field(..., description="a score between 0 and 1 on the accuracy between the field of interests of the webpage and the user query")
  evaluation_comment: str = Field(..., description="Comment on whether the context  provided was sufficient to evaluate the task completion, if any")
  