from ast import Raise
import random
from agents.utils import registry
from .utils import weighted_choice


@registry.transition_registry.register("research")
def research_state_transition(last_speaker, groupchat, max_round=10):
    messages = groupchat.messages
    
    if len(messages) >= max_round-1:
        return groupchat.agents[-1]  # Assuming the script parser is the last agent
    
    match last_speaker.name.lower():
        case "init":
            return groupchat.agents[1]  # research_coder
        case "coder" | "research_coder":
            if "```python" in messages[-1]["content"]:
                return groupchat.agents[2]  # executor
            else:
                return groupchat.agents[1]  # research_coder
        case "executor":
            if "exitcode: 1" in messages[-1]["content"]:
                return groupchat.agents[1]  # research_coder
            else:
                return groupchat.agents[3]  # informer
        case "informer":
            return groupchat.agents[4]  # podcast_host
        
@registry.transition_registry.register("podcast")
def podcast_state_transition(last_speaker, groupchat, max_round=10):
    """
    host must come First 
    """
    messages = groupchat.messages
    character_agents = [a for a, name in zip(groupchat.agents, groupchat.agent_names) if name in groupchat.config.podcast.guest_names]
    
    if len(messages) >= max_round-1:
        return groupchat.agents[-1]  # Assuming the script parser is the last agent
    
    match last_speaker.name.lower():
        case "init" | "coder" | "research_coder"|"executor" | "informer":
            Raise("Invalid last_speaker. This transitioni only supports custom podcast speakers")
        case "host" | "podcast_host":
            return random.choice(character_agents)
        case _:
            next_speaker = weighted_choice(
                character_agents + [groupchat.agents[0]], last_speaker, weight=0.5, 
                host_chance=1/len(groupchat.config.podcast.guest_names)*0.5, 
                host=groupchat.agents[0]
            )
            return next_speaker
    
    
@registry.transition_registry.register("all_in_one")
def state_transition(last_speaker, groupchat, max_round=10):
    messages = groupchat.messages
    character_agents = [a for a, name in zip(groupchat.agents, groupchat.agent_names) if name in groupchat.config.podcast.guest_names]
    
    if len(messages) >= max_round-1:
        return groupchat.agents[-1]  # Assuming the script parser is the last agent
    
    match last_speaker.name.lower():
        case "init" | "coder" | "research_coder"|"executor" | "informer":
            return research_state_transition(last_speaker, groupchat)
        case _: # "host" | "podcast_host" or others
            return podcast_state_transition(last_speaker, groupchat)