from pydantic import BaseModel
from typing import List

class EligibilityRequest(BaseModel):
    gpa: float
    income: float
    program: str
    nationality: str
    academic_level: str

class EligibilityResponse(BaseModel):
    eligible: bool
    analysis: str
    recommended_scholarships: List[str]
    next_steps: List[str]