import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gemini_client import GeminiClient
from src.custom_prompts import PromptTemplates

# Initialize client
client = GeminiClient()

# Test with a math problem
math_question = "What is the sum of the first 10 natural numbers?"
print(f"MATH QUESTION: {math_question}\n")

# Use math template to create initial prompt
initial_prompt = PromptTemplates.math_template(math_question)
print("INITIAL PROMPT:")
print(initial_prompt)

# Get first reasoning step
first_step = client.generate(initial_prompt)
print("\nFIRST REASONING STEP:")
print(first_step)

# Create final answer prompt
final_prompt = PromptTemplates.final_answer_template(math_question, first_step, domain="math")
print("\nFINAL ANSWER PROMPT:")
print(final_prompt)

# Get final answer
final_answer = client.generate(final_prompt)
print("\nFINAL ANSWER:")
print(final_answer)