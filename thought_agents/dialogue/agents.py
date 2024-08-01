from typing import List, Tuple, Dict, AnyStr
from beartype import beartype

import autogen

from thought_agents.dialogue.tools import generate_llm_config
from thought_agents.ontology.chats.client import AutogenLLMConfig
from thought_agents.ontology.config.dialogue import ConversationConfig, Person
from thought_agents.ontology.parser.dialogue import podcast_parser, dialogue_parser

from thought_agents.utils.registry import agent_registry
from thought_agents.web.summarizer import WebSummarizer

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
            person.name, parser=dialogue_parser.get_format_instructions()),
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
                host.name, parser=dialogue_parser.get_format_instructions()),
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
                guest.name, parser=dialogue_parser.get_format_instructions()),
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
    for n in agent_names:
        match n:
            case "research_coder":
                kwargs = {
                    'code_execution_config': {"last_n_messages": 3, "work_dir": "_outputs/code", "use_docker": False},
                    'llm_config': llm_config.model_dump()
                }
                kwargs['llm_config'].update({'functions': [generate_llm_config(WebSummarizer(llm_config.model))]})
            case _:
                kwargs = {'llm_config': llm_config.model_dump()}
        agents.append(
            autogen.AssistantAgent(
                name=n,
                system_message=system_prompts['research'][n],
                **kwargs
            )
        )
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