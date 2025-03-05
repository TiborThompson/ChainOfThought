import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dynamic_cot import DynamicChainOfThought
from src.chain_of_thought import ChainOfThought

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
    
    if "steps_taken" in result:
        print(f"\nSteps taken: {result['steps_taken']}")
    
    print("="*80)

def main():
    # Create both types of CoT solvers
    dynamic_cot = DynamicChainOfThought()
    fixed_cot = ChainOfThought()
    
    # Define some example questions of varying complexity
    questions = [
        "What is 24 divided by 8?",  # Simple, should need few steps
        "If a rectangle has a length of 8 cm and width of 5 cm, what is its area?",  # Simple
        "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?",  # Tricky
        "If it takes 5 workers 8 days to build a wall, how many days would it take 10 workers to build the same wall?",  # More complex
        "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how many days would it take for the patch to cover half of the lake?"  # Complex
    ]
    
    # Compare dynamic vs fixed step approaches
    for i, question in enumerate(questions, 1):
        print(f"\n\nQuestion {i}: {question}")
        print("-"*80)
        
        # Solve with dynamic steps
        print(f"Solving with DYNAMIC steps...")
        dynamic_result = dynamic_cot.solve(question)
        
        # Solve with fixed steps (3)
        print(f"Solving with FIXED steps (3)...")
        fixed_result = fixed_cot.solve(question, steps=3)
        
        # Print results
        print_result(dynamic_result, "DYNAMIC COT")
        print_result(fixed_result, "FIXED COT")
        
        # Compare step counts
        dynamic_steps = dynamic_result.get("steps_taken", len(dynamic_result["reasoning_steps"]) + 1)
        fixed_steps = len(fixed_result["reasoning_steps"]) + 1
        
        print(f"\nSTEP COUNT COMPARISON:")
        print(f"Dynamic CoT used {dynamic_steps} steps")
        print(f"Fixed CoT used {fixed_steps} steps")
        
        difference = dynamic_steps - fixed_steps
        if difference < 0:
            print(f"Dynamic CoT used {abs(difference)} FEWER steps!")
        elif difference > 0:
            print(f"Dynamic CoT used {difference} MORE steps!")
        else:
            print(f"Both methods used the same number of steps.")

if __name__ == "__main__":
    main()