from rest_framework.views import APIView
from django.http import JsonResponse
from .serializers import UserSerializer, UserBatchAddSerializer
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.openapi import *

from utils import *
from users.service import UserService
from users.service import *

# Create your views here.
logger = get_logger(__name__)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="Login",
        responses={200: UserSerializer, 404: "User not found"},
        manual_parameters=[openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING)]
    )
    @Controller
    def get(self, request):
        """
        Login with utorid
        """
        username = request.query_params.get('username', '')
        logger.info(f"User {username} logging in")
        if not (username):
            username = UserService.get_username_from_headers(request)

        user = UserService.login(username)
        return JsonResponse(user)


class UserView(APIView):

    @swagger_auto_schema(
        operation_summary="Get user details",
        responses={200: UserSerializer, 404: "User not found"},
        manual_parameters=[openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
                           openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING)]
    )
    @Controller
    def get(self, request):
        """
        Acquires the details of a certain user by either user_id or utorid, or both.
        """
        user_id = request.query_params.get('user_id', '')
        username = request.query_params.get('username', '')
        if not (username):
            username = UserService.get_username_from_headers(request)
        user = UserService.get_user(user_id, username)
        return JsonResponse(user)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: "Bad Request"}
    )
    @Controller
    def post(self, request):
        """
        Creates a new user.

        A User can be of the following roles:

        - ST: student
        - IS: instructor
        - RS: researcher
        - AM: admin
        """
        username = request.data.get('username', '')
        user = UserService.create_user(username, request.data)
        return JsonResponse(user, status=status.HTTP_201_CREATED, safe=False)

    @swagger_auto_schema(
        operation_summary="Update user's information",
        manual_parameters=[openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
                           openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING)],
        request_body=UserSerializer,
        responses={200: "User updated",
                   400: "Bad Request", 404: "User not found"}
    )
    @Controller
    def patch(self, request):
        """
        Updates the user's information

        A User can be of the following roles:

        - ST: student
        - IS: instructor
        - RS: researcher
        - AM: admin
        """
        user_id = request.query_params.get('user_id', '')
        username = request.query_params.get('username', '')
        logger.info(f"Updating user {username} with data {request.data}")
        user = UserService.update_user(user_id, username, request.data)
        return JsonResponse(user)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        manual_parameters=[openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
                           openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING)],
        responses={200: "User deleted", 404: "User not found"}
    )
    @Controller
    def delete(self, request):
        """
        Deletes a user
        """
        user_id = request.query_params.get('user_id', '')
        utorid = request.query_params.get('utorid', '')
        UserService.delete_user(user_id, utorid)
        return JsonResponse({"msg": f"User deleted"})


class UserListView(APIView):

    @swagger_auto_schema(
        operation_summary="Get all users",
        responses={200: UserSerializer(many=True), 404: "No users found"}
    )
    @Controller
    def get(self, request):
        """
        Acquires all users.
        """
        users = UserService.get_all_users()
        return JsonResponse(users, safe=False)

# class UserCoursesListView(APIView):

#     @swagger_auto_schema(
#         operation_summary="Get user's courses",
#         manual_parameters=[
#             openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
#             openapi.Parameter("utorid", openapi.IN_QUERY, description="Utorid", type=openapi.TYPE_STRING)
#         ],
#         responses={200: "User's courses", 400: "Bad request", 404: "User not found"}
#     )
#     def get(self, request):
#         """
#         Acquires the courses of a certain user by user_id.
#         """
#         user_id = request.query_params.get('user_id', '')
#         utorid = request.query_params.get('utorid', '')

#         if user_id: user = get_object_or_404(User, user_id=user_id)
#         else: user = get_object_or_404(User, utorid=utorid)

#         if user.user_role == 'ST':
#             # lst = []
#             # for course in user.courses:
#             #     c = get_object_or_404(Course, course_id=course)
#             #     if c.end_date > datetime.now():
#             #         lst.append(course)
#             #
#             return JsonResponse([course for course in user.courses if get_object_or_404(Course, course_id=course).end_date > datetime.now()], safe=False)
#         return JsonResponse(user.courses, safe=False)

# # TODO: add a view to get all the courses the user is not in


class UserBatchAddView(APIView):

    @swagger_auto_schema(
        operation_summary="Add multiple users",
        request_body=UserBatchAddSerializer(many=True),
        manual_parameters=[openapi.Parameter("role", openapi.IN_QUERY, description="User role", type=openapi.TYPE_STRING, enum=ROLE_MAP_ENUM)],
        responses={201: "Users created", 400: "Bad request"}
    )
    @Controller
    def post(self, request):
        """
        Creates multiple users. Defaults to student role if unspecified.
        Errors upon duplicate usernames.
        """
        role = request.query_params.get('role', 'ST')
        users = UserService.batch_add_users(role, request.data)
        return JsonResponse(users, status=status.HTTP_201_CREATED, safe=False)

# class UserBatchAddCsvView(APIView):

#     parser_classes = (MultiPartParser,)

#     @swagger_auto_schema(
#         operation_summary="Add multiple users through csv file",
#         manual_parameters=[
#             openapi.Parameter(name="files", in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description="Document"),
#             openapi.Parameter("course_id", openapi.IN_QUERY, description="Course ID", type=openapi.TYPE_STRING),
#             openapi.Parameter("course_code", openapi.IN_QUERY, description="Course code", type=openapi.TYPE_STRING),
#             openapi.Parameter("semester", openapi.IN_QUERY, description="Semester", type=openapi.TYPE_STRING),
#         ],
#         responses={201: "Users created", 400: "Bad request"}
#     )
#     @action(detail=False, methods=['post'])
#     def post(self, request):
#         """
#         Create mutiple users through csv file. Defaults to student role if unspecified.

#         Course can be specified by either:

#             1. course_id or
#             2. course_code and semester.

#         Skips rows missing 'utorid' and 'name' column headers.
#         Optional column with header 'role' defaults to 'ST' student role.
#         Optional column with header 'model_id' to assign a default model ID to 'ST' student role.
#         """
#         csv_file = request.FILES['files']
#         if not csv_file: return ErrorResponse("No csv uploaded", status=status.HTTP_400_BAD_REQUEST)

#         course_id = request.query_params.get('course_id', '')
#         course_code = request.query_params.get('course_code', '')
#         semester = request.query_params.get('semester', '')
#         user_role = request.query_params.get('user_role', 'ST')

#         if course_id: course = get_object_or_404(Course, course_id=course_id)
#         else: course = get_object_or_404(Course, course_code=course_code, semester=semester)

#         # Handle csv file
#         file_data = csv_file.read().decode(encoding='utf-8-sig')
#         lines = file_data.split("\n")

#         name_idx, utorid_idx, user_role_idx, model_id_idx = -1, -1, -1, -1
#         print(lines[0].split(","))
#         for index, key in enumerate(lines[0].split(",")):
#             if key == 'name': name_idx = index
#             if key == 'utorid': utorid_idx = index
#             if key == 'role': user_role_idx = index
#             if key == 'model_id': model_id_idx = index

#         print(name_idx, utorid_idx, user_role_idx, model_id_idx)

#         if not (name_idx != -1 and utorid_idx != -1):
#             return ErrorResponse(f'Fields not present: {"name" if name_idx == -1 else ""} {"utorid" if utorid_idx == -1 else ""}', status=status.HTTP_400_BAD_REQUEST)

#         successful_users = []
#         existing_users = []
#         failed_users = []

#         for i, line in enumerate(lines[1:]):

#             row = line.split(",")
#             utorid = row[utorid_idx]
#             name = row[name_idx]
#             role = row[user_role_idx] if user_role_idx != -1 else user_role
#             model_id = row[model_id_idx] if model_id_idx != -1 else ""


#             if not (utorid and name):
#                 failed_users.append(f'Row {i+2}: missing utorid or name')
#                 continue

#             if User.objects.filter(utorid=utorid):
#                 user = User.objects.get(utorid=utorid)
#                 if course_id not in user.courses:
#                     user.courses = user.courses + [str(course_id)]
#                     User.objects.filter(utorid=utorid).update(courses=user.courses, model_id=model_id)
#                 data = { 'utorid': utorid, 'name': name, 'user_role': role, 'courses': [course_id], 'model_id': model_id }
#                 existing_users.append(data)
#                 continue

#             data = { 'utorid': utorid, 'name': name, 'user_role': role, 'courses': [course_id], 'model_id': model_id }
#             successful_users.append(data)

#         serializer = UserBatchAddSerializer(data=successful_users, many=True)
#         if serializer.is_valid():
#             serializer.save()

#             # Add existing users to course
#             all_users = existing_users + successful_users
#             for user in all_users:
#                 user_id = str(User.objects.get(utorid=user['utorid']).user_id)
#                 if user['user_role'] == 'ST': course.students.append(user_id) if user_id not in course.students else None
#                 elif user['user_role'] == 'IS': course.instructors.append(user_id) if user_id not in course.instructors else None
#                 elif user['user_role'] == 'RS': course.researchers.append(user_id) if user_id not in course.researchers else None
#                 elif user['user_role'] == 'AM': course.admins.append(user_id) if user_id not in course.admins else None

#                 Course.objects.filter(course_id=course.course_id).update(
#                     students=course.students,
#                     instructors=course.instructors,
#                     researchers=course.researchers,
#                     admins=course.admins
#                 )

#             existing_users = [f"{user['utorid']}: {user['name']}" for user in existing_users]
#             return JsonResponse({"msg": f"Users created.{' Modified existing users (utorid: name): ' + (', '.join(existing_users) if existing_users else '') + '.'}{' Failed to add users: ' + (', '.join(failed_users) if failed_users else '') + '.'}"}, status=status.HTTP_201_CREATED)
#         return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRolesView(APIView):

    @swagger_auto_schema(operation_summary="Get list of user roles")
    # @Controller
    def get(self, request):
        roles = UserService.get_roles()
        return JsonResponse(roles)

# class UserUnenrolledCoursesView(APIView):

#     @swagger_auto_schema(
#         operation_summary="Get unenrolled courses",
#         manual_parameters=[
#             openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
#             openapi.Parameter("utorid", openapi.IN_QUERY, description="Utorid", type=openapi.TYPE_STRING),
#         ],
#     )
#     def get(self, request):
#         """
#         Gets unenrolled courses
#         """
#         user_id = request.query_params.get('user_id', '')
#         utorid = request.query_params.get('utorid', '')

#         if user_id: user = get_object_or_404(User, user_id=user_id)
#         else: user = get_object_or_404(User, utorid=utorid)

#         courses = Course.objects.filter(~Q(course_id__in=user.courses))
#         serializer = CourseSerializer(courses, many=True)
#         return JsonResponse(serializer.data, safe=False)

# class MarkNewUserView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Unmark new user",
#         manual_parameters=[
#             openapi.Parameter("utorid", openapi.IN_QUERY, description="UTORID", type=openapi.TYPE_STRING),
#             openapi.Parameter("deployment_id", openapi.IN_QUERY, description="Deployment ID", type=openapi.TYPE_STRING),
#         ]
#     )
#     def get(self, request):
#         """
#         Unmark new user
#         """
#         utorid = request.query_params.get('utorid', '')
#         deployment_id = request.query_params.get('deployment_id', '')

#         if utorid == '':
#             return ErrorResponse("Bad request", status=status.HTTP_400_BAD_REQUEST)

#         user = get_object_or_404(User, utorid=utorid)

#         updated_deployments = []
#         for deployment in user.status:
#             if deployment['deployment_id'] == deployment_id:
#                 deployment['new_user'] = False
#             updated_deployments.append(deployment)

#         User.objects.filter(user_id=user.user_id).update(status=updated_deployments)
#         UserStatistic(
#             user_id=user.user_id,
#             operation="lab_8_survey_complete",
#         ).save()
#         return JsonResponse({"msg": "User updated"})

class UserDeploymentStatusView(APIView):
    @swagger_auto_schema(
        operation_summary="Get user deployment status",
        manual_parameters=[
            openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
            openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING),
        ],
        responses={200: UserStatusSerializer, 404: "User not found"}
    )
    def get(self, request):
        """
        Get user deployment status
        """
        user_id = request.query_params.get('user_id', '')
        username = request.query_params.get('username', '')
        if not (username):
            username = UserService.get_username_from_headers(request)
        deployments = UserDeploymentStatusService.get_user_deployment_status(user_id, username)
        return JsonResponse(deployments, safe=False)
    
    @swagger_auto_schema(
        operation_summary="Create user deployment status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'deployment_id': openapi.Schema(type=openapi.TYPE_STRING),
                'model_id': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
    )
    def post(self, request):
        """
        Create user deployment status
        """
        data = request.data
        deployment_status = UserDeploymentStatusService.create_user_deployment_status(data)
        return JsonResponse(deployment_status, safe=False)
    
    @swagger_auto_schema(
        operation_summary="Update user deployment status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_id': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
        manual_parameters=[
            openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
            openapi.Parameter("deployment_id", openapi.IN_QUERY, description="Deployment ID", type=openapi.TYPE_STRING),
        ],
    )
    @Controller
    def patch(self, request):
        """
        Update user deployment status
        """
        user_id = request.query_params.get('user_id', '')
        deployment_id = request.query_params.get('deployment_id', '')
        data = request.data
        deployment_status = UserDeploymentStatusService.update_user_deployment_status(user_id, deployment_id, data)
        return JsonResponse(deployment_status)
    
    @swagger_auto_schema(
        operation_summary="Delete user deployment status",
        manual_parameters=[
            openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
            openapi.Parameter("deployment_id", openapi.IN_QUERY, description="Deployment ID", type=openapi.TYPE_STRING),
        ],
    )
    def delete(self, request):
        """
        Delete user deployment status
        """
        user_id = request.query_params.get('user_id', '')
        deployment_id = request.query_params.get('deployment_id', '')
        UserDeploymentStatusService.delete_user_deployment_status(user_id, deployment_id)
        return JsonResponse({"msg": "User deployment status deleted"})

class UserDeploymentStatusListView(APIView):

    @swagger_auto_schema(
        operation_summary="Get all user deployment statuses",
        manual_parameters=[Parameter("deployment_id", IN_QUERY, description="Deployment ID", type=TYPE_STRING)],
        responses={200: UserStatusSerializer(many=True), 404: "No user deployment statuses found"}
    )
    @Controller
    def get(self, request):
        """
        Get all user deployment statuses
        """
        deployment_id = request.query_params.get('deployment_id', '')
        user_deployment_statuses = UserDeploymentStatusService.get_all_user_deployment_status_by_deployment_id(deployment_id)
        return JsonResponse(user_deployment_statuses, safe=False)

class UserStatisticView(APIView):

    @swagger_auto_schema(
        operation_summary="Create new user statistic",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'operation': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        """
        Create a new user statistic
        """
        user_id = request.data.get('user_id', '')
        username = request.data.get('utorid', '')
        operation = request.data.get('operation', '')
        UserService.save_operation(user_id, username, operation)
        return JsonResponse({})
