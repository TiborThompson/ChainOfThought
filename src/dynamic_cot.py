from .llm_client_factory import LLMClientFactory
import re

class DynamicChainOfThought:
    """
    Implements a Dynamic Chain of Thought prompting technique.
    
    Instead of using a fixed number of reasoning steps, this class
    lets the model itself decide when it has reached a conclusion
    by detecting when it's ready to provide a final answer.
    """
    
    def __init__(self, provider="openai", **kwargs):
        """
        Initialize the Dynamic Chain of Thought handler.
        
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
        
        # Fall back to these patterns if delimiters aren't found
        self.conclusion_patterns = [
            r"(?i)therefore,?\s+(?:the)?\s*(?:final)?\s*answer\s+is",
            r"(?i)(?:the)?\s*(?:final)?\s*answer\s+is",
            r"(?i)in\s+conclusion",
            r"(?i)thus,?\s+(?:the)?\s*(?:final)?\s*(?:answer|result)\s+is",
            r"(?i)(?:the)?\s*(?:final)?\s*(?:answer|result)[\s:]+",
            r"(?i)(?:so|hence),?\s+(?:the)?\s*(?:final)?\s*answer\s+is",
            r"(?i)to\s+summarize",
            r"(?i)my\s+final\s+answer",
            r"(?i)final\s+result",
            r"(?i)^\s*answer\s*[:=]"
        ]
    
    def solve(self, question, max_steps=10, temperature=0.7):
        """
        Solve a problem using Dynamic Chain of Thought prompting.
        
        Args:
            question (str): The question or problem to solve.
            max_steps (int, optional): Maximum reasoning steps. Defaults to 10.
            temperature (float, optional): Temperature for generation. Defaults to 0.7.
            
        Returns:
            dict: A dictionary with the question, reasoning chains, and final answer.
        """
        # Initialize step 1
        initial_prompt = self._create_initial_prompt(question)
        reasoning_steps = []
        combined_reasoning = ""
        
        # Step 1: Get initial reasoning
        initial_reasoning = self.client.generate(initial_prompt, temperature=temperature)
        reasoning_steps.append(initial_reasoning)
        combined_reasoning = initial_reasoning
        
        # Check if initial reasoning already contains a conclusion
        answer_found, final_answer = self._extract_answer(initial_reasoning)
        if answer_found:
            return {
                "question": question,
                "reasoning_steps": reasoning_steps,
                "final_answer": final_answer,
                "steps_taken": 1
            }
        
        # Continue reasoning until reaching a conclusion or max steps
        for step in range(2, max_steps + 1):
            continuation_prompt = self._create_continuation_prompt(
                question, combined_reasoning, step
            )
            next_reasoning = self.client.generate(continuation_prompt, temperature=temperature)
            reasoning_steps.append(next_reasoning)
            
            # Keep combined reasoning manageable by keeping only last 2 steps if too long
            if len(combined_reasoning) > 2000:
                combined_reasoning = "\n\n".join(reasoning_steps[-2:])
            else:
                combined_reasoning = combined_reasoning + "\n\n" + next_reasoning
            
            # Check if we've reached a conclusion
            answer_found, final_answer = self._extract_answer(next_reasoning)
            if answer_found:
                return {
                    "question": question,
                    "reasoning_steps": reasoning_steps,
                    "final_answer": final_answer,
                    "steps_taken": step
                }
        
        # If we hit max steps without a conclusion, generate a final answer
        final_prompt = self._create_final_prompt(question, reasoning_steps)
        final_answer_text = self.client.generate(final_prompt, temperature=temperature)
        
        # Extract the final answer using our standard format
        _, extracted_answer = self._extract_answer(final_answer_text)
        if not extracted_answer:
            # If our extraction fails, use the entire response
            extracted_answer = final_answer_text
        
        return {
            "question": question,
            "reasoning_steps": reasoning_steps,
            "final_answer": extracted_answer,
            "steps_taken": max_steps
        }
    
    def _extract_answer(self, text):
        """
        Extract the answer from text using delimiters or fallback patterns.
        Returns a tuple: (answer_found, answer_text)
        """
        # First try to extract using our explicit delimiters
        delimiter_pattern = f"{self.answer_delimiter_start}(.*?){self.answer_delimiter_end}"
        delimiter_match = re.search(delimiter_pattern, text, re.DOTALL)
        if delimiter_match:
            return True, delimiter_match.group(1).strip()
            
        # Then try our fallback patterns
        for pattern in self.conclusion_patterns:
            match = re.search(pattern, text)
            if match:
                # Get everything after the conclusion marker
                conclusion_start = match.end()
                conclusion_text = text[conclusion_start:].strip()
                return True, conclusion_text
        
        # If no patterns match, check for digits (last resort)
        if re.search(r'\d+\.?\d*', text):
            return False, None
            
        # If nothing found, return the last paragraph as a fallback
        paragraphs = text.split('\n\n')
        return False, paragraphs[-1].strip()
    
    def _create_initial_prompt(self, question):
        """Create the initial prompt for starting the reasoning chain."""
        return f"""
Question: {question}

I need to solve this problem by thinking step-by-step. 
Let me work through this carefully:

IMPORTANT: When you reach your final answer, provide the answer in decimal format (not as a fraction), 
rounded to 2 decimal places if needed. Put your final numerical answer within these delimiters:
{self.answer_delimiter_start} [your numerical answer here, as a decimal] {self.answer_delimiter_end}

Step 1: Let me break down what the question is asking and identify the key information.
"""
    
    def _create_continuation_prompt(self, question, previous_reasoning, current_step):
        """Create a prompt to continue the reasoning process."""
        return f"""
Question: {question}

I'm solving this problem step-by-step. Here's my reasoning so far:

{previous_reasoning}

Let me continue my reasoning:

Step {current_step}: 

IMPORTANT: If you're ready to provide a final answer, make sure to format it like this:
{self.answer_delimiter_start} [your numerical answer in decimal format, rounded to 2 decimal places if needed] {self.answer_delimiter_end}
"""
    
    def _create_final_prompt(self, question, reasoning_steps):
        """Create a prompt to generate the final answer."""
        # Use only the last two steps if there are too many
        if len(reasoning_steps) > 3:
            selected_steps = reasoning_steps[-3:]
            summary = "(...previous steps omitted...)\n\n" + "\n\n".join(selected_steps)
        else:
            summary = "\n\n".join(reasoning_steps)
            
        return f"""
Question: {question}

I've reasoned through this problem as follows:

{summary}

Based on this complete chain of reasoning, I need to provide my final answer now.

IMPORTANT: My final answer must be in decimal format (not as a fraction), rounded to 2 decimal places if needed.
I will put my numerical answer within these delimiters:

{self.answer_delimiter_start} [numerical answer in decimal format] {self.answer_delimiter_end}

My final answer is:
"""