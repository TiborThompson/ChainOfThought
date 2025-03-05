import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gemini_client import GeminiClient

# Test the Gemini client directly
client = GeminiClient()
result = client.generate("What is 2+2?")
print(f"Test result: {result}")