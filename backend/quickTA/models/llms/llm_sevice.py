from enum import Enum
from ..config import gpt4, azure

class LLMType(Enum):
    GPT4 = "gpt4"
    AZURE = "azure"

class LLMService:
    def get_completion(llm: LLMType, system_message: str, user_message: str):
      if llm == LLMType.GPT4:
        return gpt4.get_completion(system_message, user_message)
      if llm == LLMType.AZURE:
        return azure.get_completion(system_message, user_message)