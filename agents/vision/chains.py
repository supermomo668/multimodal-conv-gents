import warnings 

from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
# from langchain_core.runnables import chain
from langchain.output_parsers import PydanticOutputParser

import base64
from utils.portkey import _init_langchain_portkey_args

from .prompts import GPTV_EVAL_QUERY_PROMPTS, EVALUATOR_SYSTEM_PROMPT
from utils import handle_image_b64
from agents.ontology.vqa import vqa_json_chain_config, vqa_chain_input


# require
def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]
  
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}

## Chain objects

class vqa_json_chain:
  def __init__(self, chain_config: vqa_json_chain_config, **kwargs) -> str | list[str] | dict:
    """
    Evaluates a query model using a chain of prompt templates, an image model, and a scorer model.

    Args:
        QUERY_MODEL (GPTV_QUERY): The query model to be evaluated.
        EVAL_PROMPT_VERSION (str, optional): The version of the evaluation prompt. Defaults to 'DEFAULT'.
        SCORER_MODEL (GPTV_SCORER, optional): The scorer model to be used. Defaults to GPTV_SCORER.
        llm_model (ChatOpenAI, optional): The language model to be used. Defaults to ChatOpenAI(model="gpt-4-vision-preview", temperature=0).

    Returns:
      the chain with the query model prompt.
    Note: (to infer/invoke)
      chain.invoke({
        "query": gptv_chain_eval_input.prompt,
        "image": gptv_chain_eval_input.image
      })

    """
    model_config = chain_config.CLIENT_CONFIG
    if chain_config.use_portkey:
      print(f"Using Portkey Gateway Client")
      kwargs.update(_init_langchain_portkey_args(model_config.model))
    self.input_prompter = TransformChain(
      input_variables=["query", "image"],
      output_variables=["message"],
      transform=self.gptv_prompter
    )
    self.model = ChatOpenAI(
      **model_config.model_dump(), **kwargs
    )
    self.parser = PydanticOutputParser(
      pydantic_object=chain_config.JSON_FORMAT)
  
  def gptv_prompter(self, inputs: dict) -> dict:
    im_b64 = handle_image_b64(inputs['image']) 
    content=[
      {"type": "text", "text": EVALUATOR_SYSTEM_PROMPT},
      {"type": "text", "text": inputs['query']},
      {"type": "text",  "text": self.parser.get_format_instructions()},
    ]
    if im_b64:
      content.append({
        "type": "image_url",
        "image_url": {
          "url": f"data:image/jpeg;base64,{im_b64}"}}
      )
    else:
      warnings.warn("image not found or not provided")
    self.input_msg = message = HumanMessage(content)
    return {"message": [message]}
  
  def _msg_post_process(self, msg):
    '''small amoutn of model output json post processing'''
    return msg.strip('```').strip('json').strip('\n')
  
  def gptv_model(self, inputs, **kwargs) -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    try:
      msg = self.model.invoke(inputs["message"])
      self.model_output = msg.content
      return self.model_output
    except Exception as e:
      warnings.warn(f"Error encountered while invoking model:{e}.\nCheck input message: f{self.input_msg}")
      return f"ERROR: {e}"
  
  @property
  def chain(self):
    return self.input_prompter | self.gptv_model | self.parser
  
  def invoke(self, args: vqa_chain_input):
    return self.chain.invoke(args)
  
class vqa_json_evaluator(vqa_json_chain):
  def __init__(self, gptv_chain_eval_input: vqa_json_chain_config, **kwargs) -> str | list[str] | dict:
    super().__init__(gptv_chain_eval_input, **kwargs)
  
  def prompter(self, inputs: dict) -> dict:
    im_b64 = handle_image_b64(inputs['image']) 
    content=[
      {"type": "text", "text": EVALUATOR_SYSTEM_PROMPT},
      {"type": "text", "text": inputs['query']},
      {"type": "text",  "text": self.parser.get_format_instructions()},
    ]
    if im_b64:
      content.append({
        "type": "image_url",
        "image_url": {
          "url": f"data:image/jpeg;base64,{im_b64}"}}
      )
    self.input_msg = message = HumanMessage(content)
    return {"message": [message]}
  
if __name__=="__main__":
  input = vqa_chain_input(query="hello, how are you?")
  print(vqa_json_chain().invoke(input))