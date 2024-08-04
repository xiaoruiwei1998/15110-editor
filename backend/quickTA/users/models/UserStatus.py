from pydantic import BaseModel
from typing import Optional

class UserStep(BaseModel):
    step: int = 0
    status: str = "not-started"
    model_id: str
    survey_response_id: str
    assessment_response_id: str
  