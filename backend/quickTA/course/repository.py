import logging
from utils import *

class CourseRepository:

    logger = get_logger(__name__)

    @staticmethod
    def find_course_by_id(course_id: str, show_users: bool = False, detailed_info: bool = False):
        
        pipeline = [{ "$match": { "_id": course_id } }]
        if show_users:
            pipeline.extend([
                { "$lookup": {
                    "from": "users",
                    "localField": "students",
                    "foreignField": "_id",
                    "as": "students"
                }},
                { "$lookup": {
                    "from": "users",
                    "localField": "instructors",
                    "foreignField": "_id",
                    "as": "instructors"
                }},
                { "$lookup": {
                    "from": "users",
                    "localField": "admins",
                    "foreignField": "_id",
                    "as": "admins"
                }},
                { "$lookup": {
                    "from": "users",
                    "localField": "researchers",
                    "foreignField": "_id",
                    "as": "researchers"
                }}
            ])

        result = list(COURSE_DB.aggregate(pipeline)) 
        return result[0] if result else None
    
    @staticmethod
    def find_course_by_code_semester(course_code: str, semester: str):
        return COURSE_DB.find_one({"course_code": course_code, "semester": semester})
    
    @staticmethod
    def create_course(data: dict):
        COURSE_DB.insert_one(data)
        return data
    
    @staticmethod
    def update_course(course_id: str, data: dict):
        COURSE_DB.update_one({"_id": course_id}, {"$set": data})
        return COURSE_DB.find_one({"_id": course_id})

    @staticmethod
    def delete_course(course_id: str):
        COURSE_DB.delete_one({"_id": course_id})

    @staticmethod
    def find_all_courses():
        return list(COURSE_DB.find())
    
    @staticmethod
    def get_all_courses_with_user_details():
        return list(COURSE_DB.aggregate([
            {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'students', 
                    'foreignField': '_id', 
                    'as': 'students'
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'instructors', 
                    'foreignField': '_id', 
                    'as': 'instructors'
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'admins', 
                    'foreignField': '_id', 
                    'as': 'admins'
                }
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'researchers', 
                    'foreignField': '_id', 
                    'as': 'researchers'
                }
            }
        ]))

    @staticmethod
    def find_courses_by_ids(course_ids: list):
        return list(COURSE_DB.find({"_id": {"$in": course_ids}}))
    
    @staticmethod
    def enroll_users_to_course(course_id: str, role_field: str, user_ids: list):
        """
        course_id: str
        role_field: (admins, instructors, researchers, students)
        user_ids: list of user_ids
        """
        COURSE_DB.update(
            {"_id": course_id},
            {"$addToSet": {role_field: {"$each": user_ids}}}
        )

    @staticmethod
    def unenroll_users_from_course(course_id: str, role: str, user_ids: list):
        role_field = COURSE_ROLE_MAP[role]
        COURSE_DB.update(
            {"_id": course_id},
            {"$pull": {role_field: {"$in": user_ids}}}
        )

    @staticmethod
    def find_course_models(course_id: str):
        return list(COURSE_DB.find({"_id": course_id}, {"models": 1}))


class CourseDeploymentRepository:
    
    logger = get_logger(__name__)

    def find_deployment_by_id(deployment_id: str):
        return COURSE_DEPLOYMENT_DB.find_one({"_id": deployment_id})

    def find_deployments_by_course_id(course_id: str):
        return list(COURSE_DEPLOYMENT_DB.find({"course_id": course_id}))
    
    def find_deployment_details_by_course_id(course_id: str):
        return list(COURSE_DEPLOYMENT_DB.aggregate([
            {
                "$match": {
                    "course_id": course_id
                }
            },
            {
                "$lookup": {
                    "from": ASSESSMENT_DB,
                    "localField": "assessment_ids",
                    "foreignField": "_id",
                    "as": "assessments"
                }
            },
            {
                "$lookup": {
                    "from": SURVEY_DB,
                    "localField": "survey_ids",
                    "foreignField": "_id",
                    "as": "surveys"
                }
            }
        ]))

    def find_course_deployments(deployment_id: str):
        return COURSE_DEPLOYMENT_DB.find_one({"_id": deployment_id})    
    
    def create_course_deployment(data: dict):
        data["_id"] = uuid4()
        data['assessment_ids'] = data.get('assessment_ids', [])
        data['survey_ids'] = data.get('survey_ids', [])
        COURSE_DEPLOYMENT_DB.insert_one(data)
        return data
    
    def update_course_deployment(deployment_id: str, data: dict):
        COURSE_DEPLOYMENT_DB.update_one({"_id": deployment_id}, {"$set": data})
        return COURSE_DEPLOYMENT_DB.find_one({"_id": deployment_id})

    def delete_course_deployment(deployment_id: str):
        COURSE_DEPLOYMENT_DB.delete_one({"_id": deployment_id})

    def enroll_all_users_to_deployment(user_ids: List[str], status: dict):
        USER_DB.update_many(
            {"_id": {"$in": user_ids}},
            {"$addToSet": {"status": status}}
        )
        return list(USER_DB.find({"_id": {"$in": user_ids}}))



