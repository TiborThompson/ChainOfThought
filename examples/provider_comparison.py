import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chain_of_thought import ChainOfThought
import time

def print_result(result, method_name):
    """Format and print a result from a Chain of Thought solver."""
    print("\n" + "="*80)
    print(f"{method_name} RESULT FOR: {result['question']}")
    print("="*80)
    
    print("\nREASONING CHAIN:")
    for i, step in enumerate(result['reasoning_steps'], 1):
        print(f"\nStep {i}:")
        print(step)
    
    print("\nFINAL ANSWER:")
    print(result["final_answer"])
    print("="*80)

def main():
    # Define a challenging problem to compare across providers
    problem = "Three cards are placed in a hat: one card is blue on both sides, one card is red on both sides, and one card is blue on one side and red on the other. You pull out a card and observe that one side is blue. What is the probability that the other side is also blue?"
    
    # Create both OpenAI and Gemini solvers
    print("Creating solvers for OpenAI and Gemini...")
    openai_cot = ChainOfThought(provider="openai", model="gpt-4o")
    gemini_cot = ChainOfThought(provider="gemini", model="gemini-2.0-flash")
    
    # Solve with OpenAI
    print("\nSolving with OpenAI GPT-4o...")
    start_time = time.time()
    openai_result = openai_cot.solve(problem, steps=3)
    openai_time = time.time() - start_time
    print(f"OpenAI completed in {openai_time:.2f} seconds")
    
    # Solve with Gemini 
    # Note: Commenting this out by default since you mentioned rate limits for Gemini
    """
    print("\nSolving with Gemini Flash...")
    start_time = time.time()
    gemini_result = gemini_cot.solve(problem, steps=3)
    gemini_time = time.time() - start_time
    print(f"Gemini completed in {gemini_time:.2f} seconds")
    """
    
    # Print results
    print_result(openai_result, "OPENAI GPT-4O")
    # Print Gemini results if uncommented above
    # print_result(gemini_result, "GEMINI FLASH")
    
    """
    # Compare performance
    print("\nPERFORMANCE COMPARISON:")
    print(f"OpenAI GPT-4o: {openai_time:.2f} seconds")
    print(f"Gemini Flash: {gemini_time:.2f} seconds")
    print(f"Difference: {abs(openai_time - gemini_time):.2f} seconds")
    print(f"OpenAI is {(gemini_time / openai_time):.2f}x {'faster' if openai_time < gemini_time else 'slower'} than Gemini")
    """

if __name__ == "__main__":
    main()