from typing import List, Tuple, Dict, AnyStr
from beartype import beartype
from omegaconf import DictConfig

import autogen

from thought_agents.utils.registry import initiation_registry

from thought_agents.ontology.config.dialogue import PodcastConfig, PodcastCharacters

@initiation_registry.register(name="podcast")
def create_research_agents(
  initializer: autogen.AssistantAgent, 
  manager: autogen.GroupChatManager,
  podcast_cfg: PodcastConfig,
  system_prompts: str
  
  ) -> List[AnyStr]:
  return initializer.initiate_chat(
    manager, 
    message=system_prompts['podcast']["initiation"].format(
      characters=",".join(podcast_cfg.character_cfg.guest_names),
      topic=podcast_cfg.topic
      )
  )