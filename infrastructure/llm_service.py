from langchain_core.messages import HumanMessage, SystemMessage
from core.config import settings


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.setup_client()
        
    def setup_client(self):
        if self.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                self.client = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                    model="nex-agi/deepseek-v3.1-nex-n1:free",
                    temperature=0.1,
                    max_tokens=1000
                )
            except ImportError:
                raise ImportError("LangChain OpenAI library not installed. Install with: pip install langchain-openai")
        elif self.provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                self.client = ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-sonnet-20240229",
                    temperature=0.1,
                    max_tokens=1000
                )
            except ImportError:
                raise ImportError("LangChain Anthropic library not installed. Install with: pip install langchain-anthropic")
        elif self.provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.client = ChatGoogleGenerativeAI(
                    api_key=settings.GOOGLE_API_KEY,
                    model="gemini-1.5-flash",
                    temperature=0.1,
                    max_tokens=1000
                )
            except ImportError:
                raise ImportError("LangChain Google GenAI library not installed. Install with: pip install langchain-google-genai")
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
        messages = [
            SystemMessage(content="You are a helpful university assistant."),
            HumanMessage(content=f"Question: {prompt}")
        ]
        response = await self.client.ainvoke(messages)
        return response.content
    

    async def _anthropic_generate(self, prompt: str, **kwargs) -> str:
        messages = [
            SystemMessage(content="You are a helpful university assistant."),
            HumanMessage(content=f"Question: {prompt}")
        ]
        response = await self.client.ainvoke(messages)
        return response.content

    async def _google_generate(self, prompt: str, **kwargs) -> str:
        messages = [
            SystemMessage(content="You are a helpful university assistant."),
            HumanMessage(content=f"Question: {prompt}")
        ]
        response = await self.client.ainvoke(messages)
        return response.content