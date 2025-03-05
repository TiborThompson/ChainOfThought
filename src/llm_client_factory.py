from .gemini_client import GeminiClient
from .openai_client import OpenAIClient

class LLMClientFactory:
    """
    Factory class that creates appropriate LLM clients based on the provider.
    This centralizes the client creation logic.
    """
    
    @staticmethod
    def create_client(provider="openai", **kwargs):
        """
        Create an appropriate LLM client based on the requested provider.
        
        Args:
            provider (str): The LLM provider to use ("openai" or "gemini")
            **kwargs: Additional arguments to pass to the client constructor
                For OpenAI: model (defaults to "gpt-4o")
                For Gemini: api_key, model (defaults to "gemini-2.0-flash")
                
        Returns:
            An instance of the appropriate client class
        """
        provider = provider.lower()
        
        if provider == "openai":
            model = kwargs.get("model", "gpt-4o")
            return OpenAIClient(model=model)
        
        elif provider == "gemini":
            api_key = kwargs.get("api_key", None)
            model = kwargs.get("model", "gemini-2.0-flash")
            return GeminiClient(api_key=api_key, model=model)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'gemini'.")