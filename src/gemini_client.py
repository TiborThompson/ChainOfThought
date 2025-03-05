import google.generativeai as genai
import os
import time
import random
import logging

# Configure basic logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiClient:
    """
    A client for interacting with the Gemini API.
    Handles rate limiting, API key configuration, and retries with exponential backoff.
    """
    
    def __init__(self, api_key=None, model="gemini-1.5-flash", requests_per_min=2): # gemini-2.0-flash
        """
        Initialize the Gemini client with API key and rate limiting.
        
        Args:
            api_key (str, optional): The API key for Gemini. Defaults to environment variable.
            model (str, optional): The model to use. Defaults to "gemini-2.0-flash".
            requests_per_min (int, optional): Maximum requests per minute. Defaults to 2.
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No Gemini API key provided. Please set GEMINI_API_KEY environment variable or pass api_key to constructor.")
        
        # Configure the genai library
        genai.configure(api_key=self.api_key)
        
        # Set model and rate limiting parameters
        self.model_name = model
        self.model = genai.GenerativeModel(self.model_name)
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
    
    def generate(self, prompt, temperature=0.7, max_retries=5):
        """
        Generate text based on the provided prompt with retry logic and exponential backoff.
        
        Args:
            prompt (str): The prompt to generate from.
            temperature (float, optional): Controls randomness. Defaults to 0.7.
            max_retries (int, optional): Maximum number of retries. Defaults to 5.
            
        Returns:
            str: The generated text.
        """
        base_delay = 2  # Base delay in seconds
        max_delay = 60  # Maximum delay in seconds
        
        retries = 0
        while True:
            try:
                # Ensure we respect rate limits
                self._wait_for_rate_limit()
                
                # Make the API call
                response = self.model.generate_content(
                    prompt,
                    generation_config={"temperature": temperature}
                )
                return response.text
                
            except Exception as e:
                retries += 1
                error_message = str(e).lower()
                
                # Check if we should retry or give up
                if retries > max_retries:
                    logger.error(f"Failed after {max_retries} retries. Last error: {e}")
                    return f"Error after {max_retries} retries: {e}"
                
                # Calculate backoff with jitter
                delay = min(max_delay, base_delay * (2 ** (retries - 1)))
                jitter = random.uniform(0, 0.1 * delay)  # Add up to 10% jitter
                total_delay = delay + jitter
                
                # Add extra delay for specific errors
                if "resource exhausted" in error_message or "quota exceeded" in error_message:
                    logger.warning("Resource exhaustion detected. Adding significant additional delay.")
                    total_delay += 10  # Add 10 more seconds for resource exhaustion
                
                # Log the retry
                logger.warning(f"Error: {e}. Retrying in {total_delay:.2f} seconds (attempt {retries}/{max_retries})")
                time.sleep(total_delay)