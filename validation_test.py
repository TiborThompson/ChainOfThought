import sys
import os
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.dynamic_cot import DynamicChainOfThought
from src.chain_of_thought import ChainOfThought
from src.llm_client_factory import LLMClientFactory

def extract_answer(text):
    """Extract numerical answers from text."""
    # First try to extract from FINAL_ANSWER: format
    delimiter_pattern = r"FINAL_ANSWER:(.*?)END_ANSWER"
    delimiter_match = re.search(delimiter_pattern, text, re.DOTALL)
    if delimiter_match:
        answer_text = delimiter_match.group(1).strip()
        # Remove brackets if present
        answer_text = re.sub(r'^\[|\]$', '', answer_text).strip()
        # Try to convert to float first
        try:
            return str(float(answer_text))
        except ValueError:
            # If not a simple number, return the extracted text
            return answer_text
    
    # Look for common fraction formats and convert to decimal
    fraction_match = re.search(r'\b(\d+)/(\d+)\b', text)
    if fraction_match:
        try:
            numerator = int(fraction_match.group(1))
            denominator = int(fraction_match.group(2))
            if denominator != 0:
                decimal_value = numerator / denominator
                return str(round(decimal_value, 2))
        except (ValueError, ZeroDivisionError):
            pass
    
    # Check for percentage answers
    percent_match = re.search(r'(\d+\.?\d*)%', text)
    if percent_match:
        try:
            return percent_match.group(1)
        except ValueError:
            pass
    
    # Fall back to original method - look for numbers in the text
    numbers = re.findall(r'\b\d+\.?\d*\b', text)
    if numbers:
        return numbers[-1]  # Return the last number found
    
    return None

def validate_answer(expected, actual, tolerance=0.03):
    """Validate if the actual answer matches the expected answer."""
    if expected is None or actual is None:
        return False
    
    # Clean the inputs - remove brackets and extra spaces
    if isinstance(expected, str):
        expected = re.sub(r'^\[|\]$', '', expected).strip()
    if isinstance(actual, str):
        actual = re.sub(r'^\[|\]$', '', actual).strip()
        
    # Try handling special fraction cases like 2/3 vs 0.67
    try:
        # Check if expected is a fraction
        if '/' in str(expected):
            num, denom = map(float, str(expected).split('/'))
            expected_num = num / denom
        else:
            expected_num = float(expected)
            
        # Check if actual is a fraction
        if '/' in str(actual):
            num, denom = map(float, str(actual).split('/'))
            actual_num = num / denom
        else:
            actual_num = float(actual)
        
        # Special case for percentages vs decimal representation (0.60 vs 60)
        if expected_num > 1 and actual_num < 1 and expected_num == actual_num * 100:
            return True
        if actual_num > 1 and expected_num < 1 and actual_num == expected_num * 100:
            return True
            
        # More generous tolerance for comparing fractions
        return abs(expected_num - actual_num) <= tolerance
        
    except (ValueError, TypeError, ZeroDivisionError):
        # If conversion fails, do string comparison
        return str(expected).strip() == str(actual).strip()

# Much more challenging problems that require careful reasoning
test_problems = [
    {
        "question": "If 6 workers can build 6 tables in 6 days, how many days would it take 12 workers to build 12 tables?",
        "expected_answer": "6"
    },
    {
        "question": "Three cards are placed in a hat: one card is blue on both sides, one card is red on both sides, and one card is blue on one side and red on the other. You pull out a card and observe that one side is blue. What is the probability that the other side is also blue?",
        "expected_answer": "0.67"
    },
    {
        "question": "A population of bacteria doubles every 10 minutes. If you start with 1 bacterium and the petri dish is completely full after 5 hours, at what time was the dish 1/4 full?",
        "expected_answer": "4.67"
    },
    {
        "question": "In a game show, you're given the choice of three doors. Behind one door is a car; behind the others, goats. You pick door #1. The host, who knows what's behind the doors, opens door #3, which has a goat. He then asks if you want to switch to door #2. What is the probability of winning the car if you switch?",
        "expected_answer": "0.67"
    },
    {
        "question": "If a train travels 60 miles per hour, how far will it travel in 2.5 hours?",
        "expected_answer": "150"
    },
    {
        "question": "A farmer has 20 chickens, 15 cows, and 10 pigs. How many total legs are there?",
        "expected_answer": "140"
    },
    {
        "question": "A store sells apples for $1.20 each. If you buy 5 apples, how much will you pay?",
        "expected_answer": "6"
    },
    {
        "question": "If a rectangle has a width of 4 cm and a length of 9 cm, what is its area?",
        "expected_answer": "36"
    },
    {
        "question": "The sum of three consecutive even numbers is 48. What is the smallest number?",
        "expected_answer": "14"
    },
    {
        "question": "A cup is filled with 80% coffee. If you remove 25% of the liquid and replace it with milk, what percentage of coffee remains?",
        "expected_answer": "60"
    },
    {
        "question": "A worker can complete a job in 10 hours. If two identical workers do the same job together, how long will it take?",
        "expected_answer": "5"
    },
    {
        "question": "If you flip a fair coin 3 times, what is the probability that you get exactly 2 heads?",
        "expected_answer": "0.375"
    }
]


def main():
    # Choose LLM provider - default to OpenAI but allow command line override
    provider = "openai"  # Default to OpenAI
    if len(sys.argv) > 1 and sys.argv[1].lower() == "gemini":
        provider = "gemini"  # Use Gemini if specified

    # Initialize all three solvers using the selected provider
    dynamic_cot = DynamicChainOfThought(provider=provider)
    fixed_cot = ChainOfThought(provider=provider)
    regular_client = LLMClientFactory.create_client(provider=provider)
    
    # Track results for each approach
    results = {
        "dynamic_cot": {"passed": 0, "failed": 0},
        "fixed_cot": {"passed": 0, "failed": 0},
        "regular": {"passed": 0, "failed": 0}
    }
    failures = []
    
    print(f"Running validation tests comparing three approaches using {provider.upper()}...\n")
    
    for i, problem in enumerate(test_problems, 1):
        print(f"Test {i}: {problem['question']}")
        print(f"Expected answer: {problem['expected_answer']}")
        print("-" * 80)
        
        # Test 1: Dynamic Chain of Thought
        print("\n1. Testing with Dynamic Chain of Thought:")
        dynamic_result = dynamic_cot.solve(problem['question'], max_steps=5)
        dynamic_answer = extract_answer(dynamic_result['final_answer'])
        dynamic_correct = validate_answer(problem['expected_answer'], dynamic_answer)
        
        if dynamic_correct:
            results["dynamic_cot"]["passed"] += 1
            print(f"YAY: Dynamic CoT CORRECT: Got {dynamic_answer}, expected {problem['expected_answer']}")
        else:
            results["dynamic_cot"]["failed"] += 1
            print(f"WRONG! Dynamic CoT WRONG: Got {dynamic_answer}, expected {problem['expected_answer']}")
            failures.append({
                "method": "Dynamic CoT",
                "question": problem['question'],
                "expected": problem['expected_answer'],
                "got": dynamic_answer,
                "steps": dynamic_result.get('steps_taken', len(dynamic_result['reasoning_steps']) + 1),
                "full_answer": dynamic_result['final_answer']
            })
        
        print(f"   Steps taken: {dynamic_result.get('steps_taken', len(dynamic_result['reasoning_steps']) + 1)}")
        
        # Test 2: Fixed Chain of Thought
        print("\n2. Testing with Fixed Chain of Thought (3 steps):")
        fixed_result = fixed_cot.solve(problem['question'], steps=3)
        fixed_answer = extract_answer(fixed_result['final_answer'])
        fixed_correct = validate_answer(problem['expected_answer'], fixed_answer)
        
        if fixed_correct:
            results["fixed_cot"]["passed"] += 1
            print(f"YAY: Fixed CoT CORRECT: Got {fixed_answer}, expected {problem['expected_answer']}")
        else:
            results["fixed_cot"]["failed"] += 1
            print(f"WRONG! Fixed CoT WRONG: Got {fixed_answer}, expected {problem['expected_answer']}")
            failures.append({
                "method": "Fixed CoT",
                "question": problem['question'],
                "expected": problem['expected_answer'],
                "got": fixed_answer,
                "full_answer": fixed_result['final_answer']
            })
        
        # Test 3: Regular direct prompt with standardized format
        print("\n3. Testing with direct prompt:")
        regular_prompt = f"Question: {problem['question']}\n\nSolve this problem step by step."
        regular_result = regular_client.generate(regular_prompt, use_standard_format=True)
        regular_answer = extract_answer(regular_result)
        regular_correct = validate_answer(problem['expected_answer'], regular_answer)
        
        if regular_correct:
            results["regular"]["passed"] += 1
            print(f"YAY: Regular CORRECT: Got {regular_answer}, expected {problem['expected_answer']}")
        else:
            results["regular"]["failed"] += 1
            print(f"WRONG! Regular WRONG: Got {regular_answer}, expected {problem['expected_answer']}")
            failures.append({
                "method": "Regular",
                "question": problem['question'],
                "expected": problem['expected_answer'],
                "got": regular_answer,
                "full_answer": regular_result
            })
        
        print("\n" + "="*80 + "\n")
    
    # Print summary
    print(f"\nRESULTS SUMMARY ({provider.upper()}):")
    print("-" * 40)
    
    # Calculate success rates
    dynamic_total = results["dynamic_cot"]["passed"] + results["dynamic_cot"]["failed"]
    fixed_total = results["fixed_cot"]["passed"] + results["fixed_cot"]["failed"]
    regular_total = results["regular"]["passed"] + results["regular"]["failed"]
    
    dynamic_rate = (results["dynamic_cot"]["passed"] / dynamic_total * 100) if dynamic_total else 0
    fixed_rate = (results["fixed_cot"]["passed"] / fixed_total * 100) if fixed_total else 0
    regular_rate = (results["regular"]["passed"] / regular_total * 100) if regular_total else 0
    
    print(f"1. Dynamic Chain of Thought: {results['dynamic_cot']['passed']}/{dynamic_total} correct ({dynamic_rate:.1f}%)")
    print(f"2. Fixed Chain of Thought:   {results['fixed_cot']['passed']}/{fixed_total} correct ({fixed_rate:.1f}%)")
    print(f"3. Regular Prompting:        {results['regular']['passed']}/{regular_total} correct ({regular_rate:.1f}%)")
    
    if failures:
        print("\nULTIMATE FAILURES:") 
        print("-" * 40)
        for i, failure in enumerate(failures, 1):
            print(f"{i}. Method: {failure['method']}")
            print(f"   Question: {failure['question']}")
            print(f"   Expected: {failure['expected']}")
            print(f"   Got: {failure['got']}")
            if "steps" in failure:
                print(f"   Steps taken: {failure['steps']}")
            print(f"   Full answer: {failure['full_answer'][:100]}..." if len(failure['full_answer']) > 100 else f"   Full answer: {failure['full_answer']}")
            print()
    
    return results

if __name__ == "__main__":
    main()