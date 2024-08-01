from typing import Dict
from beartype import beartype
import warnings

import autogen
from thought_agents.utils.registry import transition_registry
from thought_agents.ontology.config.dialogue import PodcastConfig

from .utils import weighted_choice

from thought_agents.utils.logger import setup_logger

logger = setup_logger('main_logger', 'app.log')

@beartype
def get_state_transition(
    podcast_cfg: PodcastConfig, transition="podcast.default", MAX_ROUND=10):
    """
    Get the state transition function from the registry based on the transition type.
    """
    state_transition_func = transition_registry.get_class(transition)
    if not state_transition_func:
        raise ValueError(f"No state transition function registered for transition type: {transition}")
    def state_transition_wrapper(last_speaker, groupchat, max_round=MAX_ROUND):
        kwargs = {}
        return state_transition_func(
            last_speaker, groupchat, podcast_cfg.character_cfg, max_round, **kwargs
        )
    return state_transition_wrapper

# @transition_registry.register("research")   # cannot be used standalone
def research_state_transition(
    last_speaker, groupchat, destination_agent: str | autogen.Agent , max_round=10,
    ):
    """
    Parameters:
        last_speaker (Agent): The last speaker in the group chat.
        groupchat (GroupChat): The group chat object.
        max_round (int, optional): The maximum number of rounds. Defaults to 10.
        destination_agent (Agent, optional): The agent who is the informant (target of informer)
    Returns:
        Agent: The next speaker in the group chat.
    Raises:
        ValueError: If the last_speaker is unknown.
    """
    messages = groupchat.messages
    logger.info(f"Transition: research")
    logger.info(f"Number of agents: {len(groupchat.agents)}. Agents: {groupchat.agent_names}")
    if len(messages) >= max_round-1:
        return groupchat.agents[-1]  
        # Assuming the script parser is the last agent
    match last_speaker.name.lower():
        case "init":
            return groupchat.agent_by_name("research_coder")  # research_coder
        case "research_coder":
            if "```python" in messages[-1]["content"]:
                return groupchat.agent_by_name("executor")  # executor
            else:
                return groupchat.agent_by_name("research_coder")  # research_coder
        case "executor":
            if "exitcode: 1" in messages[-1]["content"]:
                warnings.warn(f"Agent failed to complete the task, passing back to coder")
                return groupchat.agent_by_name("research_coder")  # research_coder
            else:
                return groupchat.agent_by_name("informer")  # informer
        case "informer":
            # Always pass to Host last
            return destination_agent  # podcast_host
        case _:
            raise ValueError(f"Unknown last_speaker: {last_speaker.name} given for research state transition")
        
# @transition_registry.register("podcast")   # cannot be used standalone
def podcast_state_transition(
    last_speaker, groupchat, character_cfg, max_round=10, host_chance_factor=0.2
    ):
    """
    host must come First 
    """
    messages = groupchat.messages
    logger.info(f"Transition: podcast")
    logger.info(f"Number of agents: {len(groupchat.agents)}. Agents: {groupchat.agent_names}")
    # last round to the script parser
    if len(messages) >= max_round-1:
        return groupchat.agents_by_name("script_parser")  
    if last_speaker.name in character_cfg.guest_names + character_cfg.host_names:
        # Choose between next speaker based on non-host weightings
        next_speaker = weighted_choice(
            [a for a, name in zip(groupchat.agents, groupchat.agent_names) if name in character_cfg.host_names+character_cfg.guest_names],
            last_speaker,
            hosts=[groupchat.agent_by_name(n) for n in character_cfg.host_names],
            host_chance_factor=host_chance_factor, 
        )
        return next_speaker
    elif last_speaker.name == "script_parser":
        return groupchat.agent_by_name("script_parser")
    raise ValueError(f"Invalid last_speaker:{last_speaker.name}. This transition only supports custom podcast speakers")

@transition_registry.register("podcast.default")
def full_podcast_state_transition(
    last_speaker, groupchat, character_cfg, max_round=10, **kwargs):
    messages = groupchat.messages
    if len(messages) >= max_round-1:
        return groupchat.agents[-1]  # Assuming the script parser is the last agen
    match last_speaker.name.lower():
        case "init" | "coder" | "research_coder"| "executor" | "informer":
            speaker= research_state_transition(
                last_speaker, groupchat, destination_agent=character_cfg.hosts[0].name)
        case _: # podcast characters and all others
            speaker = podcast_state_transition(
                last_speaker, groupchat, character_cfg, max_round)
    if type(speaker) == str:
        speaker = groupchat.agent_by_name(speaker)
    return speaker