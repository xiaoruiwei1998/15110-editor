from rest_framework.serializers import ModelSerializer
from models.models import GPTModel
from rest_framework import serializers

class GPTModelSerializer(ModelSerializer):

    model_type = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    default_conversation_name = serializers.SerializerMethodField()
    default_message = serializers.SerializerMethodField()
    
    model_header_name = serializers.SerializerMethodField()
    model_preheader_name = serializers.SerializerMethodField()

    model = serializers.SerializerMethodField()
    prompt = serializers.SerializerMethodField()
    max_tokens = serializers.SerializerMethodField()
    temperature = serializers.SerializerMethodField()
    top_p = serializers.SerializerMethodField()
    n = serializers.SerializerMethodField()
    stream = serializers.SerializerMethodField()
    presence_penalty = serializers.SerializerMethodField()
    frequency_penalty = serializers.SerializerMethodField()
    functions = serializers.SerializerMethodField()
    function_call = serializers.SerializerMethodField()

    class Meta:
        model = GPTModel
        fields = [
            '_id',
            'model_name',
            'model_type',
            'description',
            'course_id',
            'deployment_id',
            'status',
            'default_conversation_name',
            'default_message',
            'model_header_name',
            'model_preheader_name',
            'model',
            'prompt',
            'max_tokens',
            'temperature',
            'top_p',
            'n',
            'stream',
            'presence_penalty',
            'frequency_penalty',
            'functions',
            'function_call',
        ]

    def get_model_type(self, obj): 
        if "model_type" in obj:
            print(obj["model_type"])
            return obj["model_type"]
        return ""
    
    def get_description(self, obj): return obj["description"] if "description" in obj else ""
    def get_default_conversation_name(self, obj): return obj["default_conversation_name"] if "default_conversation_name" in obj else ""
    def get_default_message(self, obj): return obj["default_message"] if "default_message" in obj else ""
    def get_model_header_name(self, obj): return obj["model_header_name"] if "model_header_name" in obj else ""
    def get_model_preheader_name(self, obj): return obj["model_preheader_name"] if "model_preheader_name" in obj else ""

    
    def get_model(self, obj): return obj["model"] if "model" in obj else ""
    def get_prompt(self, obj): return obj["prompt"] if "prompt" in obj else ""
    def get_max_tokens(self, obj): return obj["max_tokens"] if "max_tokens" in obj else 0
    def get_temperature(self, obj): return obj["temperature"] if "temperature" in obj else 0
    def get_top_p(self, obj): return obj["top_p"] if "top_p" in obj else 0
    def get_n(self, obj): return obj["n"] if "n" in obj else 0
    def get_stream(self, obj): return obj["stream"] if "stream" in obj else False
    def get_presence_penalty(self, obj): return obj["presence_penalty"] if "presence_penalty" in obj else 0
    def get_frequency_penalty(self, obj): return obj["frequency_penalty"] if "frequency_penalty" in obj else 0
    def get_functions(self, obj): return obj["functions"] if "functions" in obj else []
    def get_function_call(self, obj): return obj["function_call"] if "function_call" in obj else ""


