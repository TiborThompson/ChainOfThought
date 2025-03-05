import sys
import os
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.dynamic_cot import DynamicChainOfThought
from src.gemini_client import GeminiClient

def extract_answer(text):
    """Extract numerical answers from text."""
    # Look for numbers in the text
    numbers = re.findall(r'\b\d+\.?\d*\b', text)
    if numbers:
        return numbers[-1]  # Return the last number found
    return None

# Choose a challenging problem (Monty Hall problem, which is often misunderstood)
problem = {
    "question": "In a game show, you're given the choice of three doors. Behind one door is a car; behind the others, goats. You pick door #1. The host, who knows what's behind the doors, opens door #3, which has a goat. He then asks if you want to switch to door #2. What is the probability of winning the car if you switch?",
    "expected_answer": "0.67"  # or 2/3
}

def main():
    # Initialize the Dynamic Chain of Thought solver and regular client
    dynamic_cot = DynamicChainOfThought()
    regular_client = GeminiClient()
    
    print("PROBLEM:")
    print(problem["question"])
    print(f"Expected answer: {problem['expected_answer']}")
    print("\n" + "="*80 + "\n")
    
    # Test with regular prompt first
    print("TESTING WITH DIRECT PROMPT:")
    regular_result = regular_client.generate(problem["question"])
    regular_answer = extract_answer(regular_result)
    
    print(f"Regular Answer: {regular_answer}")
    print("\nFull response:")
    print(regular_result)
    print("\n" + "="*80 + "\n")
    
    # Test with Dynamic Chain of Thought
    print("TESTING WITH DYNAMIC CHAIN OF THOUGHT:")
    cot_result = dynamic_cot.solve(problem["question"], max_steps=5)
    cot_answer = extract_answer(cot_result["final_answer"])
    
    print(f"Dynamic CoT Answer: {cot_answer}")
    print(f"Steps taken: {cot_result.get('steps_taken', len(cot_result['reasoning_steps']) + 1)}")
    
    print("\nReasoning Steps:")
    for i, step in enumerate(cot_result["reasoning_steps"], 1):
        print(f"\nStep {i}:")
        print(step)
    
    print("\nFinal Answer:")
    print(cot_result["final_answer"])
    
    # Compare results
    print("\n" + "="*80)
    print(f"Regular answer: {regular_answer}")
    print(f"Dynamic CoT answer: {cot_answer}")
    print(f"Expected answer: {problem['expected_answer']}")
    
    # Success?
    reg_success = validate_answer(problem["expected_answer"], regular_answer, tolerance=0.1)
    cot_success = validate_answer(problem["expected_answer"], cot_answer, tolerance=0.1)
    
    print(f"\nRegular prompt got it {'✅ RIGHT' if reg_success else '❌ WRONG'}")
    print(f"Dynamic Chain of Thought got it {'✅ RIGHT' if cot_success else '❌ WRONG'}")

def validate_answer(expected, actual, tolerance=0.01):
    """Validate if the actual answer matches the expected answer."""
    try:
        expected_num = float(expected)
        actual_num = float(actual)
        return abs(expected_num - actual_num) <= tolerance
    except (ValueError, TypeError):
        # If conversion fails, do string comparison
        return str(expected).strip() == str(actual).strip()

if __name__ == "__main__":
    main()