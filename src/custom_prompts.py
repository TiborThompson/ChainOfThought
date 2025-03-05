class PromptTemplates:
    """
    Collection of prompt templates for different Chain of Thought strategies.
    
    This allows for customizing the prompting approach based on the type
    of problem or domain of knowledge.
    """
    
    @staticmethod
    def math_template(question, reasoning=""):
        """Template optimized for mathematical problem solving."""
        if not reasoning:
            return f"""
Question: {question}

I'll solve this step-by-step:

1) First, I need to identify the mathematical concepts and variables involved.
"""
        else:
            return f"""
Question: {question}

My step-by-step solution:

{reasoning}

Continuing my solution:
"""
    
    @staticmethod
    def logic_template(question, reasoning=""):
        """Template optimized for logical reasoning problems."""
        if not reasoning:
            return f"""
Question: {question}

I'll approach this logical problem systematically:

1) Let me identify the premises and what I need to determine.
"""
        else:
            return f"""
Question: {question}

My logical reasoning so far:

{reasoning}

Next in my reasoning chain:
"""
    
    @staticmethod
    def coding_template(question, reasoning=""):
        """Template optimized for coding problems."""
        if not reasoning:
            return f"""
Coding Problem: {question}

I'll solve this by breaking it down into steps:

1) First, let me understand the problem requirements and expected inputs/outputs.
"""
        else:
            return f"""
Coding Problem: {question}

My approach so far:

{reasoning}

Next steps in my solution:
"""
    
    @staticmethod
    def science_template(question, reasoning=""):
        """Template optimized for scientific reasoning."""
        if not reasoning:
            return f"""
Scientific Question: {question}

I'll analyze this scientifically:

1) First, let me identify the relevant scientific principles and concepts.
"""
        else:
            return f"""
Scientific Question: {question}

My scientific analysis so far:

{reasoning}

Continuing my analysis:
"""
    
    @staticmethod
    def final_answer_template(question, reasoning, domain="general"):
        """Template for generating the final answer after reasoning."""
        domain_specific_instruction = ""
        
        if domain == "math":
            domain_specific_instruction = "Make sure to include the final numerical result and units if applicable."
        elif domain == "logic":
            domain_specific_instruction = "Clearly state my conclusion based on logical deduction."
        elif domain == "coding":
            domain_specific_instruction = "Provide the final code solution and explain its time/space complexity."
        elif domain == "science":
            domain_specific_instruction = "Summarize the scientific explanation and any relevant theories or principles."
        
        return f"""
Question: {question}

My complete reasoning process:

{reasoning}

Based on this reasoning, I'll now provide my final answer. {domain_specific_instruction}

Final Answer:
"""