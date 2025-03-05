import time
import random
import logging
import sys
import os

# Add the parent directory to the Python path to access apis.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from apis import get_openai_response

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    A client for interacting with the OpenAI API.
    Uses GPT-4o model for text generation.
    """
    
    def __init__(self, model="gpt-4o", requests_per_min=20):
        """
        Initialize the OpenAI client.
        
        Args:
            model (str, optional): The model to use. Defaults to "gpt-4o".
            requests_per_min (int, optional): Maximum requests per minute. Defaults to 20.
        """
        # Set model and rate limiting parameters
        self.model_name = model
        self.min_time_between_requests = 60 / requests_per_min
        self.last_request_time = 0
        
    def _wait_for_rate_limit(self):
        """Ensure rate limit compliance by waiting if needed."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_time_between_requests:
            wait_time = self.min_time_between_requests - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def generate(self, prompt, temperature=0.7, use_standard_format=True):
        """
        Generate text based on the provided prompt using OpenAI API.
        
        Args:
            prompt (str): The prompt to generate from.
            temperature (float, optional): Controls randomness. Defaults to 0.7.
            use_standard_format (bool, optional): Whether to add formatting instructions. Defaults to True.
            
        Returns:
            str: The generated text.
        """
        # Ensure we respect rate limits
        self._wait_for_rate_limit()
        
        # Add formatting instructions for consistent numerical answers
        if use_standard_format and "Question:" in prompt and not "FINAL_ANSWER:" in prompt:
            prompt += "\n\nIMPORTANT: If your answer includes a numerical value, provide it in decimal format (not as a fraction), " \
                      "rounded to 2 decimal places if needed. Put your final numerical answer within these delimiters: " \
                      "FINAL_ANSWER: [your numerical answer here] END_ANSWER"
        
        # Call the get_openai_response function from apis.py
        response = get_openai_response(prompt, modell=self.model_name)
        
        # Update the last request time
        self.last_request_time = time.time()
        
        return response