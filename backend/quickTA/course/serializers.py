from rest_framework.serializers import *
from rest_framework import serializers
from .models import *
import users.serializers as user_serializers
from models.models import GPTModel
from users.model import User

class CourseSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.show_users = kwargs.pop('show_users', False)
        self.show_active_deployments = kwargs.pop('show_active_deployments', False)
        super().__init__(*args, **kwargs)
    
    students = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()
    researchers = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    deployments = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [ '_id', 'course_code', 'semester', 'course_name', 'start_date', 'end_date', 'students', 'instructors', 'researchers', 'admins', 'deployments' ]

    def get_students(self, obj): return [str(student) for student in obj["students"]] if "students" in obj and self.show_users else []
    def get_instructors(self, obj): return [str(instructor) for instructor in obj["instructors"]] if "instructors" in obj and self.show_users else []
    def get_researchers(self, obj): return [str(researcher) for researcher in obj["researchers"]] if "researchers" in obj and self.show_users else []
    def get_admins(self, obj): return [str(admin) for admin in obj["admins"]] if "admins" in obj and self.show_users else []
    def get_deployments(self, obj): return []


class CourseMultipleSerializer(ModelSerializer):

    class Meta:
        model = Course
        fields = ['_id', 'course_code', 'semester', 'course_name', 'start_date', 'end_date']
    
class CourseMultipleEnrollmentUserSerializer(ModelSerializer):
    
    _id = serializers.CharField(max_length=200, required=False)
    username = serializers.CharField(max_length=200, required=False)
    role = serializers.CharField(max_length=200, default='ST', required=False)
    class Meta:
        model = User
        fields = [ '_id', 'username', 'role' ]
    
    # Check if either user_id or utorid is provided
    def validate(self, data):
        if 'user_id' not in data and 'username' not in data:
            raise serializers.ValidationError("Either user_id or username must be provided")
        return data

class CourseModelSerializer(ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        self.course_id = kwargs.pop('course_id', "")
        super().__init__(*args, **kwargs)

    models = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['_id', 'models']

    def get_models(self, obj): 
        models = GPTModel.objects.filter(course_id=self.course_id)
        return [model.to_student_dict() for model in models if model.status] 


class CourseDeploymentSerializer(ModelSerializer):
    
    class CourseDeploymentAssessmentIdsSerializer(Serializer):
        assessment_id = serializers.CharField(max_length=200, required=False)
    class CourseDeploymentSurveyIdsSerializer(Serializer):
        survey_type = serializers.CharField(max_length=200, required=False)
        survey_id = serializers.CharField(max_length=200, required=False)

    assessment_ids = CourseDeploymentAssessmentIdsSerializer(many=True, required=False)
    survey_ids = CourseDeploymentSurveyIdsSerializer(many=True, required=False)

    class Meta:
        model = CourseDeployment
        fields = ['_id', 'name', 'course_id', 'priority', 'status', 'assessment_ids', 'survey_ids']
