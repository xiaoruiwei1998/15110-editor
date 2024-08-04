from drf_yasg import openapi
from utils import *

def get_course(params):
    pass

def get_user_from_request_params(params):
    user_id = params.get("user_id", "")
    username = params.get("username", "")
    role = params.get("role", "")
    return user_id, username, role

def get_course_from_request_params(params):
    course_id = params.get("course_id", "")
    course_code = params.get("course_code", "")
    semester = params.get("semester", "")
    show_users = params.get("show_users", False)
    return course_id, course_code, semester, show_users

def get_roles_from_request_params(params):
    user_roles = params.get('user_roles', [])
    if user_roles: 
        user_roles = user_roles.split(',')
        for role in user_roles:
            if role not in ROLE_MAP_ENUM:
                raise BadRequestError(f"Invalid role {role}")
        return user_roles
    return ROLE_MAP_ENUM
    
def get_course_ids_from_request_params(params):
    course_ids = params.get('course_ids', [])
    if course_ids: 
        course_ids = course_ids.split(',')
    else: 
        raise BadRequestError("Please provide a list of course IDs")
    return course_ids

def user_identifier_params():
    return [
        openapi.Parameter("user_id", openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING),
        openapi.Parameter("username", openapi.IN_QUERY, description="Username", type=openapi.TYPE_STRING),
        openapi.Parameter("role", openapi.IN_QUERY, description="Role", type=openapi.TYPE_STRING, enum=ROLE_MAP_ENUM)
    ]
def course_identifier_params():
    return [
        openapi.Parameter("course_id", openapi.IN_QUERY, description="Course ID", type=openapi.TYPE_STRING),
        openapi.Parameter("course_code", openapi.IN_QUERY, description="Course code", type=openapi.TYPE_STRING),
        openapi.Parameter("semester", openapi.IN_QUERY, description="Semester", type=openapi.TYPE_STRING),
    ]