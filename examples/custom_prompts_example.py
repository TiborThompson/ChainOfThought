import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gemini_client import GeminiClient
from src.custom_prompts import PromptTemplates

def solve_with_custom_prompts(client, question, domain, steps=3):
    """
    Solve a problem using custom domain-specific prompts.
    
    Args:
        client: The Gemini client
        question: The question to solve
        domain: The domain (math, logic, coding, science)
        steps: Number of reasoning steps
        
    Returns:
        dict: A dictionary with the question, reasoning, and answer
    """
    # Get the appropriate template method
    if domain == "math":
        template_method = PromptTemplates.math_template
    elif domain == "logic":
        template_method = PromptTemplates.logic_template
    elif domain == "coding":
        template_method = PromptTemplates.coding_template
    elif domain == "science":
        template_method = PromptTemplates.science_template
    else:
        raise ValueError(f"Unknown domain: {domain}")
    
    # Generate initial prompt and get first reasoning step
    initial_prompt = template_method(question)
    reasoning_steps = []
    
    # First reasoning step
    current_reasoning = client.generate(initial_prompt)
    reasoning_steps.append(current_reasoning)
    combined_reasoning = current_reasoning
    
    # Additional reasoning steps
    for _ in range(1, steps):
        next_prompt = template_method(question, combined_reasoning)
        next_step = client.generate(next_prompt)
        reasoning_steps.append(next_step)
        combined_reasoning = combined_reasoning + "\n\n" + next_step
    
    # Generate final answer
    final_prompt = PromptTemplates.final_answer_template(
        question, combined_reasoning, domain
    )
    final_answer = client.generate(final_prompt)
    
    return {
        "question": question,
        "domain": domain,
        "reasoning_steps": reasoning_steps,
        "final_answer": final_answer
    }

def main():
    # Initialize the Gemini client
    client = GeminiClient()
    
    # Define problems for different domains
    problems = [
        {
            "domain": "math",
            "question": "If a triangle has sides of length 3, 4, and 5, what is its area?"
        },
        {
            "domain": "logic",
            "question": "If all A are B, and all B are C, what can we conclude about A and C?"
        },
        {
            "domain": "coding",
            "question": "Write a function to find the longest palindromic substring in a given string."
        },
        {
            "domain": "science",
            "question": "Why does ice float on water while most solids sink in their liquid form?"
        }
    ]
    
    # Solve each problem using domain-specific prompts
    for problem in problems:
        print(f"\n\n{'='*80}")
        print(f"DOMAIN: {problem['domain'].upper()}")
        print(f"QUESTION: {problem['question']}")
        print(f"{'='*80}")
        
        result = solve_with_custom_prompts(
            client,
            problem["question"],
            problem["domain"],
            steps=3
        )
        
        print("\nREASONING STEPS:")
        for i, step in enumerate(result["reasoning_steps"], 1):
            print(f"\nSTEP {i}:")
            print(step)
        
        print("\nFINAL ANSWER:")
        print(result["final_answer"])

if __name__ == "__main__":
    main()