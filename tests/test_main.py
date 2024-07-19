import pytest, os
from unittest import mock
from unittest.mock import MagicMock
from omegaconf import OmegaConf
from hydra import compose, initialize

from thought_agents.dialogue.main import main
from thought_agents.ontology.config.dialogue import ConversationConfig

@pytest.fixture
def mock_create_podcast_group():
    with mock.patch('thought_agents.dialogue.chat.create_podcast_group') as mock_cpg:
        yield mock_cpg

@pytest.fixture
def mock_initiation_registry():
    with mock.patch('thought_agents.dialogue.initiator.initiation_registry.get_class') as mock_ir:
        yield mock_ir

@pytest.fixture
def mock_save_conversation():
    with mock.patch('thought_agents.dialogue.utils.save_conversation') as mock_sc:
        yield mock_sc

@pytest.mark.parametrize("config_name", ["default"])
def test_main_with_test_characters(config_name, mock_create_podcast_group, mock_initiation_registry, mock_save_conversation):
    # Mock the dependencies
    mock_create_podcast_group.return_value = ("initializer_mock", "manager_mock")
    mock_initiation_registry.return_value.return_value = MagicMock(chat_history=["test message"])
    mock_save_conversation.return_value = None

    # Run the main function with test characters override
    with initialize(config_path="../conf/dialogue", job_name="test_app"):
        config = compose(config_name=config_name, overrides=["characters=test"])
        main_cfg: ConversationConfig = ConversationConfig(
            **OmegaConf.to_container(config, resolve=True)
        )
        # Call the main function
        chat_history = main(main_cfg)

        # Assertions
        assert chat_history is not None
        assert len(chat_history) > 0
        assert isinstance(chat_history, list)
        assert chat_history == ["test message"]

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_main.py"])
