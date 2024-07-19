import hydra, json
from omegaconf import DictConfig, OmegaConf
from dataclasses import asdict

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig # PodcastCharacters, AutogenLLMConfig, 
from thought_agents.dialogue.initiator import initiation_registry

from thought_agents.dialogue.chat import create_podcast_group
from thought_agents.utils.logger import setup_logger
from thought_agents.dialogue.utils import save_conversation

from thought_agents.ontology.config.dialogue import PodcastCharacters, Person, AutogenLLMConfig, PodcastConfig


def _init_character_cfg(podcast_cfg: PodcastConfig):
    """
    initialization breakdown 
    """
    # Ensure that the references to the nested configurations are correct
    host_config = podcast_cfg.character_cfg.host
    guests_config = podcast_cfg.character_cfg.guests

    # Dynamically initialize the podcast configuration
    character_cfg = PodcastCharacters(
        host=[Person(name=host_config.name, description=host_config.description)],
        guests=[
            Person(name=guest.name, description=guest.description) for guest in guests_config
        ]
    )
    return character_cfg


# @hydra.main(version_base=None, config_path="../../conf/dialogue", config_name/="default")
@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    logger = setup_logger('main_logger', 'app.log')
    logger.info("Application started")

    # Log the configuration as JSON with indentation
    logger.info(
        f"""Configuration:\n{json.dumps(
            OmegaConf.to_container(cfg, resolve=True), indent=2
        )}"""
    )
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    main_cfg: ConversationConfig = ConversationConfig(**config_dict)
    # prompts = OmegaConf.to_container(cfg.system_prompts)
    initializer, manager = create_podcast_group(main_cfg)
    # parsers
    chat_result = initiation_registry.get_class("podcast")(
        initializer, manager, main_cfg.podcast_config, main_cfg.system_prompts
    )
    logger.info(f"Chat result: {chat_result.chat_history}")
    logger.info(f"Script-only result: {chat_result.chat_history[3:]}")
    save_conversation(chat_result)
    save_conversation(chat_result, name="script_only")
    return chat_result.chat_history

if __name__ == "__main__":
    main()
