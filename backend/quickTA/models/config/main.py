from models.config import gpt4, azure
from typing import Dict
from student.models import Conversation
from models.models import GPTModel

def get_response(conversation: Conversation, system_message: str, user_message: str) -> Dict:
    return gpt4.get_response(conversation, system_message, user_message)