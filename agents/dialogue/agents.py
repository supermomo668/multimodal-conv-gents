from typing import List

import autogen
from autogen.code_utils import DEFAULT_MODEL
from omegaconf import DictConfig
from agents.ontology.dialogue.config import PodcastConfig
from agents.utils.registry import agent_registry

from .utils import termination_msg

@agent_registry.register(name="dialogue.podcast")
def create_podcast_agents(podcast_config: PodcastConfig, llm_config: dict, prompts: DictConfig) -> List[autogen.AssistantAgent]:
    podcast_gents = []
    
    # Format the host prompt
    host_prompt = prompts.host.format(host_name=podcast_config.host.name)
    
    host = autogen.AssistantAgent(
        name=podcast_config.host.name,
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        description=podcast_config.host.description,
        system_message=host_prompt,
    )
    
    # Format the guest prompts and create guest agents
    for guest in podcast_config.guests:
        guest_prompt = prompts.guest.format(guest_name=guest.name)
        podcast_gents.append(
            autogen.AssistantAgent(
                name=guest.name,
                llm_config=llm_config,
                system_message=guest_prompt,
                description=guest.description,
            )
        )
        
    return host,  podcast_gents

@agent_registry.register(name="research")
def create_research_agents(podcast_config: PodcastConfig, llm_config: dict, prompts: DictConfig) -> List[autogen.AssistantAgent]:
    agents = []
    
    agent_names = ["research_coder", "executor", "informer"]
    
    for agent_name in agent_names:
        system_message = prompts.research[agent_name]
        agent = autogen.AssistantAgent(
            name=agent_name,
            llm_config=llm_config,
            system_message=system_message
        )
        agents.append(agent)
        
    return agents