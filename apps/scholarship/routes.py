from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from apps.scholarship.service import ScholarshipService
from schemas import ChatRequest, ChatResponse, EligibilityRequest, EligibilityResponse

router = APIRouter()
scholarship_service = ScholarshipService()

@router.post("/ask", response_model=ChatResponse)
async def ask_scholarship_question(request: ChatRequest):
    try:
        response = await scholarship_service.ask_question(request.question)
        return ChatResponse(
            answer=response.answer,
            sources=[source.source for source in response.sources],
            confidence=response.confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-eligibility", response_model=EligibilityResponse)
async def check_eligibility(request: EligibilityRequest):
    try:
        student_data = {
            "gpa": request.gpa,
            "income": request.income,
            "program": request.program,
            "nationality": request.nationality,
            "academic_level": request.academic_level
        }
        result = await scholarship_service.check_eligibility(student_data)
        return EligibilityResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deadlines")
async def get_scholarship_deadlines():
    # Implement deadline retrieval logic
    return {
        "deadlines": [
            {"scholarship": "Merit Scholarship", "deadline": "2024-03-15"},
            {"scholarship": "Need-Based Aid", "deadline": "2024-04-01"}
        ]
    }