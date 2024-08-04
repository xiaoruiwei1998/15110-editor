from utils import *

class ConversationRepository:

    @staticmethod
    def find_conversation_by_id(conversation_id: str):
        return CONVERSATION_DB.find_one({"_id": conversation_id})
    
    @staticmethod
    def find_conversations_by_user_id(user_id: str):
        return list(CONVERSATION_DB.find({"user_id": user_id}).sort("start_time", -1))
    
    @staticmethod
    def find_conversations_by_course_id(course_id: str, detailed: bool):
        if detailed:
            return list(CONVERSATION_DETAILED_VIEW.find({"course_id": course_id}))
        return list(CONVERSATION_DB.find({"course_id": course_id}))
    
    @staticmethod
    def create_conversation(data: dict):
        conversation = {
            "_id": uuid4(),
            **data,
            "start_time": datetime.now(),
            "end_time": None,
            "status": "A",
            "reported": False,
            "conversation_log": []
        }
        CONVERSATION_DB.insert_one(conversation)
        return conversation
    
    @staticmethod
    def find_all_conversations():
        return list(CONVERSATION_DB.find({}))
    
    @staticmethod
    def get_conversation_history(conversation_id: str):
        return list(CONVERSATION_DB.aggregate([
            {"$match": {"_id": conversation_id}},
            {"$lookup": {
                "from": CHATLOG,
                "localField": "_id",
                "foreignField": "conversation_id",
                "as": "chatlogs"
            }},
        ]))
    
    @staticmethod
    def update_conversation(conversation_id: str, data: dict):
        CONVERSATION_DB.find_one_and_update({"_id": conversation_id}, {"$set": data})
        return data
    
    @staticmethod
    def find_conversations_by_user_course(user_id: str, course_id: str):
        return list(CONVERSATION_DB.find({"user_id": user_id, "course_id": course_id}))
    
    @staticmethod
    def find_conversations_by_user_course_models(user_id: str, course_id: str, model_ids: List[str]):
        pipeline = [{"$match": {"user_id": user_id}}]
        if course_id:
            pipeline.append({"$match": {"course_id": course_id}})
        if model_ids:
            pipeline.append({"$match": {"model_id": {"$in": model_ids}}})
        pipeline.append({"$sort": {"start_time": -1}})    
        return list(CONVERSATION_DB.aggregate(pipeline))
    
    @staticmethod
    def find_conversation_by_model_id(model_id: str):
        return CONVERSATION_DB.find_one({"model_id": model_id})

    @staticmethod
    def add_chatlog_history(conversation_id: str, chatlog: dict, conversation_name: str):
        CONVERSATION_DB.update_one({"_id": conversation_id}, {"$set": {"conversation_name": conversation_name, "conversation_log": chatlog}})

class ChatlogRepository:

    @staticmethod
    def get_chatlogs_by_conversation_id(conversation_id: str, sort: SORTING = SORTING.ASCENDING):
        return list(CHATLOG_DB
                    .find({"conversation_id": conversation_id})
                    .sort("time", sort.value))
    
    @staticmethod
    def create_chatlog(data: dict):
        data["_id"] = uuid4()
        CHATLOG_DB.insert_one(data)
        return data
    
    @staticmethod
    def get_last_chatlog(conversation_id: str):
        return CHATLOG_DB.find_one({"conversation_id": conversation_id}, sort=[("time", -1)])
    
    @staticmethod
    def save_model_response(data: dict):
        CHATLOG_DB.insert_one(data)
    
    @staticmethod
    def find_all_chatlogs():
        return list(CHATLOG_DB.find({}))
    
    @staticmethod
    def update_chatlog(chatlog_id: str, data: dict):
        CHATLOG_DB.find_one_and_update({"_id": chatlog_id}, {"$set": data})
    
class FeedbackRepository:

    @staticmethod
    def find_feedback_by_conversation_id(conversation_id: str):
        return FEEDBACK_DB.find_one({"conversation_id": conversation_id})
    
    @staticmethod
    def create_feedback(data: dict):
        data["_id"] = uuid4()
        FEEDBACK_DB.insert_one(data)
        return data    

    @staticmethod
    def update_feedback(conversation_id: str, data: dict):
        FEEDBACK_DB.update_one({"conversation_id": conversation_id}, {"$set": data}, upsert=True)
        return data
    
    @staticmethod
    def find_all_feedback():
        return list(FEEDBACK_DB.find({}))

class ReportRepository:

    @staticmethod
    def find_report_by_conversation_id(conversation_id: str):
        return REPORT_DB.find_one({"conversation_id": conversation_id})
    
    @staticmethod
    def create_report(data: dict):
        data["_id"] = uuid4()
        data["time"] = datetime.now()
        data["status"] = "O"
        REPORT_DB.insert_one(data)
        return data
    
    @staticmethod
    def find_all_reports():
        return list(REPORT_DB.find({}))
    
class ConversationNotesRepository:
    def find_conversation_notes(conversation_id: str):
        return CONVERSATION_NOTES_DB.find_one({"conversation_id": conversation_id})
    
    def upsert_conversation_notes(data: dict):
        conversation = CONVERSATION_NOTES_DB.find_one({"conversation_id": data["conversation_id"]})
        if conversation:
            data["updated_at"] = now()
            CONVERSATION_NOTES_DB.update_one({"conversation_id": data["conversation_id"]}, {"$set": data})
        else:
            data["_id"] = uuid4()
            data["created_at"] = now()
            data["updated_at"] = now()
            CONVERSATION_NOTES_DB.insert_one(data)