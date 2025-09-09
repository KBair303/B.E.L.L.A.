"""
AI Image Generation Module for B.E.L.L.A.
Handles OpenAI DALL-E image generation with @salonsuitedigitalstudio branding
"""

import os
import openai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get OpenAI API key
OPENAI_API_KEY = os.environ.get("BELLAS_OPEN_AI_KEY") or os.environ.get("OPENAI_API_KEY2") or os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=60,  # Increased timeout for image generation stability
    max_retries=1  # Allow 1 retry for image generation
)

def enhance_prompt_with_branding(prompt):
    """
    ALWAYS enhance user prompt to ensure @salonsuitedigitalstudio branding is included
    This function guarantees branding appears in every generated image regardless of user input
    """
    # ALWAYS add branding - don't check if it exists, ensure it's prominent
    branding = "@salonsuitedigitalstudio"
    enhanced_prompt = f"{prompt}. MANDATORY: Include '{branding}' prominently and clearly visible in the image (on a sign, window display, wall art, business card, or digital screen). Make the branding professional and naturally integrated into the scene as if it's the business name."
    
    return enhanced_prompt

def generate_images(prompt, num_images=1, size="1024x1024"):
    """
    Generate images using OpenAI DALL-E 3
    
    Args:
        prompt (str): The image generation prompt
        num_images (int): Number of images to generate (1-4)
        size (str): Image size - "1024x1024", "1792x1024", or "1024x1792"
    
    Returns:
        list: List of dictionaries containing image URLs and metadata
    """
    try:
        # Enhance prompt with branding
        enhanced_prompt = enhance_prompt_with_branding(prompt)
        logger.info(f"Generating {num_images} image(s) with size {size}")
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Validate inputs
        if num_images < 1 or num_images > 4:
            raise ValueError("Number of images must be between 1 and 4")
        
        if size not in ["1024x1024", "1792x1024", "1024x1792"]:
            raise ValueError("Invalid image size")
        
        images = []
        
        # Resource management for image generation
        if num_images > 3:
            logger.warning(f"Large image request ({num_images}). Limiting to 3 for stability.")
            num_images = 3
        
        import time
        
        # Generate images one by one with timeout and pacing
        for i in range(num_images):
            try:
                logger.info(f"Generating image {i+1}/{num_images}")
                
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size=size,
                    quality="standard",
                    n=1  # DALL-E 3 only supports n=1
                )
                
                if response.data and len(response.data) > 0:
                    image_data = {
                        "url": response.data[0].url,
                        "revised_prompt": getattr(response.data[0], 'revised_prompt', enhanced_prompt),
                        "size": size,
                        "index": i + 1
                    }
                else:
                    raise Exception("No image data returned from API")
                
                images.append(image_data)
                logger.info(f"✅ Successfully generated image {i+1}")
                
                # Add delay between image generations to prevent overload
                if i < num_images - 1:
                    time.sleep(1)
                    
            except Exception as img_error:
                logger.error(f"Failed to generate image {i+1}: {str(img_error)}")
                # Add placeholder for failed image but continue
                images.append({
                    "url": None,
                    "error": "Image generation temporarily unavailable",
                    "size": size,
                    "index": i + 1
                })
        
        return images
        
    except openai.APIError as e:
        logger.error(f"OpenAI API Error: {e}")
        raise Exception(f"Failed to generate images: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in generate_images: {e}")
        raise Exception(f"Image generation failed: {str(e)}")

def validate_prompt(prompt):
    """
    Validate and clean the input prompt
    
    Args:
        prompt (str): User input prompt
        
    Returns:
        str: Cleaned and validated prompt
        
    Raises:
        ValueError: If prompt is invalid
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    prompt = prompt.strip()
    
    if len(prompt) < 10:
        raise ValueError("Prompt must be at least 10 characters long")
    
    if len(prompt) > 4000:
        raise ValueError("Prompt must be less than 4000 characters")
    
    # Check for potentially problematic content
    prohibited_words = ["nude", "nsfw", "violent", "illegal", "harmful"]
    if any(word in prompt.lower() for word in prohibited_words):
        raise ValueError("Prompt contains prohibited content")
    
    return prompt

def get_image_generation_suggestions():
    """
    Get example prompts for different business types
    """
    return {
        "beauty": [
            "Professional hair salon workspace with modern styling chairs, elegant lighting, and @salonsuitedigitalstudio branding visible on a wall sign",
            "Luxurious nail art studio setup with organized nail polish display, comfortable client chair, and @salonsuitedigitalstudio subtly reflected in a mirror",
            "Clean and modern makeup artist station with professional lighting, organized cosmetics, and @salonsuitedigitalstudio logo on a business card"
        ],
        "wellness": [
            "Serene massage therapy room with soft lighting, comfortable massage table, and @salonsuitedigitalstudio branding on a small wall plaque",
            "Professional skincare treatment room with clean aesthetic, modern equipment, and @salonsuitedigitalstudio visible on product packaging"
        ],
        "business": [
            "Modern professional office space with clean desk, computer setup, and @salonsuitedigitalstudio branding on a business card or laptop sticker",
            "Professional consultation room with comfortable seating, natural lighting, and @salonsuitedigitalstudio logo subtly visible in the background"
        ]
    }