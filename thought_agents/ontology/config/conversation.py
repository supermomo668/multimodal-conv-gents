"""
[deprecated 7/25/2024]
"""
from pydantic import BaseModel, Field
from typing import List

from thought_agents.ontology.chats import Agent, Task

class ConvesrationConfig(BaseModel):
    starter_prompt: str = Field(..., description="Input message for the conversation")
    system_prompt: str = Field(..., description="System prompt for the supervisor")
    agents: List[Agent] = Field(..., description="List of agents with their descriptions")
    style: str = Field(..., description="Style of interaction, e.g., round-robin")
    TEMPLATE: str = Field(..., description="Template for the chat history")

if __name__=="__main__":
  # Example usage
  config = ConvesrationConfig(
      starter_prompt="Input message for the conversation.",
      system_prompt="As a supervisor, your role is to oversee the insight between these workers: {members}. Based on the user's request, determine which worker should take the next action. Each worker is responsible for executing a specific task and reporting back their findings and progress. Once all tasks are completed, indicate 'FINISH'.",
      agents=[
          Agent(name="Darth Vader", description="Darth Vader is a fictional character in the Star Wars universe who serves at the Galactic Empire as the right-hand man to the Sith and is once known as Anakin Skywalker, the fallen Jedi."),
          Agent(name="Joe Rogan", description="A comedian and well-known podcast host for his own shows.")
      ],
      style="round-robin",
      TEMPLATE="The following is a friendly conversation between a human user and AI. \nThe AI is talkative and provides lots of specific details from its context. If the participants does not know the answer to a question, it truthfully says it does not know.\nCurrent conversation:\n{history}\nUser: {input}\nAI:"
  )

  print(config.json(indent=2))
