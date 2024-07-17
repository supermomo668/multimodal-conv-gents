from typing import List, Dict, AnyStr
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

from agents.ontology.config.dialogue import Person

class Monologue(BaseModel):
    dialogue: str = Field(..., description="your dialogue to the current conversation")
    inner_thought: str = Field(..., description="your inner thought up to the current conversation")
    
class Dialogue(BaseModel):
    speaker: Person
    monologue: Monologue

class Podcast(BaseModel):
    abstract: AnyStr = Field(..., description="abstract of the podcast")
    podcast: List[Dialogue] = Field(..., description="the dialogues script in the podcast")
    
podcast_parser = PydanticOutputParser(pydantic_object=Podcast)
monologue_parser = PydanticOutputParser(pydantic_object=Monologue)