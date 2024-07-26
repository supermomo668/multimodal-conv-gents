from typing import List, Dict, AnyStr
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

from thought_agents.ontology.config.dialogue import Person

class Monologue(BaseModel):
    dialogue: str = Field(..., description="your dialogue to the current conversation")
    inner_thought: str = Field(..., description="your inner thought up to the current conversation")
    
class Dialogue(BaseModel):
    speaker: Person
    monologue: Monologue

class Podcast(BaseModel):
    title: str = Field(..., description="Title of the podcast")
    abstract: str = Field(..., description="Abstract of the podcast")
    dialogues: List[Dialogue] = Field(..., description="Script of dialogues that took palce in the podcast")
    
podcast_parser = PydanticOutputParser(pydantic_object=Podcast)
monologue_parser = PydanticOutputParser(pydantic_object=Monologue)