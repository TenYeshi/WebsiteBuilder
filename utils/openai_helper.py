import os
import json
import logging
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_welcome_message(visitor_info=None):
    """
    Generate a personalized welcome message based on visitor information
    
    Args:
        visitor_info (dict): Information about the visitor (optional)
                            Can include: name, time_of_day, location, etc.
    
    Returns:
        str: A personalized welcome message
    """
    # Default information if none provided
    if visitor_info is None:
        visitor_info = {}
    
    name = visitor_info.get('name', 'there')
    time_of_day = visitor_info.get('time_of_day', 'today')
    location = visitor_info.get('location', '')
    
    # Create fallback messages based on the visitor info
    if name and name.lower() != 'there' and location and time_of_day and time_of_day.lower() != 'today':
        fallback_message = f"Good {time_of_day}, {name} from {location}! Welcome to Ten Yeshi's portfolio website. Feel free to explore my projects and get in touch."
    elif name and name.lower() != 'there' and time_of_day and time_of_day.lower() != 'today':
        fallback_message = f"Good {time_of_day}, {name}! Welcome to Ten Yeshi's portfolio website. I invite you to explore my work and projects."
    elif name and name.lower() != 'there' and location:
        fallback_message = f"Welcome to my portfolio website, {name} from {location}! I hope you enjoy browsing through my projects and achievements."
    elif name and name.lower() != 'there':
        fallback_message = f"Welcome, {name}! Thanks for visiting Ten Yeshi's portfolio website. Please take a look around at my projects."
    elif location:
        fallback_message = f"Hello visitor from {location}! Welcome to Ten Yeshi's portfolio website. I hope you find my projects interesting."
    else:
        fallback_message = "Welcome to Ten Yeshi's portfolio website! Feel free to explore my projects and get in touch."
    
    # Create a prompt for the OpenAI API
    prompt = f"""
    Create a friendly, warm welcome message for a visitor to Ten Yeshi's portfolio website.
    
    Visitor info:
    - Name (if known): {name}
    - Time of day: {time_of_day}
    - Location (if known): {location}
    
    The message should:
    - Be professional but warm and inviting
    - Be brief (maximum 2 sentences)
    - Include the visitor's name if provided
    - Reference the time of day if provided
    - Reference the visitor's location if provided
    - End with an invitation to explore the portfolio
    
    Do not use emojis or overly casual language.
    """
    
    try:
        # Check if API key is provided
        if not os.environ.get('OPENAI_API_KEY'):
            logger.warning("No OpenAI API key provided. Using fallback message.")
            return fallback_message
            
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant creating personalized welcome messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Return the generated welcome message
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Log the specific error
        logger.error(f"Error generating welcome message: {e}")
        
        # Check for specific error types
        error_str = str(e)
        if "insufficient_quota" in error_str:
            logger.warning("OpenAI API quota exceeded. Using fallback message.")
        elif "invalid_api_key" in error_str:
            logger.warning("Invalid OpenAI API key. Using fallback message.")
        elif "rate_limit_exceeded" in error_str:
            logger.warning("OpenAI API rate limit exceeded. Using fallback message.")
            
        # Return fallback message
        return fallback_message