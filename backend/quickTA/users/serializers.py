from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.model import *
from users.repository import UserRepository
from course.models import Course


# class UserSerializer:
#     def __init__(self, data):
#         self.user = User(**data)
#         self.validate_data()

#     def validate_data(self):
#         if not self.user.username:
#             raise ValueError("Username is required")
#         if not self.user.first_name:
#             raise ValueError("First name is required")
#         if not self.user.last_name:
#             raise ValueError("Last name is required")
#         if not self.user.role:
#             raise ValueError("Role is required")

#     def save(self):
#         UserRepository.create_user(self.user)
#         return self.user


class UserSerializer(ModelSerializer):

    USER_ROLE_CHOICES = (
        ('ST', 'Student'),
        ('RS', 'Researcher'),
        ('AM', 'Admin'),
        ('IS', 'Instructor'),
    )

    role = serializers.ChoiceField(choices=USER_ROLE_CHOICES)
    courses = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            '_id',
            'name',
            'username',
            'role',
            'courses',
            'status',
            'created_at',
            'updated_at',
        ]

    def get_courses(self, obj):
        return [str(course) for course in obj["courses"]] if "courses" in obj else []

    def get_status(self, obj):
        return [s for s in obj["status"]] if "status" in obj else []


class UserBatchAddSerializer(ModelSerializer):

    role = serializers.CharField(default='ST', required=False)
    courses = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'name',
            'username',
            'role',
            'courses',
            'status'
        ]

    def get_courses(self, obj):
        return [str(course) for course in obj["courses"]] if "courses" in obj else []

    def get_status(self, obj):
        return [s for s in obj["status"]] if "status" in obj else []

    def __init__(self, *args, **kwargs):
        self.default_role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if 'role' not in data:
            data['role'] = self.default_role

        courses = data.pop('courses', [])
        status = data.pop('status', [])

        data['courses'] = courses
        data['status'] = status

        return super().to_internal_value(data)

class UserStatusSerializer(ModelSerializer):

    class Meta:
        model = UserStatus
        fields = [
            '_id',
            'user_id',
            'deployment_id',
            'model_id',
            'condition_id',
            'status',
            'enrolled_at',
        ]
