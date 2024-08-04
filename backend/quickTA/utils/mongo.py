import pymongo
from django.conf import settings
from enum import Enum

USER = "users"
USER_DEPLOYMENT = "user_deployment"
USER_STATISTIC = "user_statistics"
COURSE = "course"
COURSE_DEPLOYMENT = "course_deployment"
MODEL = "models"
MODEL_RESPONSE = "model_response"
CHATLOG = "chatlog"
CONVERSATION = "conversation"
STRATEGY = "strategy"

# Views
CONVERSATION_DETAILED = "conversation_detailed"
class MongoConnection:
    __instance = None

    @staticmethod
    def get_instance():
        if MongoConnection.__instance is None:
            MongoConnection()
        return MongoConnection.__instance

    def __init__(self):
        if MongoConnection.__instance is not None:
            raise Exception("Singleton class, use get_instance() method instead")
        else:
            MONGO_URI = settings.DATABASES['default']['CLIENT']['host']
            self.client = pymongo.MongoClient(MONGO_URI)
            self.db = self.client['quickTA']
            MongoConnection.__instance = self

# Database instance for each collection
client = MongoConnection.get_instance()

USER_DB = client.db[USER]
USER_DEPLOYMENT_DB = client.db[USER_DEPLOYMENT]
USER_STATISTIC_DB = client.db[USER_STATISTIC]
COURSE_DB = client.db[COURSE]
COURSE_DEPLOYMENT_DB = client.db[COURSE_DEPLOYMENT]
MODEL_DB = client.db[MODEL]
MODEL_RESPONSE_DB = client.db[MODEL_RESPONSE]
CHATLOG_DB = client.db[CHATLOG]
CONVERSATION_DB = client.db[CONVERSATION]
STRATEGY_DB = client.db[STRATEGY]

CONVERSATION_DETAILED_VIEW = client.db[CONVERSATION_DETAILED]

class SORTING(Enum):
    ASCENDING = 1
    DESCENDING = -1