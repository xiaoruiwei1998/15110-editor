from utils import *
from users.repository import UserRepository, UserStatisticRepository, UserDeploymentStatusRepository
from users.model import *
from users.serializers import *


log = get_logger(__name__)
class UserService:

    # TODO: How to make a logger accessible to static methods

    @staticmethod
    def login(username: str):
        user = UserRepository.find_user_by_username(username)
        if user is None:
            raise ValueError(f"User {username} not found")

        UserStatisticRepository.save_operation(user_id=user["_id"], operation="login")
        log.info(f"User {username} logged in")
        user.pop("created_at")
        user.pop("updated_at")
        return user

    @staticmethod
    def get_username_from_headers(request):
        if 'utorid' in request.headers:
            return request.headers['utorid']
        return ""

    @staticmethod
    def get_user(user_id: str, username: str = ""):
        if (user_id != ""):
            user = UserRepository.find_user_by_id(user_id)
        elif (username != ""):
            user = UserRepository.find_user_by_username(username)
        else:
            raise BadRequestError("Either user_id or username must be provided")

        if user is None:
            log.error(f"User {user_id or username} not found")
            raise ValueError(f"User {user_id or username} not found")

        log.info(f"User {user_id or username} found")
        return user

    @staticmethod
    def create_user(username, data):
        UserService.ensure_user_uniqueness(username)
        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            raise BadRequestError(serializer.errors)

        user_data = {"_id": uuid4(), **serializer.data}
        user = UserRepository.create_user(user_data)
        log.info(f"User {username} created")
        return user

    @staticmethod
    def update_user(user_id: str, username: str, data: dict):
        new_username = data.get('username', '')

        log.info(f"Updating user {username} with data {data}")
        user = UserService.get_user(user_id, username)
        serializer = UserSerializer(user, data=data, partial=True)
        if not (serializer.is_valid()):
            raise BadRequestError(serializer.errors)

        if new_username and new_username != username:
            UserService.ensure_user_uniqueness(new_username)

        return UserRepository.update_user(user["_id"], serializer.data)

    @staticmethod
    def delete_user(user_id: str, username: str):
        user = UserService.get_user(user_id, username)
        if user["courses"]:
            raise ForbiddenError("User is enrolled with courses")

        if user_id: UserRepository.delete_user("user_id", user_id)
        elif username: UserRepository.delete_user("username", username)

    @staticmethod
    def ensure_user_uniqueness(username: str):
        user = UserRepository.find_user_by_username(username)
        if user:
            raise BadRequestError(f"User {username} already exists")

    @staticmethod
    def get_all_users():
        return UserRepository.get_all_users()

    @staticmethod
    def batch_add_users(role: str, data: list):
        UserService.validate_role(role)
        serializer = UserBatchAddSerializer(data=data, role=role, many=True)
        if not serializer.is_valid():
            raise BadRequestError(serializer.errors)

        usernames = [user["username"] for user in data]
        existing_users = UserRepository.find_users_by_usernames(usernames)
        if existing_users:
            existing_users = [user["username"] for user in existing_users]
            raise BadRequestError(f"Users {existing_users} already exist")

        return UserRepository.batch_add_users(serializer.data)

    @staticmethod
    def validate_role(role: str):
        if role not in list(ROLE_MAP.keys()):
            raise BadRequestError(f"Invalid role provided: {role}")

    @staticmethod
    def get_user_roles():
        response = {"roles": []}
        for role in ROLE_MAP.keys():
            response["roles"].append({"id": role, "name": ROLE_MAP[role].capitalize()})
        return response

    @staticmethod
    def save_operation(user_id: str, username: str, operation: str):
        if user_id == "" and username:
            user = UserRepository.find_user_by_username(username)
            user_id = user["_id"]
        elif username == "":
            raise BadRequestError("Either user_id or username must be provided")
        
        UserStatisticRepository.save_operation(user_id, operation)
        log.info(f"User {user_id} performed operation {operation}")

    @staticmethod
    def get_user_full_name(user: dict):
        if user["name"]:
            return user["name"]
        return user["username"]
    
    @staticmethod
    def get_roles():
        res = { "roles": [] }
        for role in ROLE_MAP.keys():
            res["roles"].append({ "id": role, "name": ROLE_MAP[role].capitalize() })
        return res

class UserDeploymentStatusService:

    def get_user_deployment_status(user_id: str, username: str = "") -> List[dict]:
        if user_id == "": user_id = UserService.get_user(user_id, username).get("_id", "")
        deployment_statuses = UserDeploymentStatusRepository.get_user_deployments(user_id)
        return deployment_statuses

    def create_user_deployment_status(data: dict):
        deployment_status = UserDeploymentStatusRepository.create_user_deployments([data])
        return deployment_status[0]
    
    def update_user_deployment_status(user_id: str, deployment_id: str, data: dict):
        # user = UserService.get_user(user_id)
        # status = user.get("status", [])
        return UserRepository.update_user(user_id, { "status": data })
    
    def delete_user_deployment_status(user_id: str, deployment_id: str):
        UserDeploymentStatusRepository.delete_user_deployment(user_id, deployment_id)

    def update_user_status_by_user_id(user_id: str, deployment_id: str, data: dict):
        user = UserService.get_user(user_id)
        status = user.get("status", [])
        
        updated = False
        for i, deployment in enumerate(status):
            if deployment.get("deployment_id", "") == deployment_id:
                status[i] = {**status[i], **data}
                updated = True
                break

        if not updated: status.append(data)
        UserRepository.update_user(user_id, { "status": status })

    def get_all_user_deployment_status_by_deployment_id(deployment_id: str):
        return UserDeploymentStatusRepository.get_all_users_by_deployment_id(deployment_id)