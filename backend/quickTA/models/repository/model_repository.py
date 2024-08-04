from utils import * 


class ModelRepository:

    def find_model_by_id(model_id: str):
        return MODEL_DB.find_one({"_id": model_id})

    def find_models_by_id(model_id: List[str]):
        if len(model_id) > 1:
            return list(MODEL_DB.find({"_id": {"$in": model_id}}))
        print(model_id)
        return MODEL_DB.find_one({"_id": model_id[0]})
    
    def create_model(data: dict):
        data["_id"] = uuid4()
        MODEL_DB.insert_one(data)
        return data
    
    def delete_model(model_id: str):
        return MODEL_DB.delete_one({"_id": model_id})

    def update_model(model_id: str, data: dict):
        MODEL_DB.update_one({"_id": model_id}, {"$set": data})
        return MODEL_DB.find_one({"_id": model_id})
    
    def find_models_by_course_id(course_id: str):
        pipeline = [
            {"$match": {"course_id": course_id}},
            {"$lookup": { 
                "from": COURSE_DEPLOYMENT,
                "localField": "deployment_id",
                "foreignField": "_id",
                "as": "deployment"
            }},
            # project first object's field "deployment_name" as "deployment_name", keep all other fields
            {"$addFields": {
                "deployment_name": {"$arrayElemAt": ["$deployment.name", 0]}
            }}
        ]
        return list(MODEL_DB.aggregate(pipeline))
    
    def find_all_models():
        return list(MODEL_DB.find({}))
    
    def update_model_status(model_id: str, status: bool):
        return MODEL_DB.update_one({"_id": model_id}, {"$set": {"status": status}})
    
    def find_models_by_user_id(user_id: str):
        return list(MODEL_DB.find({"user_id": user_id}))
    
    def find_models_by_deployment_id(deployment_id: str):
        return list(MODEL_DB.find({"deployment_id": deployment_id}))
