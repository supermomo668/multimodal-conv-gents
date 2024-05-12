from abc import ABC, abstractmethod
from typing import *
from pathlib import Path
from beartype import beartype

class Pipeline(ABC):
    @abstractmethod
    def process_input(self, image_path: str | Path, text) -> List[Dict]:
        pass
    @abstractmethod
    def process_image(self, image_path: str | Path) -> List[Dict]:
        pass
    
    
    @abstractmethod
    @beartype
    def process_chat(self, text: str)->List[Dict]:
        return [{"type": "text", "text": text}]
    
    @abstractmethod
    def generate_completion(self, text: str, image_path: str):
        pass

    def __call__(self, *args):
        pass
   
from abc import ABC, abstractmethod
import wandb

@beartype
class metric(ABC):
    def __init__(self, config):
        self.config = config
        self.results = None
        self.artifact = None  # This will hold the wandb artifact or table object
    
    @abstractmethod
    def initialize(self):
        """Initialize any necessary resources or settings."""
        pass
    
    @abstractmethod
    def process(self):
        """The core logic for processing or evaluating."""
        pass
        

    
    def __call__(self):
        """Run the evaluator workflow: initialize, process, and log results."""
        self.initialize()
        self.process()
        self.log_to_wandb()
        return self.results