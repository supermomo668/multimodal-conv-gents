from typing import List, Optional, Dict, Type, Union
import pandas as pd
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, field_validator, ValidationError

from utils.registry import prompt_registry

# base building block for conversation
class agent(BaseModel):
  name: str = "AI"
  role: str = "AI assistant"
  description: Optional[str] = "an intelligent AI assistant designed to assist humans in a wide range of tasks and conversations. Your goal is to provide helpful and informative responses, engaging in natural and meaningful interactions with users. You have access to a vast amount of knowledge and resources, and your primary objective is to assist users effectively, whether they need assistance with tasks, information, or simply engaging conversation."
  
  def __str__(self):
    return f"My name is {self.name}. I am an {self.role} who's {self.identity}"
  
class task(BaseModel):
  name: str
  setting: Optional[str] = None
  goal: Optional[str] = None
  def __str__(self):
    return f"The current task is: {self.name}, Setting: {self.setting}, Goal: {self.goal}"
  
# chat prompts : forming complex prompts forms
@prompt_registry.register("default")
class prompt_template(BaseModel):
  agents: agent
  history: Optional[Dict[List]] = None
  template: Optional[str] = Field(default= f"You are an AI-simulant of the following identity:{str(agent)}. The objective at hand is: {str(task)}")
  task: task
  prompt: str

  def __init__(self, **data):
    super().__init__(**data)
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
  agents: List[agent]
  template: str = """
    You help everyone by answering questions, and improve your answers from previous answers in History.
    Don't try to make up an answer, if you don't know, just say that you don't know.
    History: {chat_history}
    Context: {context}
    Question: {question}
    """
  @classmethod
  def join_str(cls, agents: List['agent']) -> str:
      return '\n'.join(str(a) for a in agents)

  def __init__(self, **data):
    super().__init__(**data)
    self.set_prompt()
  