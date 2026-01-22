from typing import List, Dict, Any, TYPE_CHECKING
from domain import RAGResponse, DocumentType
from infrastructure.llm_service import LLMService
from infrastructure.vector_store_service import VectorStoreService
from infrastructure.cache_service import CacheService
from application.scholarship.prompts.scholarship_qa import SCHOLARSHIP_QA_PROMPT
from application.scholarship.prompts.eligibility_check import ELIGIBILITY_CHECK_PROMPT

if TYPE_CHECKING:
    from infrastructure.llm_service import LLMService

class ScholarshipService:
    def __init__(self):
        self.llm_service: 'LLMService' = LLMService()
        self.vector_store = VectorStoreService()
        self.cache_service = CacheService()
    
    async def ask_question(self, question: str) -> RAGResponse:
        # Check cache first
        cache_key = self.cache_service.generate_question_key(question)
        cached_response = await self.cache_service.get(cache_key)
        if cached_response:
            print(f"   📋 Cache hit for question: {question[:50]}...")
            return RAGResponse(**cached_response)

        # Search for relevant documents
        search_results = await self.vector_store.search(
            question,
            document_type=DocumentType.SCHOLARSHIP,
            limit=5
        )

        # Build context from search results
        context = "\n\n".join([result.chunk.content for result in search_results])

        # Generate answer using LLM
        prompt = SCHOLARSHIP_QA_PROMPT.format(question=question, context=context)
        answer = await self.llm_service.generate_response(prompt)

        response = RAGResponse(
            answer=answer,
            sources=search_results,
            context=context,
            confidence=min([result.score for result in search_results]) if search_results else 0.0
        )

        # Cache the response
        await self.cache_service.set(cache_key, response.dict())
        print(f"   💾 Cached response for question: {question[:50]}...")

        return response
    
    async def check_eligibility(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check cache first
        cache_key = self.cache_service.generate_eligibility_key(student_data)
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            print(f"   📋 Cache hit for eligibility check: {student_data}")
            return cached_result

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

        result = {
            "eligible": "eligible" in analysis.lower(),
            "analysis": analysis,
            "recommended_scholarships": self._extract_recommended_scholarships(analysis),
            "next_steps": self._generate_next_steps(analysis)
        }

        # Cache the result
        await self.cache_service.set(cache_key, result)
        print(f"   💾 Cached eligibility result for: {student_data}")

        return result
    
    def _extract_recommended_scholarships(self, analysis: str) -> List[str]:
        # Implement logic to extract scholarship names from analysis
        return ["Merit Scholarship", "Need-Based Scholarship"]
    
    def _generate_next_steps(self, analysis: str) -> List[str]:
        return [
            "Submit required documents",
            "Complete scholarship application form",
            "Contact financial aid office"
        ]