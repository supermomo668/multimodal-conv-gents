
# Registry of models with their details
FAL_MODELS = {
    'text-to-images': {
        'name': 'fal-ai/fast-sdxl',
        'description': 'Generates images based on textual prompts.',
        'args': ['prompt', 'negative_prompt', 'image_size', 'num_inference_steps', 'guidance_scale', 'num_images', 'format']
    },
    'images-to-video': {
        'name': 'fal-ai/fast-svd-lcm',
        'description': 'Generates a video from an image.',
        'args': ['image_url', 'motion_bucket_id', 'cond_aug', 'steps', 'fps']
    }
}
# constants.py
BRAVE_ENDPOINTS = {
    'news': {
        'url': 'https://api.search.brave.com/res/v1/news/search',
        'description': 'Search for news articles.'
    },
    'videos': {
        'url': 'https://api.search.brave.com/res/v1/videos/search',
        'description': 'Search for videos.'
    },
    'images': {
        'url': 'https://api.search.brave.com/res/v1/images/search',
        'description': 'Search for images.'
    },
    'web': {
        'url': 'https://api.search.brave.com/res/v1/web/search',
        'description': 'Search the web for information.'
    }
}
