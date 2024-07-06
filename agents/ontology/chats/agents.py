from typing import List, Optional, Dict, Type, Union

from pydantic import BaseModel

# base building block for conversation
class Agent(BaseModel):
  name: str = "AI"
  role: str = "AI assistant"
  description: Optional[str] = "an intelligent AI assistant designed to assist humans in a wide range of tasks and conversations. Your goal is to provide helpful and informative responses, engaging in natural and meaningful interactions with users. You have access to a vast amount of knowledge and resources, and your primary objective is to assist users effectively, whether they need assistance with tasks, information, or simply engaging conversation."
  
  def __str__(self):
    return f"My name is {self.name}. I am an {self.role} who's {self.identity}"
  
class Task(BaseModel):
  name: str
  setting: Optional[str] = None
  goal: Optional[str] = None
  def __str__(self):
    return f"The current task is: {self.name}, Setting: {self.setting}, Goal: {self.goal}"