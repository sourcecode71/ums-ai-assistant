import json
import redis
from typing import Optional, Any
from core.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.ttl = settings.CACHE_TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, self.ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def generate_question_key(self, question: str) -> str:
        """Generate cache key for scholarship questions"""
        # Normalize the question for consistent caching
        normalized = question.lower().strip()
        return f"scholarship:question:{hash(normalized)}"

    def generate_eligibility_key(self, student_data: dict) -> str:
        """Generate cache key for eligibility checks"""
        # Create a deterministic key from student data
        key_parts = [
            str(student_data.get('gpa', '')),
            str(student_data.get('income', '')),
            student_data.get('program', ''),
            student_data.get('nationality', ''),
            student_data.get('academic_level', '')
        ]
        key_string = '|'.join(key_parts)
        return f"scholarship:eligibility:{hash(key_string)}"