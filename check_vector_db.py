import asyncio
from services.vector_store_service import VectorStoreService

async def check_storage():
    vector_store = VectorStoreService()

    # Check collection stats
    collection = vector_store.collection
    count = collection.count()
    print(f"Documents in vector DB: {count}")

    # Try a test search
    results = await vector_store.search("scholarship", limit=3)
    print(f"Test search found {len(results)} results")

    if results:
        print("\nSample result:")
        print(f"Source: {results[0].source}")
        print(f"Content preview: {results[0].chunk.content[:200]}...")

asyncio.run(check_storage())