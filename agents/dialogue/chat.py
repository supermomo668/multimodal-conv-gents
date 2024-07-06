import autogen
from .transition import state_transition
from .utils import termination_msg
from .agents import agent_registry
from hydra import compose, initialize
from omegaconf import OmegaConf


def create_chat_group(podcast_config, llm_config, prompts):
    initializer, research_coder, executor, informer = agent_registry.get_class("research")(
        podcast_config, llm_config, prompts)
    
    podcast_host = autogen.AssistantAgent(
        name=podcast_config.host.name,  
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        description=podcast_config.host.description,
        system_message=prompts["podcast_host"].format(host_name=podcast_config.host.name),
    )
    
    podcast_gents = [
        autogen.AssistantAgent(
            name=guest.name,
            llm_config=llm_config,
            system_message=prompts["podcast_guest"].format(guest_name=guest.name),
            description=guest.description,
        )
        for guest in podcast_config.guests
    ]
    
    groupchat = autogen.GroupChat(
        agents=[initializer, research_coder, executor, informer, podcast_host] + podcast_gents,
        messages=[],
        max_round=10,
        speaker_selection_method=state_transition,
    )
    return autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

if __name__ == "__main__":
    with initialize(config_path="../configs"):
        config = compose(config_name="default")
        llm_config = config.llm_config
        podcast_config = config.podcast
        prompts = OmegaConf.to_container(config.system_prompts)

        manager = create_chat_group(podcast_config, llm_config, prompts)
        characters_str = ",".join([g.name for g in podcast_config.guests])
        chat_result = manager.groupchat.agents[0].initiate_chat(
            manager, 
            message=f"This is a podcast among the characters: {characters_str} ..."
        )
        print(chat_result.chat_history)