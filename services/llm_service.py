from core.config import settings


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.setup_client()
        
    def setup_client(self):
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL
                )
            except ImportError:
                raise ImportError("OpenAI library not installed. Install with: pip install openai")
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except ImportError:
                raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        elif self.provider == "google":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.client = genai.GenerativeModel('gemini-1.5-flash')  # Using a common model
            except ImportError:
                raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        if self.provider == "openai":
            return await self._openai_generate(prompt, **kwargs)
        elif self.provider == "anthropic":
            return await self._anthropic_generate(prompt, **kwargs)
        elif self.provider == "google":
            return await self._google_generate(prompt, **kwargs)
        
    async def _openai_generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=kwargs.get("model", "nex-agi/deepseek-v3.1-nex-n1:free"),
            messages=[
                {"role": "system", "content": "You are a helpful university assistant."},
                {"role": "user", "content": f"Question: {prompt}"}
            ],
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        return response.choices[0].message.content
    

    async def _anthropic_generate(self, prompt: str, **kwargs) -> str:
        message = self.client.messages.create(
            model=kwargs.get("model", "claude-3-sonnet-20240229"),
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.1),
            system="You are a helpful university assistant.",
            messages=[{
                "role": "user",
                "content": f"Question: {prompt}"
            }]
        )
        return message.content[0].text

    async def _google_generate(self, prompt: str, **kwargs) -> str:
        response = self.client.generate_content(prompt)
        return response.text