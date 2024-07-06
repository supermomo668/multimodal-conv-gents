from hydra.core.config_store import ConfigStore
from dataclasses import dataclass, field
from typing import List

@dataclass
class Person:
    name: str
    description: str

@dataclass
class PodcastConfig:
    host: Person
    guests: List[Person]

    @property
    def guest_names(self) -> List[str]:
        return [guest.name for guest in self.guests]

@dataclass
class Config:
    cache_seed: int = 42
    temperature: float = 0
    timeout: int = 120
    podcast: PodcastConfig = field(default_factory=lambda: PodcastConfig(
        host=Person(name="NPR Podcast Host", description="An NPR Podcast Host who starts and sustains entertaining conversations that aim to inspire meaningful thoughts and perspectives from others."),
        guests=[
            Person(name="Harry Potter", description="Harry Potter is a fictional character and the titular protagonist in J.K. Rowling's series of fantasy novels."),
            # add more guests here
        ]
    ))

cs = ConfigStore.instance()
cs.store(name="podcast_base", node=Config)
