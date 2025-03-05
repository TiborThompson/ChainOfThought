# ChainOfThought

This project implements advanced Chain of Thought (CoT) approaches for solving complex reasoning problems using various LLM providers (OpenAI and Gemini). Chain of Thought is a prompting technique that encourages language models to break down their reasoning into explicit steps before providing a final answer, significantly enhancing accuracy and transparency.

## Concept

This project implements both fixed and dynamic chain-of-thought prompting to improve accuracy on complex reasoning tasks. Rather than building a new model, it uses prompt engineering techniques to guide models through structured reasoning processes.

The approach works by:
1. Breaking a problem into multiple thinking steps
2. Using the output from each step as input for the next prompt
3. Accumulating reasoning before arriving at a final answer
4. Using standardized answer formats for consistent extraction

## Performance

Our latest validation tests show substantial improvements with structured CoT approaches:

```
RESULTS SUMMARY (OPENAI):
----------------------------------------
1. Dynamic Chain of Thought: 11/12 correct (91.7%)
2. Fixed Chain of Thought:   12/12 correct (100.0%)
3. Regular Prompting:        10/12 correct (83.3%)
```

The project includes structured answer formats, robust answer extraction, and validation logic that handles various numerical representations (fractions, decimals, percentages).

## Project Structure

```
ChainOfThought/
├── src/
│   ├── __init__.py
│   ├── llm_client_factory.py  # Factory for creating LLM clients
│   ├── openai_client.py       # OpenAI API client
│   ├── gemini_client.py       # Gemini API client
│   ├── chain_of_thought.py    # Core CoT implementation
│   ├── dynamic_cot.py         # Dynamic step CoT implementation
│   └── custom_prompts.py      # Domain-specific prompt templates
├── examples/
│   ├── basic_usage.py         # Simple examples
│   ├── advanced_usage.py      # More complex customization
│   ├── custom_prompts_example.py  # Domain-specific prompting
│   └── provider_comparison.py  # Compare OpenAI vs Gemini
├── tests/
│   └── test_chain_of_thought.py   # Unit tests
└── validation_test.py         # Comprehensive performance benchmarks
```

## Usage

Basic usage:

```python
from src.chain_of_thought import ChainOfThought

# Initialize with OpenAI (default)
cot = ChainOfThought(provider="openai", model="gpt-4o")

# Or initialize with Gemini
# cot = ChainOfThought(provider="gemini", model="gemini-2.0-flash")

# Solve a problem with default parameters
result = cot.solve("If a train travels 120 miles in 2 hours, what is its average speed?")

# Print the result
print(f"Question: {result['question']}")
print(f"Reasoning:")
for step in result['reasoning_steps']:
    print(step)
print(f"Answer: {result['final_answer']}")
```

To use dynamic steps (automatic step count based on reasoning):

```python
from src.dynamic_cot import DynamicChainOfThought

# Initialize with OpenAI
dynamic_cot = DynamicChainOfThought(provider="openai")

# Solve with dynamic steps (model decides when to conclude)
result = dynamic_cot.solve("What is the area of a circle with radius 5?")

print(f"Steps taken: {result['steps_taken']}")
```

## Features

- **Multiple LLM Support**: Works with both OpenAI and Gemini APIs
- **Fixed & Dynamic CoT**: Both predefined step count and adaptive reasoning path options
- **Modular Design**: Separate client, CoT logic, and prompt templates
- **Rate Limiting**: Built-in rate limiting to comply with API usage limits
- **Structured Output Format**: Consistent answer delimitation for improved accuracy
- **Robust Answer Handling**: Supports various numerical formats (fractions, decimals, percentages)
- **Domain-Specific Prompts**: Optimized templates for different problem domains
- **Customizable**: Adjust number of reasoning steps and temperature

## Getting Started

1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`
3. Set your API keys:
   - For OpenAI: Create an `apis.py` file with a function `get_openai_response(prompt, modell="gpt-4o")`
   - For Gemini: `export GEMINI_API_KEY=your_key_here` or pass directly to the constructor
4. Run one of the example scripts: `python examples/basic_usage.py`

## Running the Validation Tests

To run the validation tests with OpenAI (default):
```
python validation_test.py
```

To run with Gemini:
```
python validation_test.py gemini
```

## Requirements

- Python 3.7+
- `google-generativeai` package (for Gemini)
- `openai` package (for OpenAI)

## License

MIT