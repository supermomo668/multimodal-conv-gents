import pytest
from hydra import compose, initialize
from omegaconf import OmegaConf
from agents.dialogue.main import main
from agents.ontology.config.dialogue import ConversationConfig

@pytest.mark.parametrize("config_name", ["default"])
def test_main_with_test_characters(config_name):
    with initialize(config_path="../conf/dialogue", job_name="test_app"):
        cfg = compose(config_name=config_name, overrides=["characters=test_characters"])
        # Convert the OmegaConf config to the Pydantic model
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        main_cfg = ConversationConfig(**config_dict)
        
        # Run the main function and get the result
        chat_history = main(main_cfg)
        
        # Add your assertions here
        assert chat_history is not None
        assert len(chat_history) > 0
        assert isinstance(chat_history, list)
