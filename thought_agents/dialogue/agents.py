from typing import List, Tuple, Dict, AnyStr
from beartype import beartype
from omegaconf import DictConfig

import autogen
from autogen.code_utils import DEFAULT_MODEL

from thought_agents.ontology.chats.client import AutogenLLMConfig
from thought_agents.ontology.config.dialogue import ConversationConfig, Person
from thought_agents.ontology.parser.dialogue import podcast_parser, monologue_parser

from thought_agents.utils.registry import agent_registry

from .utils import termination_msg

def create_conversable_agent(
    cfg: ConversationConfig,
    person: Person
    ) -> autogen.ConversableAgent:
    return autogen.ConversableAgent(
        name=person.name,  
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=cfg.llm_config.model_dump(),
        description=person.description,
        system_message=cfg.system_prompts['podcast']['guest'].format(
            person.name, parser=monologue_parser.get_format_instructions()),
    )
    
@agent_registry.register(name="podcast.characters")
@beartype
def create_podcast_agents(
    cfg: ConversationConfig
    ) -> Tuple[List[autogen.ConversableAgent], List[autogen.ConversableAgent]]: 
    podcast_hosts = [
        autogen.ConversableAgent(
            name=host.name,  
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=cfg.llm_config.model_dump(),
            description=host.description,
            system_message=cfg.system_prompts['podcast']['host'].format(
                host.name, parser=monologue_parser.get_format_instructions()),
            )
        for host in cfg.podcast_config.character_cfg.hosts
    ]
    podcast_guests = [
        autogen.ConversableAgent(
            name=guest.name,
            code_execution_config=False,
            llm_config=cfg.llm_config.model_dump(),
            human_input_mode="NEVER",  # Never ask for human input.
            system_message=cfg.system_prompts['podcast']['guest'].format(
                guest.name, parser=monologue_parser.get_format_instructions()),
            description=guest.description,
        )
        for guest in cfg.podcast_config.character_cfg.guests
    ]
    return podcast_hosts, podcast_guests

@agent_registry.register(name="dialogue.research")
@beartype
def create_research_agents(
    llm_config: AutogenLLMConfig,
    system_prompts: Dict[str, Dict | AnyStr]
    ) -> List[autogen.AssistantAgent]:
    agents = []
    agent_names = ["research_coder", "executor", "informer"]
    agents = [
        autogen.AssistantAgent(
            name=agent_name,
            llm_config=llm_config.model_dump(),
            system_message=system_prompts['research'][agent_name],
            code_execution_config={"last_n_messages": 3, "work_dir": "_outputs/code", "use_docker": False} if "coder" in agent_name else {}
        ) for agent_name in agent_names
    ]
    return agents

@agent_registry.register(name="podcast.parser")
@beartype
def create_parser_agents(
    llm_config: AutogenLLMConfig,
    system_prompts: Dict[str, Dict | AnyStr]
    ) -> List[autogen.AssistantAgent]:
    script_parser = autogen.AssistantAgent(
        name="script_parser",
        llm_config=llm_config.model_dump(),
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: all([s in msg["content"].lower() for s in ["abstract", "script"]]),
        system_message=system_prompts['podcast']['script_parser'].format(
            parser=podcast_parser.get_format_instructions()
        ),
    )
    return [script_parser]