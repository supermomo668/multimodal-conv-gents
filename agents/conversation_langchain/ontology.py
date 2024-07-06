from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    
class ModelConfig(BaseModel):
    provider: str="google"
    model: str="gemini-pro"