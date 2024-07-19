import base64
import requests
import logging
import os
import io
import mimetypes
from beartype import beartype
from typing import *
from pathlib import Path

from openai import OpenAI
from PIL import Image

from utils.urls import is_valid_url as is_url

from .base import Pipeline
from .constants import ENDPOINTS

from thought_agents.ontology.vqa import gptv_config

from utils.portkey import _init_portkey


DEFAULT_GPTV_CONFIG = gptv_config()

logger = logging.getLogger(__name__)

class GPTV(Pipeline):
    def __init__(
        self, 
        config: dict | gptv_config = DEFAULT_GPTV_CONFIG
        ):
        if isinstance(config, dict):
            config = gptv_config(**config)
        if config.USE_PORTKEY:
            self.chat_client = _init_portkey(config.model)
        else:
            try:
                self.api_key = os.environ["OPENAI_API_KEY"]
                self.chat_client = OpenAI()
            except KeyError:
                raise KeyError(
                    "Please set your OpenAI API key in the environment variable `OPENAI_API_KEY`"
                )
        self.config = config
        logger.info(self.config)
        self.api_url = ENDPOINTS.get("Chat_Completions_API")

    @staticmethod
    def is_base64(s):
        try:
            return base64.b64encode(base64.b64decode(s)).decode("utf-8") == s
        except Exception:
            return False
        
    @beartype
    def process_input(self, image_path: str | Path| List[Union[str, Path]], text:str):
        img_contents = self.process_image(image_path)
        text= self.process_chat(text)
        img_contents.extend(text)
        return [{
            "role": "user", "content": img_contents
        }]
    
    def process_chat(self, text: str):
        return super().process_chat(text)
    
    def encode_image(self, image_input):
        if isinstance(image_input, str) and Path(image_input).exists():
            return image_input
        elif isinstance(image_input, Image.Image):
            buffered = io.BytesIO()
            image_input.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)} or check {image_input} exist")

    def process_image(self, image_inputs: str | List[str]):
        """
        Process an image input and return a list of image contents.

        Parameters:
            image_input (Union[str, List[str]]): The input image or a list of input images.
                If a single image is provided, it can be either a URL or a file path.
                If a list of images is provided, each image can be either a URL or a file path.

        Returns:
            List[Dict[str, Union[str, Dict[str, str]]]]: A list of image contents.
                Each image content is represented as a dictionary with the following keys:
                    - "type" (str): The type of the image content ("image_url").
                    - "image_url" (Dict[str, str]): The URL or base64-encoded image data.
                        - "url" (str): The URL or base64-encoded image data.

        Raises:
            None

        Examples:
            >>> image_processor = ImageProcessor()
            >>> image_processor.process_image("https://example.com/image.jpg")
            [{"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}]
            >>> image_processor.process_image(["https://example.com/image1.jpg", "image2.jpg"])
            [{"type": "image_url", "image_url": {"url": "https://example.com/image1.jpg"}},
             {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,encoded_image_data"}}]
        """
        if not isinstance(image_inputs, list):
            image_inputs = [image_inputs]
        image_contents = []
        for image in image_inputs:
            if is_url(image):
                image_content = {
                    "type": "image_url", 
                    "image_url": {"url": image},
                }
            else:
                encoded_image = self.encode_image(image)
                mime_type, _ = mimetypes.guess_type(image[:30]) if isinstance(image, str) else ("image/jpeg", None)
                image_content = {
                    "type": "image_url", 
                    "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}}
            image_contents.append(image_content)
        return image_contents
    
    def generate_completion(
        self, text: str, images: List[str]):
        """
        generate caption via OpenAI's SDK or API
        """
        composed_message = self.process_input(images, text)
        try:
            # Assuming this is where the API call that might raise the error is made
            response = self.chat_client.chat.completions.create(
                model=self.config.model,
                messages=composed_message,
                max_tokens=self.config.max_tokens
            )
        except requests.exceptions.HTTPError as e:
            # Extracting JSON response from the error, assuming it's in the same format as the BadRequestError example
            error_response = e.response.json()
            error_message = error_response.get('error', {}).get(
                'message', f'An exception occurred: {e}')
            return f"error: {error_message}"
    # further extract meessage : 
        return response.choices[0].message.content
    
    def __call__(self, *args: Optional[Dict]):
        """
        calls the generate_completion method 
        """
        return self.generate_completion(*args)
                


if __name__ == "__main__":
    """
    Check OpenAI docs on GPT-Vision: https://platform.openai.com/docs/guides/vision
    Standalone run:
        python -m finetuning.evaluate.vision.openai
    """
    from dotenv import load_dotenv
    assert load_dotenv(), "Please set your OpenAI API key in .env"
    image_src = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
    ][0]
    prompt = "Describe the element and a detailed summary of what's in this webpage?"
    def run_example(pipeline, prompt, image_src):
        caption = pipeline.generate_completion(
            prompt, image_src)
        return caption
    
    pipeline = GPTV(gptv_config)
    logger.info(run_example(
        pipeline, prompt, image_src))
    
    # [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='This image depicts a serene natural landscape featuring a wooden boardwalk that extends through a lush meadow with green grasses. The vibrant greenery suggests this area may be a wetland or marsh, where such walkways are common to allow for exploration without disturbing the delicate ecosystem. The sky is blue with a scattering of white clouds, indicating it could be a fair-weather day and a wonderful opportunity for a nature walk. The photo gives a sense of tranquility and an invitation to the viewer to take a peaceful stroll amidst nature.', role='assistant', function_call=None, tool_calls=None))]
    #  extract meessage with: 
    #   response.choices[0].message.content