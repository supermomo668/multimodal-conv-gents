import os, json
from typing import List, AnyStr, Type, TypeVar
from .ontology import WebSearchInput, BaseModel, Document

from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.tools import BaseTool

from langchain_community.tools import BraveSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.llm import LLMChain
from langchain import hub # !pip install langchainhub -qqq

from .prompts import map_prompt_template, reduce_prompt_template, ChatPromptTemplate

async def load_urls_playwright(urls: List[AnyStr]=[]):
  loader = PlaywrightURLLoader(
    urls=urls, remove_selectors=["header", "footer"])
  return await loader.aload()

# docs = await load_urls_playwright()


async def advanced_url_extractor(query: str, search_params = {"count": 2}):
  search_tool = BraveSearch.from_api_key(
    api_key=os.getenv("BRAVE_API_KEY"), 
    search_kwargs=search_params
  )
  search_urls = json.loads(search_tool.run(query))
  urls = [l.get("link") for l in search_urls]
  return await load_urls_playwright(urls)


def client_factory(model="gemini-1.5-pro"):
  if "gemini" in model.lower():
    return ChatGoogleGenerativeAI(model=model)
  elif "gpt" in model.lower():
    return ChatOpenAI(model=model)
  
class WebSummarizer(BaseTool):
  # Autogen tool attributes
  name = "web_search_engine"
  description = "Use this tool when you need access to current or additional data, news from the internet"
  args_schema: Type[BaseModel] = WebSearchInput
  docs: List[Document] = None
  # Additional prompts attributes
  map_prompt: ChatPromptTemplate = None
  reduce_prompt: ChatPromptTemplate = None
  map_reduce_chain: MapReduceDocumentsChain = None
  text_splitter: TypeVar = None
  
  def __init__(self, model, summaries_max_token=int(4e3), **kwargs):
    super().__init__(**kwargs)
    if not self.map_prompt: 
      try:
        self.map_prompt =hub.pull("rlm/map-prompt")
      except:
        self.map_prompt = map_prompt_template
    if not self.reduce_prompt:
      try:
        self.reduce_prompt = hub.pull("rlm/reduce-prompt")
      except:
        self.reduce_prompt = reduce_prompt_template
    llm = client_factory(model)
    map_chain = LLMChain(llm=llm, prompt=self.map_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=self.reduce_prompt)
    
    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, 
        document_variable_name="doc_summaries"
    )
    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_chain,
        # The maximum number of tokens to group documents into.
        token_max=summaries_max_token,
    )
    # Combining documents by mapping a chain over them, then combining results
    self.map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )
  
    self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
  
  def url_extractor(self):
    async def advanced_url_extractor(query: str, search_params = {"count": 2}):
      search_tool = BraveSearch.from_api_key(
        api_key=os.getenv("BRAVE_API_KEY"), 
        search_kwargs=search_params
      )
      search_urls = json.loads(search_tool.run(query))
      urls = [l.get("link") for l in search_urls]
      return await load_urls_playwright(urls)

  async def _run(self, web_query: str) -> float:
      if self.docs is None:
          self.docs = await advanced_url_extractor(web_query)
      return self.map_reduce_chain.invoke(
        self.text_splitter.split_documents(self.docs)
        ).get("output_text")

  