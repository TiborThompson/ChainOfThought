import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chain_of_thought import ChainOfThought

# Create a Chain of Thought solver
cot = ChainOfThought()

# Simple example
question = "If a rectangle has a length of 10 cm and width of 5 cm, what is its area?"
print(f"Question: {question}\n")

# Solve with 2 steps to keep it fast
result = cot.solve(question, steps=2)

# Display the result
print("REASONING STEPS:")
for i, step in enumerate(result['reasoning_steps'], 1):
    print(f"\nStep {i}:")
    print(step)

print("\nFINAL ANSWER:")
print(result["final_answer"])