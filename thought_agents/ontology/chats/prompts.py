from typing import List, Optional, Dict, Type, Union
import pandas as pd
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, field_validator, ValidationError

from thought_agents.utils.registry import prompt_registry
from .agents import Agent, Task
  
# chat prompts : forming complex prompts forms
@prompt_registry.register("default")
class prompt_template(BaseModel):
  agents: list[Agent]
  task: Task
  history: Optional[List[Dict]] = None
  template: Optional[str] = Field(
    default= 
                                  "You are an AI-simulant of the following identity:{agents_description}. The objective at hand is: {task}")
  prompt: str

  def __init__(self, agents:List[Agent], task, **kwargs):
    self.agents_description = ','.join([str(desc) for desc in agents])
    self.task = task
    if self.template is not None:
      self.prompt = self.set_prompt()

  def set_prompt(self, template: str="Evaluate {GOAL} with {QUERY}") -> str:
      """Generates a custom prompt from a template string using the GOAL and QUERY fields.
      
      Args:
          template (str): The template string containing placeholders for {GOAL} and {QUERY}.
      
      Returns:
          str: A formatted string with the placeholders replaced by instance values.
      """
      # Use **self.dict() to pass all instance attributes as keyword arguments
      return self.template.format(**self.model_dump())
  class Config:
    arbitrary_types_allowed = True
      
@prompt_registry.register("conversation")
class conversation(prompt_template):
  agents: List[Agent]
  template: str = """
    You help everyone by answering questions, and improve your answers from previous answers in History.
    Don't try to make up an answer, if you don't know, just say that you don't know.
    History: {chat_history}
    Context: {context}
    Question: {question}
    """
  @classmethod
  def join_str(cls, agents: List[Agent]) -> str:
      return '\n'.join(str(a) for a in agents)

  def __init__(self, **data):
    super().__init__(**data)
    self.set_prompt()
  