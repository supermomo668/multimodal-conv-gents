import pytest
from agents.ontology.config.dialogue import PodcastCharacters, AutogenLLMConfig
from agents.dialogue.chat import create_podcast_group

def test_create_podcast_group():
    characters = PodcastCharacters(
        host={"name": "Host", "description": "A test host."},
        guests=[
            {"name": "Guest 1", "description": "A test guest."},
            {"name": "Guest 2", "description": "Another test guest."}
        ]
    )
    
    llm_config = AutogenLLMConfig(
        cache_seed=42,
        temperature=0,
        timeout=120,
        config_list=[],
        filter_dict={"model": ["gemini-1.5-pro"]},
        config_list_path="conf/OAI_CONFIG_LIST.txt"
    )

    system_prompts = {"host": "Host system prompt", "guest": "Guest system prompt"}
    
    podcast_config = {"topic": "Test Topic", "character_cfg": characters, "system_prompts": system_prompts}

    # Create podcast group and validate
    initializer, manager = create_podcast_group(podcast_config)
    
    assert initializer is not None
    assert manager is not None
