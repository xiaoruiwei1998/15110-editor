from utils import *
from course.models import CourseDeployment, DeploymentStepType
from models.repository.model_repository import ModelRepository
from users.repository import UserRepository
from course.serializers import CourseSerializer, CourseDeploymentSerializer
from course.repository import CourseRepository, CourseDeploymentRepository
from users.service import UserService

log = get_logger(__name__)

class CourseService:

    @staticmethod
    def get_course_id(course_id: str, course_code: str, semester: str):
        if course_id != "": 
            return course_id
        elif course_code != "" and semester != "": 
            course = CourseRepository.find_course_by_code_semester(course_code, semester)
            return course["_id"]
        raise BadRequestError("Either course_id or course_code and semester must be provided")
        
    @staticmethod
    def get_course(course_id: str, course_code: str = "", semester: str = "", show_users: str = False, detailed_info: str = False) -> dict:
        if course_id != "": course = CourseRepository.find_course_by_id(course_id, show_users, detailed_info)
        elif course_code != "" and semester != "": course = CourseRepository.find_course_by_code_semester(course_code, semester)
        else: raise BadRequestError("Either course_id or course_code and semester must be provided")

        if course is None: 
            if course_id != "": 
                raise ValueError(f"Course {course_id} not found")
            raise ValueError(f"Course {course_code} {semester} not found")
        
        if show_users not in ["true", True]:
            course.pop("students")
            course.pop("instructors")
            course.pop("researchers")
            course.pop("admins")
        return course
    
    @staticmethod
    def create_course(data: dict, course_code: str, semester: str) -> dict:
        CourseService.ensure_course_uniqueness(course_code, semester)
        serializer = CourseSerializer(data=data)
        if not serializer.is_valid():
            raise BadRequestError(serializer.errors)

        course_data = {"_id": uuid4(), **serializer.data}
        return CourseRepository.create_course(course_data)
    
    @staticmethod
    def validate_update_course(data: dict):
        editable_course_fields = ["course_code", "semester", "course_name", "start_date", "end_date"]
        if not data:
            raise BadRequestError("No data provided")
        for key in data.keys():
            if key not in editable_course_fields:
                raise BadRequestError(f"Invalid fields provided: {key}")

    @staticmethod
    def update_course(course_id: str, course_code: str, semester: str, data: dict) -> dict:
        new_course_code = data.get('course_code', '')
        new_semester = data.get('semester', '')

        course = CourseService.get_course(course_id, course_code, semester, True)
        if (new_course_code or new_semester) and course_id != course["_id"]:
            CourseService.ensure_course_uniqueness(new_course_code, new_semester)

        CourseService.validate_update_course(data)
        return CourseRepository.update_course(course["_id"], data)
    
    @staticmethod
    def delete_course(course_id: str, course_code: str, semester: str) -> dict:
        course = CourseService.get_course(course_id, course_code, semester, True)

        if course["students"] or course["instructors"] or course["researchers"] or course["admins"]:
            raise BadRequestError("Course cannot be deleted because it has users")

        return CourseRepository.delete_course(course["_id"])

    @staticmethod
    def ensure_course_uniqueness(course_code: str, semester: str):
        course = CourseRepository.find_course_by_code_semester(course_code, semester)
        if course:
            raise BadRequestError(f"Course {course_code} {semester} already exists")

    @staticmethod
    def get_all_courses(show_user_details: bool):
        if show_user_details not in ["false", False]:
            return CourseRepository.get_all_courses_with_user_details()
        return CourseRepository.find_all_courses()
    
    @staticmethod
    def enroll_user(course_id: str, course_code: str, semester: str, user_id: str, username: str, role: str, enroll_deployments: bool):
        
        role_field = CourseService.validate_role_field(role)
        course = CourseRepository.find_course_by_id(course_id)
        user = UserService.get_user(user_id, username)
        if (CourseService.user_in_course(course, user["_id"])): 
            raise BadRequestError(f"[{role}] {user_id if user_id != '' else username} already enrolled in course: {course_id if course_id != '' else course_code + ' ' + semester}")

        # Update course
        course[role_field].append(user["_id"])
        course[role_field] = list(set(course[role_field]))

        log.info(f"Enrolling {role} ({role_field}) {user_id if user_id != '' else username} to course: {course_id if course_id != '' else course_code + ' ' + semester}")
        CourseRepository.update_course(course["_id"], {role_field: course[role_field]})

        # Update user courses
        user["courses"].append(course["_id"])
        user["courses"] = list(set(user["courses"]))
        log.info(f"Enrolling course {course_id if course_id != '' else course_code + ' ' + semester} to user {user_id if user_id != '' else username}")
        user_update_fields = {"courses": user["courses"]}

        # Update user deployments
        if enroll_deployments:
            # TODO - DYNAMIC ASSIGNATION - BASED ON MODEL DISTRIBUTION STRATEGY
            model = ModelRepository.find_models_by_course_id(course["_id"])
            if len(model) > 0: 
                model = model[0]["_id"]

            user["status"].append({
                "deployment_id": "",
                "new_user": True,
                "model_id": model,
                "active": True
            })
            user_update_fields["status"] = user["status"]

        return UserRepository.update_user(user["_id"], user_update_fields)

    @staticmethod
    def unenroll_user(course_id: str, course_code: str, semester: str, user_id: str, username: str, role: str):
        role_field = CourseService.validate_role_field(role)
        
        course = CourseRepository.find_course_by_id(course_id)
        user = UserService.get_user(user_id, username)
        if not (CourseService.user_in_course(course, user["_id"])): 
            raise BadRequestError(f"[{role}] {user_id if user_id != '' else username} not enrolled in course: {course_id if course_id != '' else course_code + ' ' + semester}")

        # Update course
        course[role_field].remove(user["_id"])
        CourseRepository.update_course(course["_id"], course)

        # Update user
        user["courses"].remove(course["_id"])
        return UserRepository.update_user(user["_id"], {"courses": user["courses"]})
    
    @staticmethod
    def get_course_user_list(course_id: str, course_code: str, semester: str, user_roles: list):
        course = CourseService.get_course(course_id, course_code, semester, True)
        
        user_list = dict()
        roles = [COURSE_ROLE_MAP[role] for role in COURSE_ROLE_MAP.keys() if role in user_roles]

        for role in roles:
            user_list[role] = UserRepository.find_users_by_user_ids(course[role])
        return user_list
    
    @staticmethod
    def get_courses_by_user(user_id: str, username: str, user_roles: list):
        user = UserService.get_user(user_id, username)
        user_courses = CourseRepository.find_courses_by_user(user["_id"], user_roles)
        return user_courses

    @staticmethod
    def validate_role_field(role: str):
        role_field = COURSE_ROLE_MAP.get(role, None)
        if not role_field:
            raise BadRequestError("User role is required")
        return role_field
    
    @staticmethod
    def user_in_course(course: dict, user_id: str):
        for role_field in COURSE_ROLE_MAP.values():
            if (user_id in course[role_field]):
                return True
        return False
    
    @staticmethod
    def get_multiple_courses(course_ids: list):
        courses = CourseRepository.find_courses_by_ids(course_ids)
        for course in courses:
            course.pop("students")
            course.pop("instructors")
            course.pop("researchers")
            course.pop("admins")
        return courses
    
    @staticmethod
    def get_unenrolled_users(course_id: str, course_code: str, semester: str, roles: str):
        course = CourseRepository.find_course_by_id(course_id)
        users = UserRepository.find_all_users()
        users = [user for user in users if user.get("role", "") in roles]

        course_role_fields = [COURSE_ROLE_MAP[role] for role in roles]
        unenrolled_users = dict()

        for role in course_role_fields:
            role_users = [user for user in users if user["_id"] not in course[role]]
            # print(course[role])
            unenrolled_users[role] = role_users
            log.info(f"Acquired {len(role_users)} users for role: {role}")

        return {role: [user for user in users] for role, users in unenrolled_users.items()}
    
    @staticmethod
    def enroll_multiple_users(course_id: str, course_code: str, semester: str, users: list, role: str):
        course = CourseService.get_course(course_id, course_code, semester, True)
        role_field = COURSE_ROLE_MAP[role]
        user_ids = [user.get("_id", "") for user in users]
        enrolled_users = flatten([course[role] for role in COURSE_ROLE_MAP.values()])
        enrolled_user_ids = [user.get("_id", "") for user in enrolled_users]
        unenrolled_user_ids = list(set(user_ids) - set(enrolled_user_ids))

        CourseRepository.enroll_users_to_course(course_id, role_field, unenrolled_user_ids)
        UserRepository.enroll_users_to_course(unenrolled_user_ids, course_id)

        enrolled_usernames = [user["username"] for user in users if user["_id"] in unenrolled_user_ids]
        return enrolled_usernames
    
    @staticmethod
    def unenroll_multiple_users(course_id: str, course_code: str, semester: str, users: list, role: list):
        course = CourseService.get_course(course_id, course_code, semester, True)

        role_field = COURSE_ROLE_MAP[role]
        user_ids = [user.get("_id", "") for user in users]
        all_enrolled_user_ids = flatten([course[role] for role in course[COURSE_ROLE_MAP.values()]])
        enrolled_user_ids = list(set(user_ids) & set(all_enrolled_user_ids))
        unenrolled_user_ids = list(set(user_ids) - set(enrolled_user_ids))

        CourseRepository.unenroll_users_from_course(course_id, enrolled_user_ids, role_field)
        UserRepository.unenroll_users_from_course(enrolled_user_ids, course_id)

        unenrolled_usernames = [user["username"] for user in users if user["_id"] in unenrolled_user_ids]
        return unenrolled_usernames

    @staticmethod
    def get_course_models(course_id: str, course_name: str, semester: str, show_all: bool):
        if course_name and semester:
            course = CourseService.get_course("", course_name, semester, True)
            course_id = course["_id"]
        models = ModelRepository.find_models_by_course_id(course_id)
        response = []
        if not show_all:
            for model in models:
                response.append({
                    "model_id": str(model["_id"]),
                    "model_name": model["model_name"],
                    "course_id": model["course_id"],
                    "status": model["status"],
                    "default_message": model.get("default_message", ""),
                    "model_header_name": model.get("model_header_name", ""),
                    "model_preheader_name": model.get("model_preheader_name", ""),
                    "model_header_information": model.get("model_header_information", ""),
                    "enableTTS": model.get("enableTTS", False),
                    "enableSTT": model.get("enableSTT", False),
                    "enableNotes": model.get("enableNotes", False),
                    "enableNewConversation": model.get("enableNewConversation", False),
                    "enableGuardrails": model.get("enableGuardrails", False),
                    "enableEvaluationResults": model.get("enableEvaluationResults", False),
                })
        return response