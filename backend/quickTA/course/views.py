from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.openapi import *

from users.serializers import UserSerializer
from course.serializers import *
from course.helpers import *
from course.interface.service import CourseService
from models.serializers import GPTModelSerializer
from utils import *


# Create your views here.
class CourseView(APIView):

    @swagger_auto_schema(
        operation_summary="Get course details",
        responses={200: CourseSerializer(), 404: "Course not found"},
        manual_parameters=[
            *course_identifier_params(),
            Parameter("show_users", in_=IN_QUERY, description="Include user lists [True/False]", type=TYPE_BOOLEAN, default=False),
            Parameter("detailed", in_=IN_QUERY, description="Include detailed information [True/False]", type=TYPE_BOOLEAN, default=False),
        ]
    )
    @Controller
    def get(self, request):
        """
        Acquires the details of a certain course by either:
        
            1. course_id, or
            2. course_code and semester

        Additionally, you can send True/False to the 'show_users' parameter to get the list of students enrolled in the course.
        """
        course_id, course_code, semester, show_users = get_course_from_request_params(request.query_params)
        detailed_info = request.query_params.get('detailed', False)
        course = CourseService.get_course(course_id, course_code, semester, show_users, detailed_info)
        return JsonResponse(course)
    
    @swagger_auto_schema(
        operation_summary="Create a new course",
        request_body=CourseSerializer,
        responses={201: CourseSerializer(), 400: "Bad Request"}
    )
    @Controller
    def post(self, request):
        """
        Creates a new course
        """
        _, course_code, semester, _ = get_course_from_request_params(request.query_params)
        course = CourseService.create_course(request.data, course_code, semester)
        return JsonResponse(course, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Update course's information",
        manual_parameters=[*course_identifier_params()],
        request_body=CourseSerializer,
        responses={200: "User updated", 400: "Bad Request", 403: "Course already exists", 404: "User not found"}
    )
    # @Controller
    def patch(self, request):
        """
        Updates the course's information
        """
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        course = CourseService.update_course(course_id, course_code, semester, request.data)
        return JsonResponse(course)
    
    @swagger_auto_schema(
        operation_summary="Delete a course",
        manual_parameters=[*course_identifier_params()],
        responses={200: "Course deleted", 404: "Course not found", 405: "Cannot delete course with enrolled users"}
    )
    @Controller
    def delete(self, request):
        """
        Deletes an empty course
        """
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        CourseService.delete_course(course_id, course_code, semester)
        return JsonResponse({"msg": "Course deleted"})

class CourseList(APIView):
    @swagger_auto_schema(
        operation_summary="Get all courses",
        manual_parameters=[Parameter("show_user_details", IN_QUERY, description="Show user details [True/False]", type=TYPE_BOOLEAN)],
        responses={200: CourseSerializer(many=True)}
    )
    @Controller
    def get(self, request):
        """
        Gets all courses
        """
        show_user_details = request.query_params.get('show_user_details', False)
        courses = CourseService.get_all_courses(show_user_details)
        return JsonResponse(courses, safe=False)

class CourseEnrollment(APIView):
    @swagger_auto_schema(
        operation_summary="Enroll a student in a course",
        manual_parameters=[*course_identifier_params(), *user_identifier_params()],
        responses={200: "User enrolled", 400: "User already enrolled", 404: "User or course not found"}
    )
    # @Controller
    def get(self, request):
        """
        Enrolls a student in a course
        """
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        user_id, username, role = get_user_from_request_params(request.query_params)
        enroll_to_all_deployments = request.query_params.get('enroll_deployments', False)
        user = CourseService.enroll_user(course_id, course_code, semester, user_id, username, role, enroll_to_all_deployments)
        return JsonResponse(user)

    @swagger_auto_schema(
        operation_summary="Unenroll a student from a course",
        manual_parameters=[*course_identifier_params(), *user_identifier_params()],
        responses={200: "User unenrolled", 400: "User is not enrolled", 404: "User or course not found"}
    )
    @Controller
    def delete(self, request):
        """
        Unenrolls a student from a course.

        A course can be specified by:
        
            1. course_id, or
            2. course_code and semester

        A user can be specified by: 

            1. user_id, or
            2. utorid
        """
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        user_id, username, role = get_user_from_request_params(request.query_params)
        user = CourseService.unenroll_user(course_id, course_code, semester, user_id, username, role)
        return JsonResponse(user)

class CourseUserList(APIView):
    
    @swagger_auto_schema(
        operation_summary="Get students in a course by user roles",
        manual_parameters=[
            *course_identifier_params(),
            Parameter("user_roles", IN_QUERY, description="List of user roles (ST = Student, IS = Instructor, RS = Researcher, AM = Admin)", type=TYPE_ARRAY, items=Items(type=TYPE_STRING)),
        ],
        responses={200: UserSerializer(many=True), 404: "Course not found"}
    )
    @Controller
    def get(self, request):
        """
        Acquires students in a course by user roles.
        """
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        user_roles = get_roles_from_request_params(request.query_params)
        users = CourseService.get_course_user_list(course_id, course_code, semester, user_roles)
        return JsonResponse(users)

class CourseMultipleList(APIView):
    @swagger_auto_schema(
        operation_summary="Get multiple courses",
        manual_parameters=[Parameter("course_ids", IN_QUERY, description="List of course IDs", type=TYPE_ARRAY, items=Items(type=TYPE_STRING))],
        responses={200: CourseMultipleSerializer(many=True), 404: "Course not found"}
    )
    @Controller
    def get(self, request):
        """
        Gets multiple courses by their course ids.
        """
        course_ids = get_course_ids_from_request_params(request.query_params)
        courses = CourseService.get_multiple_courses(course_ids)
        return JsonResponse({"courses": courses})
    
class CourseModelList(APIView):
    
    @swagger_auto_schema(
        operation_summary="Get all models from the given course",
        manual_parameters=[
            *course_identifier_params(),
            Parameter("show_all", IN_QUERY, description="Show all models [True/False]", type=TYPE_BOOLEAN),
        ],
        responses={200: GPTModelSerializer(many=True), 404: "Course Not found"}
    )
    def get(self, request):
        course_id, course_code, semester, _ = get_course_from_request_params(request.query_params)
        show_all = request.query_params.get('show_all', False)
        models = CourseService.get_course_models(course_id, course_code, semester, show_all)
        return JsonResponse({'models': models})    
