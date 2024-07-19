import warnings
import base64
import requests

from utils.urls import is_valid_url

def handle_image_b64(image_url: str) -> dict:
    """Convert the image from a URL to a base64-encoded string."""
    
    def encode_image_from_url(url):
        response = requests.get(url)
        try:
            response.raise_for_status()  
            # Ensure that the request was successful
            return base64.b64encode(response.content).decode('utf-8')
        except:
            return False
    if is_valid_url(image_url):
        return encode_image_from_url(image_url)
    else: 
        return None