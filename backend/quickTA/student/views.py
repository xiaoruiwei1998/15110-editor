import pytz 
import re

from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from drf_yasg import openapi
from drf_yasg.openapi import *
from drf_yasg.utils import swagger_auto_schema

from utils import *
from student.service import *
from student.serializers import *
from models.service import ModelService

log = get_logger(__name__)

class ConversationView(APIView):
    
    @swagger_auto_schema(
        operation_summary="Get conversation details",
        responses={200: ConversationSerializer(), 404: "Conversation not found"},
        manual_parameters=[Parameter("conversation_id", IN_QUERY, description="Conversation ID", type=TYPE_STRING)]
    )
    @Controller
    def get(self, request):
        """
        Acquires the details of a certain conversation by conversation_id.
        """
        conversation_id = request.query_params.get('conversation_id', '')
        conversation = ConversationService.get_conversation(conversation_id)
        return JsonResponse(conversation)

    @swagger_auto_schema(
        operation_summary="Create a new conversation",
        manual_parameters=[
            Parameter("user_id", IN_QUERY, description="User ID", type=TYPE_STRING),
            Parameter("course_id", IN_QUERY, description="Course ID", type=TYPE_STRING),            
            Parameter("model_id", IN_QUERY, description="Model ID", type=TYPE_STRING),
        ],
        responses={201: ConversationSerializer(), 400: "Bad Request"}
    )
    # @Controller
    def post(self, request):
        """
        Creates a new conversation
        """
        user_id = request.query_params.get('user_id', '')
        course_id = request.query_params.get('course_id', '')
        model_id = request.query_params.get('model_id', '')
        conversation = ConversationService.create_conversation(user_id, course_id, model_id, request.data)
        return JsonResponse(conversation, status=status.HTTP_201_CREATED)

class ConversationListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all conversations",
        manual_parameters=[
            Parameter("user_id", IN_QUERY, description="User ID", type=TYPE_STRING),
            Parameter("course_id", IN_QUERY, description="Course ID", type=TYPE_STRING),
        ],
        responses={200: ConversationSerializer(many=True)},
    )
    def get(self, request):
        """
        Gets all conversations
        """
        user_id = request.query_params.get('user_id', '')
        course_id = request.query_params.get('course_id', '')
        detailed = request.query_params.get('detailed', False)
        conversations = ConversationService.get_all_conversations(user_id, course_id, detailed)
        return JsonResponse(conversations, safe=False)

class ConversationHistoryCsvView(APIView):

    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Get conversation history",
        responses={200: Response('File Attachment', schema=Schema(type=TYPE_FILE))},
        manual_parameters=[Parameter("conversation_id", IN_QUERY, description="Conversation ID", type=TYPE_STRING),]
    )
    def get(self, request):
        conversation_id = request.query_params.get('conversation_id', "")
        conversation_history = list(ConversationService.get_conversation_history(conversation_id))[0]
        
        filename = f'[{conversation_history["conversation_name"]}]_{nowDateTimeCsvStr()}.csv'
        response = CsvResponse(filename)
        return ConversationService.get_conversation_history_csv(conversation_history, response)

class ConversationChatlogsView(APIView):

    @swagger_auto_schema(  
        operation_summary="Get all chatlogs from a conversation",
        responses={200: ConversationChatlogSerializer(many=True)},
        manual_parameters=[
            Parameter("conversation_id", IN_QUERY, description="Conversation ID", type=TYPE_STRING),
            Parameter("analysis", IN_QUERY, description="Show analysis", type=TYPE_BOOLEAN)
        ]
    )
    def get(self, request):
        conversation_id = request.query_params.get('conversation_id', '')
        show_metadata = request.query_params.get('analysis', False)
        chatlogs = ConversationService.get_conversation_chatlogs(conversation_id, show_metadata)
        return JsonResponse({"_id": conversation_id, "chatlogs": chatlogs})

class ChatlogView(APIView):

    @swagger_auto_schema(
        operation_summary="Create a new chatlog",
        request_body=ChatlogSerializer(),
        responses={201: ConversationSerializer(), 400: "Bad Request", 406: "Model not active"}
    )
    @Controller
    def post(self, request):
        """
        Creates a new chatlog from the user, as well as acquiring a response from the LLM.
        """
        system_prompt = request.data.get('system_message', {})
        user_message = request.data.get('user_message', "")
        conversation_id = request.data.get('conversation_id', '')

        # 1. Generate system prompt
        system_message = ChatlogService.get_system_message(system_prompt)

        # 2. Create user chatlog record
        ChatlogService.create_user_chatlog(conversation_id, user_message)
        
        # 3. Acquire LLM chatlog response 
        model_response = ModelService.get_response(conversation_id, system_message, user_message)
        ChatlogService.create_agent_chatlog(conversation_id, model_response)
        return JsonResponse({ "message" : model_response }, status=status.HTTP_201_CREATED)
    

    
class ChatlogListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all chatlogs from a conversation",
        responses={200: ChatlogSerializer(many=True)},
    )
    @Controller
    def get(self, request):
        """
        Gets all chatlogs
        """
        chatlogs = ChatlogService.get_all_chatlogs()
        return JsonResponse(chatlogs, safe=False)
   
class ConversationHistoryView(APIView):

    @swagger_auto_schema(
        operation_summary="Get conversation history",
        manual_parameters=[
            Parameter("user_id", IN_QUERY, description="User ID", type=TYPE_STRING),
            Parameter("course_id", IN_QUERY, description="Course ID", type=TYPE_STRING),
            Parameter("model_ids", IN_QUERY, description="Model IDs (Comma-separated)", type=TYPE_STRING)
        ],
        responses={200: ConversationSerializer}
    )
    @Controller
    def get(self, request):
        """
        Gets all conversations of a user from that course.
        Pass in comma-separated model_ids to filter by model.
        """
        user_id = request.query_params.get('user_id', '')
        course_id = request.query_params.get('course_id', '')
        model_ids = request.query_params.get('model_ids', '').split(',')
        if (model_ids == ['']): model_ids = []

        conversations = ConversationService.get_conversations_by_user_course(user_id, course_id, model_ids)
        return JsonResponse({"conversations": conversations})
    
class ConversationEndView(APIView):
    @swagger_auto_schema(
        operation_summary="End conversation",
        manual_parameters=[Parameter("conversation_id", IN_QUERY, description="Conversation ID", type=TYPE_STRING),],
        responses={200: "Conversation ended", 404: "Conversation not found"}
    )
    @Controller
    def post(self, request):
        """
        Ends a conversation
        """
        conversation_id = request.query_params.get('conversation_id', '')
        conversation = ConversationService.end_conversation(conversation_id)
        return JsonResponse(conversation)
