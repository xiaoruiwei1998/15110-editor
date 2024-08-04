import logging
from typing import *
from users.model import User
from utils.config import *
from utils import *

class UserRepository:

    logger = get_logger(__name__)

    @staticmethod
    def create_user(user: User):
        user["created_at"] = now()
        user["updated_at"] = now()
        USER_DB.insert_one(user)
        return user

    @staticmethod
    def find_user_by_username(username: str):
        return USER_DB.find_one({"username": username})

    @staticmethod
    def find_user_by_id(user_id: str):
        return USER_DB.find_one({"_id": user_id})

    @staticmethod
    def update_user(user_id: str, data: dict):
        data["updated_at"] = now()
        USER_DB.update_one({"_id": user_id}, {"$set": data})
        return USER_DB.find_one({"_id": user_id})

    @staticmethod
    def delete_user(field_name: str, value: str):
        return USER_DB.delete_one({field_name: value})

    @staticmethod
    def find_all_users():
        return list(USER_DB.find({}))

    @staticmethod
    def find_users_by_usernames(usernames: list):
        return list(USER_DB.find({"username": {"$in": usernames}}))

    @staticmethod
    def batch_add_users(users: list):
        for user in users:
            user["_id"] = uuid4()
            user["created_at"] = now()
            user["updated_at"] = now()
        USER_DB.insert_many(users)
        return users

    @staticmethod
    def find_users_by_user_ids(user_ids: List[str]):
        return list(USER_DB.find({"_id": {"$in": user_ids}}))
    
    @staticmethod   
    def enroll_users_to_course(user_ids: List[str], course_id: str):
        USER_DB.update_many({"_id": {"$in": user_ids}}, {"$addToSet": {"courses": course_id}})

    @staticmethod 
    def unenroll_users_from_course(user_ids: List[str], course_id: str):
        USER_DB.update_many({"_id": {"$in": user_ids}}, {"$pull": {"courses": course_id}})

class UserStatisticRepository:

    @staticmethod
    def save_operation(user_id: str, operation: str):
        USER_STATISTIC_DB.insert_one({"_id": uuid4(), "user_id": user_id, "operation": operation, "time": now()})


class UserDeploymentStatusRepository:

    def get_user_deployments(user_id: str) -> List[dict]:
        user = USER_DB.find_one({"_id": user_id})
        user_deployment_statuses = user.get("status", [])
        return user_deployment_statuses

    def create_user_deployments(data: List[dict]):
        data = [{"_id": uuid4(), **user_deployment} for user_deployment in data]
        USER_DEPLOYMENT_DB.insert_many(data)
        return data
    
    def update_user_deployment(user_id: str, deployment_id: str, data: dict):
        USER_DEPLOYMENT_DB.update_one({"user_id": user_id, "deployment_id": deployment_id}, {"$set": data})
        return USER_DEPLOYMENT_DB.find_one({"user_id": user_id, "deployment_id": deployment_id})
    
    def delete_user_deployment(user_id: str, deployment_id: str):
        USER_DEPLOYMENT_DB.delete_one({"user_id": user_id, "deployment_id": deployment_id})

    def get_all_users_by_deployment_id(deployment_id: str):
        return list(USER_DEPLOYMENT_DB.find({"deployment_id": deployment_id}).sort("condition").sort("username", -1))
