import hydra
from omegaconf import DictConfig
from agents.dialogue.chat import create_chat_group
from agents.utils.logger import setup_logger
from agents.ontology.dialogue.config import PodcastConfig, Person

@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    logger = setup_logger('main_logger', 'app.log')
    logger.info("Application started with configurations: \n%s", cfg)

    # Ensure that the references to the nested configurations are correct
    host_config = cfg.podcast.host
    guests_config = cfg.podcast.guests

    # Dynamically initialize the podcast configuration
    podcast_config = PodcastConfig(
        host=Person(name=host_config.name, description=host_config.description),
        guests=[Person(name=guest.name, description=guest.description) for guest in guests_config]
    )
    
    llm_config = dict(cfg.llm_config)
    prompts = cfg.system_prompts
    
    manager = create_chat_group(podcast_config, llm_config, prompts)
    characters_str = ",".join([g.name for g in podcast_config.guests])
    chat_result = manager.groupchat.agents[0].initiate_chat(
        manager, 
        message=f"This is a podcast among the characters: {characters_str} ..."
    )
    logger.info(f"Chat result: {chat_result.chat_history}")

if __name__ == "__main__":
    main()
