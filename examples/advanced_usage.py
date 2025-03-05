import sys
import os
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chain_of_thought import ChainOfThought

def main():
    # Create a Chain of Thought solver with custom parameters
    cot = ChainOfThought()
    
    # Try different types of problems with varying step counts and temperatures
    problems = [
        {
            "type": "math",
            "question": "A rectangle has a length of 10 units and a width of 6 units. What is the area of the rectangle?",
            "steps": 2,
            "temperature": 0.2
        },
        {
            "type": "logic",
            "question": "All cats have tails. Fluffy is a cat. Does Fluffy have a tail?",
            "steps": 3,
            "temperature": 0.5
        },
        {
            "type": "complex_math",
            "question": "If it takes 6 workers 7 days to build a wall, how long would it take 3 workers to build the same wall?",
            "steps": 4,
            "temperature": 0.7
        },
        {
            "type": "reasoning",
            "question": "Tom is twice as old as Jerry was when Tom was as old as Jerry is now. If Jerry is 24 years old, how old is Tom?",
            "steps": 5,
            "temperature": 0.3
        }
    ]
    
    # Process each problem and save results
    results = []
    
    for problem in problems:
        print(f"\nSolving {problem['type']} problem with {problem['steps']} steps...")
        
        result = cot.solve(
            question=problem["question"],
            steps=problem["steps"],
            temperature=problem["temperature"]
        )
        
        # Add problem metadata to result
        result["problem_type"] = problem["type"]
        result["steps_requested"] = problem["steps"]
        result["temperature"] = problem["temperature"]
        
        results.append(result)
        
        # Print condensed result
        print(f"Question: {result['question']}")
        print(f"Answer: {result['final_answer'][:100]}..." if len(result['final_answer']) > 100 else f"Answer: {result['final_answer']}")
    
    # Save all results to a JSON file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAll results saved to {output_path}")

if __name__ == "__main__":
    main()