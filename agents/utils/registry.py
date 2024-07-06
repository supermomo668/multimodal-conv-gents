
class Registry:
    def __init__(self):
        self._registry = {}

    def register(self, name=None):
        def inner_wrapper(cls):
            nonlocal name
            if name is None:
                name = cls.__name__
            if name in self._registry:
                raise KeyError(f"Class name '{name}' already registered.")
            self._registry[name] = cls
            return cls
        return inner_wrapper

    def get_class(self, name):
        return self._registry.get(name)

    def __str__(self):
        return f"Registered classes: {', '.join(self._registry.keys())}"

# Add any of the needed registries here

prompt_registry = Registry()

parser_registry = Registry()

agent_registry = Registry() 

workflow_registry = Registry() 

# dialogues

transition_registry = Registry()