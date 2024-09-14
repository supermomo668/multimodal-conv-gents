from langchain_core.output_parsers import JsonOutputParser
from dataclasses import dataclass

from typing import Union, Optional
from pydantic import BaseModel, ConfigDict, Field

ROLE_PROMPT = "Your are a genuine, informative and valuable human being. Your name is {name} and you are {role}."
TASK_PROMPT = "The task is web navigation."

QUERY_PROMPTS = {
    "DEFAULT": "Use any of the given information, the screenshot, actions that the user may still need to take and any additional indicators of progress towards the task completion. Provide the best possible answer regardless of whether all the information is available.",
    #
    "multion_trajectory": "The context of the goal is as follows: {goal}, and the user's web navigation query: {query}. The final website has the following text: {dom}. Provide the best possible answer given information, if available, such as the screenshot, actions that the user may still need to take and  any additional indicators of progress towards the task completion. Leave blank on information not available.",
  # 
    "multion_trajectory-opentable": "The user is navigating on the OpenTable website to complete a restaurant reservation. The context of the task, the user's web navigation query, the screenshot and html DOM will be given in the following. Provide the best possible evaluation given information, if available, by comparing the user query with the current website context. Leave blank on information not available.\nContext of the task:{goal}\nThe user's query is: {query}. The website has the following text: {dom}.",
}

GPTV_EVAL_QUERY_PROMPTS = {}

# update default as needed
GPTV_EVAL_QUERY_PROMPTS.update({
    'DEFAULT': GPTV_EVAL_QUERY_PROMPTS.get('DEFAULT')
})
DEFAULT_EVAL_PROMPT = GPTV_EVAL_QUERY_PROMPTS.get('DEFAULT')

@dataclass
class DEFAULT_PROMPTER(BaseModel):
    query: Optional[str] = None
    goal: Optional[str] = None
    dom: Optional[str] = None
    model_config = ConfigDict(
        protected_namespaces=(),
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    def __init__(self, **data):
      super().__init__(**data)

    def create_prompt(self, template: str="Evaluate {GOAL} with {QUERY}") -> str:
        """Generates a custom prompt from a template string using the GOAL and QUERY fields.
        
        Args:
            template (str): The template string containing placeholders for {GOAL} and {QUERY}.
        
        Returns:
            str: A formatted string with the placeholders replaced by instance values.
        """
        # Use **self.dict() to pass all instance attributes as keyword arguments
        return template.format(**self.model_dump())

