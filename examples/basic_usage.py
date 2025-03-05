import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chain_of_thought import ChainOfThought

def print_result(result):
    """Format and print a result from the ChainOfThought solver."""
    print("\n" + "="*80)
    print(f"QUESTION: {result['question']}")
    print("="*80)
    
    print("\nREASONING CHAIN:")
    for i, step in enumerate(result['reasoning_steps'], 1):
        print(f"\nStep {i}:")
        print(step)
    
    print("\nFINAL ANSWER:")
    print(result["final_answer"])
    print("="*80)

def main():
    # Create a Chain of Thought solver
    cot = ChainOfThought()
    
    # Define some example questions
    questions = [
        "If a train travels 120 miles in 2 hours, what is its average speed in miles per hour?",
        "What is the value of x in the equation 3x + 7 = 22?",
        "Janet's age is 3 times the sum of her children's ages. She has 3 children aged 2, 4, and 6. How old is Janet?"
    ]
    
    # Solve each question and print the results
    for question in questions:
        result = cot.solve(question)
        print_result(result)

if __name__ == "__main__":
    main()