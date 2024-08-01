from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from hydra.utils import to_absolute_path
from cryptography.fernet import Fernet
import autogen

# Generate a key for encryption and decryption
# This should be securely stored and reused
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    return cipher_suite.decrypt(data.encode()).decode()

# Model client settings
class model_client_config(BaseModel):
    model: str = "gpt-4-vision-preview"
    temperature: float = 0
    max_tokens: Optional[int] = 1024
    timeout: int = 120
    cache_seed: int = 42

class AutogenLLMConfig(BaseModel):
    config_list: Optional[List] = Field(default_factory=list)
    model: str = "gemini-1.5-pro"
    filter_dict: Dict
    config_list_path: str = "conf/OAI_CONFIG_LIST.txt"
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.filter_dict = {"model": [self.model]}
        self.config_list = self.initialize_config_list(
            self.config_list_path, self.filter_dict
        )

    def initialize_config_list(self, config_list_path: str, filter_dict: Dict, encrypt: bool = False) -> List:
        """
        Initializes a list of configurations from a JSON file.

        Args:
            config_list_path (str): The path to the JSON file.
            filter_dict (Dict): A dictionary containing filters to apply to the configurations.
            encrypt (bool, optional): Whether to encrypt the API keys in the config list. Defaults to False.

        Returns:
            List: A list of configurations.

        Raises:
            ValueError: If there was an error initializing the config list.
        """
        try:
            config_list = autogen.config_list_from_json(
                to_absolute_path(config_list_path),
                filter_dict=filter_dict,
            )
            if encrypt:
                # Encrypt the api_key in the config_list
                for config in config_list:
                    if 'api_key' in config:
                        config['api_key'] = encrypt(config['api_key'])
            return config_list
        except Exception as e:
            raise ValueError(f"Failed to initialize config_list: {e}")

    def get_decrypted_config_list(self) -> List:
        decrypted_config_list = []
        for config in self.config_list:
            if 'api_key' in config:
                config['api_key'] = decrypt(config['api_key'])
            decrypted_config_list.append(config)
        return decrypted_config_list
