import environ
import asyncio
import os
from utils import *
from student.repository import *

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain

env = environ.Env()
environ.Env.read_env()

# AZURE OPENAI API CONFIG
# openai.api_type = 'azure'
# openai.api_version = '2023-05-15'
BASE_URL = f"https://{env('AZURE_RESOURCE_NAME')}.openai.azure.com/"
API_KEY = env('AZURE_API_KEY')
DEPLOYMENT_NAME = env('AZURE_DEPLOYMENT_NAME')

# NEMO GUARDRAILS CONFIG
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["DISABLE_NEST_ASYNCIO"]= "true"

log = get_logger(__name__)

class AzureSettings:
    def __init__(self, conversation: Dict, settings: Dict) -> None:
        self.model = None
        self.azure_model = None
        
        # Conversation
        self.conversation_id = conversation.get('_id', "")
        self.conversation_name = conversation.get('conversation_name', "New Conversation")
        self.conversation_log = conversation.get('conversation_log', [])
        self.formatted_conversation_log = []
        self.start_time = conversation.get('start_time', datetime.now())            

        # Settings
        self.default_message = settings.get('default_message', "")
        self.default_conversation_name = settings.get('default_conversation_name', "")
        self.prompt = settings.get('prompt', "Please provide a response")
        self.llm_model = settings.get('model', 'gpt-3.5-turbo')

        self.summarize = settings.get('summarize', False)

        # Parameters
        self.max_tokens = settings.get('max_tokens', 200)
        self.temperature = settings.get('temperature', 0.5)
        self.top_p = settings.get('top_p', 1)
        self.frequency_penalty = settings.get('frequency_penalty', 0)
        self.presence_penalty = settings.get('presence_penalty', 0)
        self.n = settings.get('n', 1)

        self.use_guardrails = settings.get('enableGuardrails', False)

        # Initialize model
        self._init_model()
    
    def __str__(self) -> str:
        return str(self.__dict__)

    def _init_model(self):
        self._setup_model()
        self._format_conversation_log()

    def _setup_model(self) -> None:
        self.model = AzureChatOpenAI(
            azure_endpoint = BASE_URL,
            openai_api_version = "2023-05-15",
            deployment_name = DEPLOYMENT_NAME,
            openai_api_key = API_KEY,
            openai_api_type = "azure",
            max_tokens=self.max_tokens,
            model_name=self.llm_model
        )   

    def get_model(self) -> Optional[ConversationChain]:
        return self.model
    
    def _format_conversation_log(self) -> None:
      """Format conversation log for Azure model"""
      if has_conversation_history := self.conversation_log:
            self.history = []
            for message in self.conversation_log:
                MSG_ROLE, MSG_CONTENT = message['role'], message['content']
                if MSG_ROLE == "system": self.history.append(SystemMessage(content=MSG_CONTENT))
                elif MSG_ROLE == "assistant": self.history.append(AIMessage(content=MSG_CONTENT))
                elif MSG_ROLE == "user": self.history.append(HumanMessage(content=MSG_CONTENT))
      else:
          self.history = []
          self.history.append(SystemMessage(content=self.prompt))
          self.history.append(AIMessage(content=self.default_message))

    def generate_conversation_name(self, chatlog: str) -> None:
        """TODO: Can be called in parallel to the completion function."""
        
        if self.default_conversation_name:
            self.conversation_name = self.default_conversation_name
            return
        
        template = f"""
        Label this conversation with a name that is less than 6 words:
        
        Prompt: {self.prompt}
        Chatlog: {chatlog}

        Conversation name:
        """

        chain = ConversationChain(llm=self.azure_model)
        self.conversation_name = chain.predict(input=template.format(chatlog=chatlog))
        self.conversation_name = self.conversation_name.replace('"', "").replace("", "")

    def set_up_conversation(self, chatlog: str) -> None:
        """Generate new conversation or append to existing conversation"""
        if new_conversation := not self.conversation_log:
            self.history.append(HumanMessage(content=chatlog))
            create_chatlog(
                cid=self.conversation_id, 
                chatlog=self.default_message, 
                is_user=False, 
                time=self.start_time, 
                delta=None
            )
            self.generate_conversation_name(chatlog)
            self.conversation_log.append({"role": "system", "content": self.prompt})
            self.conversation_log.append({"role": "assistant", "content": self.default_message})
            self.conversation_log.append({"role": "user", "content": chatlog})
        else:
            self.conversation_log.append({"role": "user", "content": chatlog})
            pass
        self._format_conversation_log()

    async def async_predict(self, user_message: str) -> str:
        """Generate response from Azure model asynchronously"""
        
        prompt = ChatPromptTemplate.from_messages(self.history)
        output_parser = StrOutputParser()
        chain = prompt | self.model | output_parser
        
        if not self.use_guardrails:
            response = await asyncio.get_event_loop().run_in_executor(None, chain.invoke, {"input": user_message})
            pass
        else:

            prompt = ChatPromptTemplate.from_messages(self.format_conversation())
            output_parser = StrOutputParser()
            chain = prompt | self.model | output_parser

            log.info("NemoGuardrails enabled generation")
            config = RailsConfig.from_path("./models/llms/guardrails")
            chain_with_guardrails = RunnableRails(config, llm=self.model, runnable=chain)
            response = await asyncio.get_event_loop().run_in_executor(None, chain_with_guardrails.invoke, {"input": user_message})
            response = self.parse_response(response)

        self.conversation_log.append({"role": "assistant", "content": response})
        return response

    def predict(self, user_message: str) -> str:
        """Wrapper to run async predict in an event loop"""
        return asyncio.run(self.async_predict(user_message))

    def format_conversation(self) -> List[Dict]:
        """Format conversation log for Azure model with NemoGuardrails enabled"""
        formatted_conversation = []
        for message in self.conversation_log:
            MSG_ROLE, MSG_CONTENT = message['role'], message['content']
            formatted_conversation.append((MSG_ROLE, MSG_CONTENT))
        return formatted_conversation
    
    def parse_response(self, response: str) -> str:
        """
        Check if the response is a dict and parse it, if not leave it as a string
        """
        if isinstance(response, dict):
            response = response.get("output", "")
        return response


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