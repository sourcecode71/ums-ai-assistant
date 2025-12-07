from typing import List, Dict, Any, TYPE_CHECKING
from models.rag_models import RAGResponse, DocumentType
from services.llm_service import LLMService
from services.vector_store_service import VectorStoreService
from apps.scholarship.prompts.scholarship_qa import SCHOLARSHIP_QA_PROMPT
from apps.scholarship.prompts.eligibility_check import ELIGIBILITY_CHECK_PROMPT

if TYPE_CHECKING:
    from services.llm_service import LLMService

class ScholarshipService:
    def __init__(self):
        self.llm_service: 'LLMService' = LLMService()
        self.vector_store = VectorStoreService()
    
    async def ask_question(self, question: str) -> RAGResponse:
        # Search for relevant documents
        search_results = await self.vector_store.search(
            question, 
            document_type=DocumentType.SCHOLARSHIP,
            limit=5
        )
        
        print(f"   📖 Search Results {search_results}")
        
        # Build context from search results
        context = "\n\n".join([result.chunk.content for result in search_results])
        
        # Generate answer using LLM
        prompt = SCHOLARSHIP_QA_PROMPT.format(question=question, context=context)
        answer = await self.llm_service.generate_response(prompt)
        
        return RAGResponse(
            answer=answer,
            sources=search_results,
            context=context,
            confidence=min([result.score for result in search_results]) if search_results else 0.0
        )
    
    async def check_eligibility(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        # Search for eligibility criteria
        search_results = await self.vector_store.search(
            "eligibility criteria requirements GPA income",
            document_type=DocumentType.SCHOLARSHIP,
            limit=10
        )
        
        eligibility_context = "\n\n".join([result.chunk.content for result in search_results])
        
        prompt = ELIGIBILITY_CHECK_PROMPT.format(
            student_data=str(student_data),
            eligibility_criteria=eligibility_context
        )

        analysis = await self.llm_service.generate_response(prompt)
        
        return {
            "eligible": "eligible" in analysis.lower(),
            "analysis": analysis,
            "recommended_scholarships": self._extract_recommended_scholarships(analysis),
            "next_steps": self._generate_next_steps(analysis)
        }
    
    def _extract_recommended_scholarships(self, analysis: str) -> List[str]:
        # Implement logic to extract scholarship names from analysis
        return ["Merit Scholarship", "Need-Based Scholarship"]
    
    def _generate_next_steps(self, analysis: str) -> List[str]:
        return [
            "Submit required documents",
            "Complete scholarship application form",
            "Contact financial aid office"
        ]