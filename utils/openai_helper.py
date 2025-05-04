import os
import json
from openai import OpenAI

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
        # Fallback message in case of any errors
        print(f"Error generating welcome message: {e}")
        return f"Welcome to Ten Yeshi's portfolio website! Feel free to explore my projects and get in touch."