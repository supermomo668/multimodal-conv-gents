from builtins import isinstance
from portkey_ai import Portkey
from portkey_ai import AsyncPortkey

from langchain_openai import ChatOpenAI
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL

import os
from dotenv import load_dotenv
import asyncio

from typing import *
# Load environment variables
load_dotenv()

def match_model_to_virtual_key_env(model):
  match model:
    case "gemini-pro-vision":
      key_name = "GEMINI_VISION_VIRTUAL_KEY"
    case "gemini-1.5-pro-latest":
      key_name = "GEMINI_VIRTUAL_KEY"
    case "gpt-4":
      key_name = "GPT4_VIRTUAL_KEY"
    case "gpt-4-vision" | "gpt-4-vision-preview":
      key_name = "GPT4V_VIRTUAL_KEY"
    case "gpt-3.5-turbo" | "gpt-3.5":
      key_name = "GPT3.5_VIRTUAL_KEY"
  key = os.getenv(key_name)
  assert key, f"Matching key not found for model {model}. Please export {key_name}"
  return key

def match_model_to_provider(model):
  if "gpt" in model.lower():
    provider = "openai"
  elif "gemini" in model.lower():
    provider = "google"
  return provider 

def _init_langchain_portkey_args(model="gemini-1.5-pro-latest"):
  assert os.getenv("PORTKEY_API_KEY"), "Ensure portkey API key is available in the environment variable"
  return {
    "api_key": os.getenv("PORTKEY_API_KEY", "X"),
    "base_url": PORTKEY_GATEWAY_URL,
    "default_headers": createHeaders(
      api_key=os.getenv("PORTKEY_API_KEY"),
      virtual_key=match_model_to_virtual_key_env(model),
      provider=match_model_to_provider(model))
  }
  
def get_portkey_langchain_llm(model):
    os.environ["PORTKEY_API_KEY"] = match_model_to_virtual_key_env(model)
    portkey_args = {
      'api_key': os.getenv("PORTKEY_API_KEY"),  # 
      'virtual_key': match_model_to_virtual_key_env(model),
      'base_url': PORTKEY_GATEWAY_URL
    }
    portkey_args = _init_langchain_portkey_args(model)
    if model.lower().startswith("gpt4"):
      portkey_args.update(config=os.getenv("PORTKEY_GPT4_CONFIG_KEY"))
    # return llm object
    return ChatOpenAI(**portkey_args)

async def query_model(
    completion_message:Union[List[str], str], 
    model='gemini-1.5-pro-latest'
    ):
    """
    Reads a message from a file and sends it to the Google Gemini model via Portkey.
    
    Args:
    file_path (str): Path to the text file containing the user's message.
    """
    if isinstance(completion_message, str):
      completion_message = [{
        "role": "user", "content": completion_message
      }]
    # Initialize Portkey with your API and virtual keys from environment variables
    # Invoke chat completions with Google Gemini
    completion = get_portkey_langchain_llm(model).chat.completions.create(
        message=completion_message,
        model=model
    )
    # Extract and print the response
    return completion.choices[0].message.content