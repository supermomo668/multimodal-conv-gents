from pydantic import BaseModel, Field
from langchain_core.documents.base import Document

class WebSearchInput(BaseModel):
    web_query: str = Field()