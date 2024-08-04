import uuid
import openai
import environ
from utils import *
from student.models import Conversation
from models.models import GPTResponse
from student.models import Chatlog
from datetime import timedelta
from student.repository import *

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ChatMessageHistory

from models.llms.azure_settings import AzureSettings

log = get_logger(__name__)

env = environ.Env()
environ.Env.read_env()

BASE_URL = f"https://{env('AZURE_RESOURCE_NAME')}.openai.azure.com/"
API_KEY = env('AZURE_API_KEY')
DEPLOYMENT_NAME = env('AZURE_DEPLOYMENT_NAME')

# openai.api_type = 'azure'
# openai.api_version = '2023-05-15'

def completion(conversation: Dict, settings: Dict, chatlog: str):
    azure = AzureSettings(conversation, settings)
    azure.set_up_conversation(chatlog)

    # Acquire azure gpt response
    output = azure.predict(user_message=chatlog)

    # Post response processing
    ConversationRepository.add_chatlog_history(azure.conversation_id, azure.conversation_log, azure.conversation_name)
    return output, azure.conversation_name

def get_response(conversation, settings, chatlog):
    response, conversation_name = completion(conversation, settings, chatlog)
    if not response: response = "Sorry for the invconvenience. Currently having difficulties. Please try again later."
    return response, conversation_name

def create_chatlog(cid, chatlog, is_user, time, delta):
    chatlog = {
        "_id": uuid4(),
        "conversation_id": cid,
        "time": time,
        "is_user": is_user,
        "chatlog": chatlog,
        "delta": delta
    }
    ChatlogRepository.create_chatlog(chatlog)
    return chatlog

def get_completion(message):
    # NOT IMPLEMENTED
    pass