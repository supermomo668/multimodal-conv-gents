from hydra.core.config_store import ConfigStore
from dataclasses import dataclass, field
from typing import List, Dict, AnyStr

from pydantic import BaseModel, Field
from agents.ontology.chats.client import AutogenLLMConfig

class Person(BaseModel):
    name: AnyStr = Field(..., description="name of the person")
    description: AnyStr = Field(..., description="1-2 line description of the person if known, otherwise just a generic character.")


class PodcastCharacters(BaseModel):
    hosts: List[Person] = Field(..., description="host of the podcast")
    guests: List[Person] = Field(..., description="list of guests of the podcast")

    @property
    def guest_names(self) -> List[AnyStr]:
        return [guest.name for guest in self.guests]
    @property
    def host_names(self) -> List[AnyStr]:
        return [host.name for host in self.hosts]

class PodcastConfig(BaseModel):
    topic: str
    character_cfg: PodcastCharacters

class ConversationConfig(BaseModel):
    llm_config: AutogenLLMConfig
    podcast_config: PodcastConfig
    system_prompts: Dict[str, Dict | AnyStr]
    
# Register the configuration with ConfigStore
# cs = ConfigStore.instance()
# cs.store(name="podcast_base", node=PodcastConfig)

