import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chain_of_thought import ChainOfThought

class TestChainOfThought(unittest.TestCase):
    """Tests for the ChainOfThought class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the GeminiClient
        self.mock_client_patcher = patch('src.chain_of_thought.GeminiClient')
        self.mock_client = self.mock_client_patcher.start()
        
        # Configure the mock client's generate method to return predefined responses
        self.mock_generate = MagicMock()
        self.mock_client.return_value.generate = self.mock_generate
        
        # Create an instance of ChainOfThought with the mocked client
        self.cot = ChainOfThought()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_client_patcher.stop()
    
    def test_create_initial_prompt(self):
        """Test the creation of the initial prompt."""
        question = "What is 2+2?"
        prompt = self.cot._create_initial_prompt(question)
        
        # Verify the prompt contains the question
        self.assertIn(question, prompt)
        # Verify the prompt instructs to break down the problem
        self.assertIn("break down", prompt.lower())
    
    def test_create_continuation_prompt(self):
        """Test the creation of the continuation prompt."""
        question = "What is 2+2?"
        previous_steps = ["Step 1: I need to add 2 and 2 together."]
        
        prompt = self.cot._create_continuation_prompt(question, previous_steps)
        
        # Verify the prompt contains the question and previous steps
        self.assertIn(question, prompt)
        self.assertIn(previous_steps[0], prompt)
        # Verify the prompt asks for the next step
        self.assertIn("next step", prompt.lower())
    
    def test_create_final_prompt(self):
        """Test the creation of the final prompt."""
        question = "What is 2+2?"
        reasoning_steps = [
            "Step 1: I need to add 2 and 2 together.",
            "Step 2: 2+2 equals 4."
        ]
        
        prompt = self.cot._create_final_prompt(question, reasoning_steps)
        
        # Verify the prompt contains the question and reasoning steps
        self.assertIn(question, prompt)
        for step in reasoning_steps:
            self.assertIn(step, prompt)
        # Verify the prompt asks for the final answer
        self.assertIn("final answer", prompt.lower())
    
    def test_solve(self):
        """Test the solve method of ChainOfThought."""
        question = "What is 2+2?"
        
        # Configure mock responses
        self.mock_generate.side_effect = [
            "I need to add 2 and 2 together.",  # Step 1
            "Adding 2 and 2 gives me 4.",       # Step 2
            "The answer is 4."                  # Final answer
        ]
        
        # Call the solve method
        result = self.cot.solve(question, steps=3)
        
        # Verify the result structure
        self.assertEqual(result["question"], question)
        self.assertEqual(len(result["reasoning_steps"]), 2)
        self.assertEqual(result["final_answer"], "The answer is 4.")
        
        # Verify the mock was called the expected number of times
        self.assertEqual(self.mock_generate.call_count, 3)

if __name__ == '__main__':
    unittest.main()