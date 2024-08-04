from drf_yasg.openapi import *


GPTMODEL_BODY = { 
    'model_name': Schema(type=TYPE_STRING),
    'course_id': Schema(type=TYPE_STRING),
    'deployment_id': Schema(type=TYPE_STRING),
    'default_message': Schema(type=TYPE_STRING),
    'default_conversation_name': Schema(type=TYPE_STRING),
    'status': Schema(type=TYPE_BOOLEAN),
    'model': Schema(type=TYPE_STRING),
    'prompt': Schema(type=TYPE_STRING),
    'max_tokens': Schema(type=TYPE_INTEGER),
    'temperature': Schema(type=TYPE_NUMBER),
    'top_p': Schema(type=TYPE_NUMBER),
    'n': Schema(type=TYPE_INTEGER),
    'stream': Schema(type=TYPE_BOOLEAN),
    'presence_penalty': Schema(type=TYPE_NUMBER),
    'frequency_penalty': Schema(type=TYPE_NUMBER),
}