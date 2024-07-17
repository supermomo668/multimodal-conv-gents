import hydra, json
from omegaconf import DictConfig, OmegaConf
from dataclasses import asdict

from agents.ontology.config.dialogue import ConversationConfig, PodcastConfig # PodcastCharacters, AutogenLLMConfig, 
from agents.dialogue.initiator import initiation_registry

from agents.dialogue.chat import create_podcast_group
from agents.utils.logger import setup_logger
from agents.dialogue.utils import save_conversation

from agents.ontology.config.dialogue import PodcastCharacters, Person, AutogenLLMConfig, PodcastConfig


def _init_podcast_cfg(podcast_cfg: PodcastConfig):
    """
    initialization breakdown 
    """
    # Ensure that the references to the nested configurations are correct
    host_config = podcast_cfg.character_cfg.host
    guests_config = podcast_cfg.character_cfg.guests

    # Dynamically initialize the podcast configuration
    podcast_config = PodcastCharacters(
        host=Person(name=host_config.name, description=host_config.description),
        guests=[
            Person(name=guest.name, description=guest.description) for guest in guests_config
        ]
    )
    return podcast_config


# @hydra.main(version_base=None, config_path="../../conf/dialogue", config_name/="default")
@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    logger = setup_logger('main_logger', 'app.log')
    logger.info("Application started")

    # Log the configuration as JSON with indentation
    logger.info(
        f"Configuration:\n{json.dumps(
            OmegaConf.to_container(cfg, resolve=True), indent=2
        )}"
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
    save_conversation(chat_result)
    return chat_result.chat_history

if __name__ == "__main__":
    main()
