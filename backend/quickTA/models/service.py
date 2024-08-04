from models.serializers import *
from models.repository.model_repository import ModelRepository
from models.repository.strategy_repository import StrategyRepository
from student.service import ConversationService
from course.interface.service import CourseService
from models.config.main import *
from utils import *
from random import shuffle
from users.service import UserDeploymentStatusService
from users.models.UserStatus import UserStep
from student.service import ConversationService
from typing import List
from .llms.llm_sevice import LLMService, LLMType
from datetime import datetime

log = get_logger(__name__)

class ModelService:

    def validate_model_data(data: dict):
        editable_fields = vars(GPTModel).keys()
        if not data:
            raise BadRequestError("No data provided")
        for key in data.keys():
            if key not in editable_fields:
                raise BadRequestError(f"Invalid fields provided: {key}") 

    def get_model_by_id(model_id: List[str]):
        log.info(f"Getting model for model {model_id}")
        return ModelRepository.find_models_by_id(model_id)
    
    def create_model(data: dict):
        return ModelRepository.create_model(data)
    
    def update_model(model_id: str, data: dict):
        ModelService.validate_model_data(data)
        return ModelRepository.update_model(model_id, data)
    
    def delete_model(model_id: str):
        if (ConversationService.model_usage(model_id)):
            raise BadRequestError("Cannot delete model with existing conversations.")
        return ModelRepository.delete_model(model_id)
    
    def get_response(conversation_id: str, system_message: str, user_message: str):
        conversation = ConversationService.get_conversation(conversation_id)
        if not conversation["status"]:
            raise BadRequestError("Conversation is not active")
        return get_response(conversation, system_message, user_message)

    def get_all_models_by_course(course_id: str):
        return ModelRepository.find_models_by_course_id(course_id)
    
    def get_all_models_by_user(user_id: str):
        return list(ModelRepository.find_models_by_user_id(user_id))
    
    def get_all_models():
        return ModelRepository.find_all_models()
    
    def get_all_models_by_deployment(deployment_id: str):
        return ModelRepository.find_models_by_deployment_id(deployment_id)
    
    def update_model_status(model_id: str, status: bool):
        ModelService.exists(model_id)
        return ModelRepository.update_model_status(model_id, status)
    
    def exists(model_id: str):
        model = ModelService.get_model_by_id(model_id)
        if not model:
            raise BadRequestError("Model does not exist")
        return model

class StrategyService:
    
    def generate_strategy(student_question: str, code_content: str, user_id: str, conversation_id: str):
        if not(conversation_id):
            conversation = ConversationService.create_conversation(model_id=None, data={ "user_id": user_id })
        else:
            conversation = ConversationService.get_conversation(conversation_id)
        
        strategy_repository = StrategyRepository()
        user_input = strategy_repository.get_user_input(student_question, code_content)
        
        situation = None
        max_retries = 5
        while situation not in strategy_repository.situations:
            situation = LLMService.get_completion(LLMType.GPT4, strategy_repository.strategy_prompt, user_input)
            max_retries -= 1
            if max_retries == 0:
                raise BadRequestError("Failed to generate strategy")
            
        strategies = strategy_repository.get_strategies(situation)
        metadata = { **strategies, "student_question": student_question, "code_content": code_content, "date": datetime.now() }
        
        if not conversation_id: conversation["metadata"] = [metadata]
        else: conversation["metadata"].append(metadata)
        
        ConversationService.update_conversation(conversation["_id"], {"metadata": conversation["metadata"]})
        return { "conversation_id": conversation["_id"], **strategies}
        
        