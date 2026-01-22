from typing import Any, Dict, List, Optional
from models.rag_models import DocumentType
from services.llm_service import LLMService
from services.vector_store_service import VectorStoreService


class FAQAgent:
    def __init__(self, domain: str):
        self.domain = domain
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.document_type = DocumentType(domain)


    async def answer_question(self, question: str) -> Dict[str, Any]:
        # Enhanced RAG with follow-up questions
        search_results = await self.vector_store.search(
            question, 
            document_type=self.document_type,
            limit=5
        )
        
        context = "\n\n".join([result.chunk.content for result in search_results])
        
        # Generate answer with potential follow-ups
        prompt = f"""
        Question: {question}
        Context: {context}

        Provide:
        1. Direct answer
        2. 2-3 potential follow-up questions the student might have
        3. Confidence level (high/medium/low)
        """

        response = await self.llm_service.generate_response(prompt)
        
        return {
            "answer": self._extract_answer(response),
            "follow_up_questions": self._extract_follow_ups(response),
            "confidence": self._extract_confidence(response),
            "sources": [result.source for result in search_results]
        }

    def _extract_answer(self, response: str) -> str:
        # Extract the direct answer from the response
        try:
            parts = response.split("1. Direct answer")
            if len(parts) > 1:
                answer_part = parts[1].split("2.")[0].strip()
                return answer_part
            return response  # Fallback
        except:
            return response

    def _extract_follow_ups(self, response: str) -> List[str]:
        # Extract follow-up questions
        try:
            parts = response.split("2.")
            if len(parts) > 1:
                follow_up_part = parts[1].split("3.")[0].strip()
                # Split by newlines or bullets
                questions = [q.strip("- ").strip() for q in follow_up_part.split("\n") if q.strip()]
                return questions[:3]  # Limit to 3
            return []
        except:
            return []

    def _extract_confidence(self, response: str) -> str:
        # Extract confidence level
        try:
            parts = response.split("3. Confidence level")
            if len(parts) > 1:
                confidence = parts[1].strip().lower()
                if "high" in confidence:
                    return "high"
                elif "medium" in confidence:
                    return "medium"
                elif "low" in confidence:
                    return "low"
            return "medium"  # Default
        except:
            return "medium"

    