from drf_yasg.openapi import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from django.http import JsonResponse

from utils import *
from course.interface.service import CourseService
from models.helpers import *
from models.service import ModelService, StrategyService
from models.serializers import GPTModelSerializer

# Create your views here.

log = get_logger(__name__)

class GPTModelView(APIView):

    @swagger_auto_schema(
        operation_description="Returns a GPT model given the model_id and course_id.",
        responses={ 200: GPTModelSerializer(), 400: "Bad Request", 404: "Model not found"},
        manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)]
    )
    # @Controller
    def get(self, request):
        """
        Returns a GPT model given the model_id.
        Comma-separated model_id can be used to get multiple models.
        """
        model_id = request.query_params.get('model_id', '')
        model_id = model_id.split(',') if model_id else []

        log.info(f"model_id: {model_id}")
        model = ModelService.get_model_by_id(model_id)
        if len(model_id) > 1:
            return JsonResponse({'models': model})
        else:
            return JsonResponse({'models': [model]})
        return JsonResponse(model, safe=False)

    @swagger_auto_schema(
        operation_description="Creates a GPT Model given the parameter specifications.",
        request_body=Schema(type=TYPE_OBJECT, properties=GPTMODEL_BODY),
        responses={ 200: GPTModelSerializer(), 400: "Bad Request"}
    )
    @Controller
    def post(self, request):
        """
        Creates a GPT Model given the parameter specifications.
        """
        model = ModelService.create_model(request.data)
        return JsonResponse(model, safe=False)
    
    @swagger_auto_schema(
        operation_description="Updates a GPT Model given the parameter specifications.",
        manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
        request_body=Schema(type=TYPE_OBJECT, properties=GPTMODEL_BODY),
        responses={ 200: GPTModelSerializer(), 400: "Bad Request"}
    )
    @Controller
    def patch(self, request):
        """
        Updates a GPT Model given the parameter specifications.
        """
        model_id = request.query_params.get('model_id', '')
        model = ModelService.update_model(model_id, request.data)
        return JsonResponse(model)
    
    @swagger_auto_schema(
        operation_description="Deletes a GPT Model given the model_id and course_id.",
        responses={ 200: GPTModelSerializer(), 404: "Model not found" },
        manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)]
    )
    @Controller
    def delete(self, request):
        """
        Deletes a GPT Model given the model_id
        """
        model_id = request.query_params.get('model_id', '')
        ModelService.delete_model(model_id)
        return JsonResponse({'msg': 'Model deleted successfully.'})

class GPTModelCourseListView(APIView):

    @Controller
    def get(self, request):
        """
        Get all models in a course given course id
        """
        course_id = request.query_params.get('course_id', '')
        course_code = request.query_params.get('course_code', '')
        semester = request.query_params.get('semester', '')

        course = CourseService.get_course(course_id, course_code, semester)
        models = ModelService.get_all_models_by_course(course["_id"])
        # models = [model.to_dict() for model in models]
        return JsonResponse({'models': models})

class GPTModelListView(APIView):
    """
    View to list all GPT models in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Returns all GPT models in the system.",
        responses={ 200: GPTModelSerializer(many=True) }
    )
    @Controller
    def get(self, request):
        """
        Returns all GPT models in the system.
        """
        models = ModelService.get_all_models()
        return JsonResponse({"models": models})

class ActivateGPTModelView(APIView):

    @swagger_auto_schema(
        operation_description="Activates a selected GPTModel",
        manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
        responses={ 200: 'Model activated', 400: "Bad Request", 404: "Model not found"}
    )
    @Controller
    def get(self, request):
        """
        Activates a selected GPTModel.
        """
        model_id = request.query_params.get('model_id', '')
        ModelService.update_model_status(model_id, True)
        return JsonResponse({'msg': 'Model activated successfully.'})

class DeactivateGPTModelView(APIView):

    @swagger_auto_schema(
        operation_description="Deactivates a selected GPTModel",
        manual_parameters=[Parameter("_id", IN_QUERY, type=TYPE_STRING)],
        responses={ 200: "Model deactivated", 400: "Bad Request", 404: "Model not found"}
    )
    def get(self, request):
        """
        Deactivates a selected GPTModel.
        """
        model_id = request.query_params.get('_id', '')
        ModelService.update_model_status(model_id, False)        
        return JsonResponse({'msg': 'Model deactivated successfully.'})

class GPTModelDeploymentListView(APIView):

    @swagger_auto_schema(
        operation_description="Get all models in a deployment given deployment id",
        manual_parameters=[Parameter("deployment_id", IN_QUERY, type=TYPE_STRING)],
        responses={ 200: GPTModelSerializer(many=True) }
    )
    @Controller
    def get(self, request):
        """
        Get all models in a deployment given deployment id
        """
        deployment_id = request.query_params.get('deployment_id', '')
        models = ModelService.get_all_models_by_deployment(deployment_id)
        return JsonResponse({'models': models})
    
class ModelStrategyView(APIView):
        
        @swagger_auto_schema(
            operation_description="Get all strategies for the given model_id",
            manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
            responses={ 200: "Strategies returned", 400: "Bad Request"}
        )
        def get(self, request):
            """
            Get all strategies for the given model_id
            """
            model_id = request.query_params.get('model_id', '')
            strategies = StrategyService.get_strategies(model_id)
            return JsonResponse({'strategies': strategies})
        
        @swagger_auto_schema(
            operation_description="Create a strategy for the given model_id",
            manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
            responses={ 200: "Strategy created", 400: "Bad Request"}
        )
        def post(self, request):
            """
            Create a strategy for the given model_id
            """
            model_id = request.query_params.get('model_id', '')
            strategy = StrategyService.create_strategy(model_id)
            return JsonResponse({'strategy': strategy})
        
        @swagger_auto_schema(
            operation_description="Update a strategy for the given model_id",
            manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
            responses={ 200: "Strategy updated", 400: "Bad Request"}
        )
        def patch(self, request):
            """
            Update a strategy for the given model_id
            """
            model_id = request.query_params.get('model_id', '')
            strategy = StrategyService.update_strategy(model_id)
            return JsonResponse({'strategy': strategy})
        
        @swagger_auto_schema(
            operation_description="Delete a strategy for the given model_id",
            manual_parameters=[Parameter("model_id", IN_QUERY, type=TYPE_STRING)],
            responses={ 200: "Strategy deleted", 400: "Bad Request"}
        )
        def delete(self, request):
            """
            Delete a strategy for the given model_id
            """
            model_id = request.query_params.get('model_id', '')
            StrategyService.delete_strategy(model_id)
            return JsonResponse({'msg': 'Strategy deleted successfully.'})

class GenerateStrategyView(APIView):
    
    @swagger_auto_schema(
        operation_description="Generate strategy based on student question and code content",
        responses={ 200: "Strategy generated", 400: "Bad Request"}
    )
    def post(self, request):
        """
        Generate a strategy for the given student question and code content
        Response: 
        {
            conversation_id: str,
            situation: str,
            strategies: List[str]
        }
        """
        user_id = request.data.get('user_id', '')
        conversation_id = request.data.get('conversation_id', '')
        student_question = request.data.get('student_question')
        code_content = request.data.get('code_content')
        strategies = StrategyService.generate_strategy(student_question, code_content, user_id, conversation_id)
        return JsonResponse(strategies)