import csv
import os
from users.service import UserService
from course.interface.service import CourseService
from student.models import *
from student.serializers import *
from student.repository import ConversationRepository, ChatlogRepository, FeedbackRepository, ReportRepository, ConversationNotesRepository
from models.repository.model_repository import *
from utils import *

log = get_logger(__name__)

class ConversationService:

    def get_conversation(conversation_id: str):
        conversation = ConversationRepository.find_conversation_by_id(conversation_id)
        if conversation is None:
            raise NotFoundError(f"Conversation {conversation_id} not found ")
        return conversation

    def create_conversation(model_id: str, data: dict):
        if model_id: ModelRepository.find_model_by_id(model_id)
        return ConversationRepository.create_conversation(data)
        
    def get_all_conversations(user_id, course_id = "", detailed = False):
        if user_id:
            return ConversationRepository.find_conversations_by_user_id(user_id)
        if course_id:
            return ConversationRepository.find_conversations_by_course_id(course_id, detailed)
        return ConversationRepository.find_all_conversations()
    
    def get_conversation_history(conversation_id: str):
        return ConversationRepository.get_conversation_history(conversation_id)
    

    def get_conversation_history_csv(conversation_history, response) -> HttpResponse:
        user = UserService.get_user(conversation_history["user_id"])
        name = UserService.get_user_full_name(user)

        writer = csv.writer(response)
        writer.writerow(['Time', 'Speaker', 'Message'])
        for chatlog in conversation_history["chatlogs"]:
            formatted_time = chatlog["time"].strftime("%Y-%m-%d %H:%M:%S")
            speaker = name if chatlog["is_user"] else os.getenv("DEPLOYMENT_NAME")
            writer.writerow(['[' + formatted_time + ']', speaker, str(chatlog["chatlog"])])
        return response
    
    def get_conversation_chatlogs(conversation_id: str, show_metadata: bool = False):
        chatlogs = ChatlogRepository.get_chatlogs_by_conversation_id(conversation_id)

        for chatlog in chatlogs:
            server_formatted_time = get_server_time(chatlog["time"], SERVER_TIMEZONE)
            chatlog["time"] = server_formatted_time

            if not(isFalse(show_metadata)) and "sentiment" not in chatlog:
                log.info(f"Acquring sentiment analysis for chatlog with {chatlog.get('_id')}")
                flair = FlairSentimentAnalysis()
                flair.get_all_sentiment_scores(chatlogs=[{ "_id": chatlog.get('_id'), "chatlog": chatlog["chatlog"]}])
                flair.save_sentiment_scores()
                value, score = flair.scores[0]["value"], flair.scores[0]["score"]
                chatlog["sentiment"] = {"flair": {"value": value, "score": score }}

            if not(show_metadata):
                del chatlog["delta"]
                del chatlog["sentiment"]

        return chatlogs
    
    def exists(conversation_id: str):
        if (ConversationRepository.find_conversation_by_id(conversation_id) is None):
            raise NotFoundError("Conversation not found")
        
    def get_conversations_by_user_course(user_id: str, course_id: str, model_ids: List[str]):
        conversations = ConversationRepository.find_conversations_by_user_course_models(user_id, course_id, model_ids)
        for conversation in conversations:
            conversation.pop("conversation_log")
        return conversations
    
    def model_usage(model_id: str) -> bool:
        if ConversationRepository.find_conversation_by_model_id(model_id):
            return True 
        return False
    
    def end_conversation(conversation_id: str):
        updated_conversation_fields = {"status": "I", "end_time": datetime.now()}
        ConversationRepository.update_conversation(conversation_id, updated_conversation_fields)
        conversation = ConversationRepository.find_conversation_by_id(conversation_id)
        return conversation
    
    def update_conversation_name(conversation_id: str, name: str):
        ConversationService.exists(conversation_id)
        return ConversationRepository.update_conversation(conversation_id, {"conversation_name": name})

    @staticmethod
    def grade_conversation(conversation_id: str):
        updated_conversation_fields = {"graded": True}
        ConversationRepository.update_conversation(conversation_id, updated_conversation_fields)
        conversation = ConversationRepository.find_conversation_by_id(conversation_id)
        print(conversation, conversation_id)
        return conversation
    
    @staticmethod
    def update_conversation(conversation_id: str, data: dict):
        ConversationService.exists(conversation_id)
        return ConversationRepository.update_conversation(conversation_id, data)
    
    
class ChatlogService:
    
    def get_system_message(system_prompt: Dict[any, any]):
        strategy = system_prompt.get("strategy_prompt")
        problem = system_prompt.get("problem_context")
        prior_knowledge = system_prompt.get("learner_knowledge")
        code = system_prompt.get("code_context")
        
        system_message = f"""
        ### Instruction for construction this certain type of output
        {strategy}
        
        ### Learner's Context Information
        {problem}
        
        ### Learner's Prior Knowledge
        {prior_knowledge}
        
        ### Code Context
        {code}
        """
        
        return system_message
   
    def get_all_chatlogs():
        return ChatlogRepository.find_all_chatlogs()
    
    def get_delta(conversation_id: str, time: str):
        delta = 0
        last_chatlog = ChatlogRepository.get_last_chatlog(conversation_id)
        if last_chatlog and not(last_chatlog["is_user"]):
            time = datetime.strptime(time[:19], "%Y-%m-%dT%H:%M:%S")
            delta = (time - last_chatlog["time"]).total_seconds()
        return delta

    def create_user_chatlog(conversation_id: str, user_message: str):
        data = {
            "chatlog": user_message,
            "conversation_id": conversation_id,
            "time": datetime.now(),
            "is_user": True,
        }
        return ChatlogRepository.create_chatlog(data)
    
    def create_agent_chatlog(conversation_id: str, model_response: str):
        agent_chatlog = {
            "chatlog": model_response,
            "conversation_id": conversation_id,
            "time": datetime.now(),
            "is_user": False,
        }
        return ChatlogRepository.create_chatlog(agent_chatlog)

    def to_server_time(time: str = ""):
        if time == "": 
            current_time = datetime.now(tz=pytz.utc)
            print(current_time, type(current_time))
        else:
            idx = time.find("[")
            current_time = dateparse.parse_datetime(time[:idx]).astimezone(pytz.utc)
            print(current_time, type(current_time))
        return current_time
   
    def format_responses(user, model, conversation_name):
        return {
            "conversation_name": conversation_name,
            "agent": model,
            "user": user,
        }
