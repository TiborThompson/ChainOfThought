from .llm_client_factory import LLMClientFactory

class ChainOfThought:
    """
    Implements the Chain of Thought prompting technique.
    
    This class creates a step-by-step reasoning approach using
    either OpenAI or Gemini LLMs. It breaks reasoning into
    explicit steps and provides both reasoning chains and final answers.
    """
    
    def __init__(self, provider="openai", **kwargs):
        """
        Initialize the Chain of Thought handler.
        
        Args:
            provider (str, optional): LLM provider to use ("openai" or "gemini"). Defaults to "openai".
            **kwargs: Additional arguments to pass to the client constructor
                For OpenAI: model (defaults to "gpt-4o")
                For Gemini: api_key, model (defaults to "gemini-2.0-flash")
        """
        self.client = LLMClientFactory.create_client(provider=provider, **kwargs)
        # Use standardized delimiters for detecting answers
        self.answer_delimiter_start = "FINAL_ANSWER:"
        self.answer_delimiter_end = "END_ANSWER"
    
    def solve(self, question, steps=3, temperature=0.7):
        """
        Solve a problem using Chain of Thought prompting.
        
        Args:
            question (str): The question or problem to solve.
            steps (int, optional): Number of reasoning steps. Defaults to 3.
            temperature (float, optional): Temperature for generation. Defaults to 0.7.
            
        Returns:
            dict: A dictionary containing the question, reasoning chains, and final answer.
        """
        # Initialize step 1
        initial_prompt = self._create_initial_prompt(question)
        reasoning_steps = []
        
        # Step 1: Get initial reasoning
        initial_reasoning = self.client.generate(initial_prompt, temperature=temperature)
        reasoning_steps.append(initial_reasoning)
        
        # Steps 2 to n-1: Continue reasoning
        for i in range(1, steps-1):
            continuation_prompt = self._create_continuation_prompt(
                question, reasoning_steps, i+1
            )
            next_step = self.client.generate(continuation_prompt, temperature=temperature)
            reasoning_steps.append(next_step)
        
        # Final step: Get the answer
        final_prompt = self._create_final_prompt(question, reasoning_steps)
        final_answer = self.client.generate(final_prompt, temperature=temperature)
        
        return {
            "question": question,
            "reasoning_steps": reasoning_steps,
            "final_answer": final_answer
        }
    
    def _create_initial_prompt(self, question):
        """Create the initial prompt for starting the reasoning chain."""
        return f"""
Question: {question}

I need to solve this problem by thinking step-by-step.

IMPORTANT: When you reach your final answer, provide the answer in decimal format (not as a fraction), 
rounded to 2 decimal places if needed. Put your final numerical answer within these delimiters:
{self.answer_delimiter_start} [your numerical answer here, as a decimal] {self.answer_delimiter_end}

Step 1: Let me break down what the question is asking and identify key information.
"""
    
    def _create_continuation_prompt(self, question, previous_steps, current_step):
        """Create a prompt to continue the reasoning process."""
        previous_reasoning = "\n\n".join(previous_steps)
        return f"""
Question: {question}

I'm solving this problem step-by-step. Here's my reasoning so far:

{previous_reasoning}

Let me continue with the next step in my reasoning:

Step {current_step}: 
"""
    
    def _create_final_prompt(self, question, reasoning_steps):
        """Create a prompt to generate the final answer."""
        full_reasoning = "\n\n".join(reasoning_steps)
        return f"""
Question: {question}

I've reasoned through this problem as follows:

{full_reasoning}

Based on this complete chain of reasoning, I need to provide my final answer now.

IMPORTANT: My final answer must be in decimal format (not as a fraction), rounded to 2 decimal places if needed.
I will put my numerical answer within these delimiters:

{self.answer_delimiter_start} [numerical answer in decimal format] {self.answer_delimiter_end}

My final answer is:
"""