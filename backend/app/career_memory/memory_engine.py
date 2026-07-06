from sqlalchemy.orm import Session
from app.db.models.user import User
from app.career_memory.memory_store import MemoryStore
from app.vector_db.chroma_client import get_career_memory_collection, get_company_memory_collection, get_application_memory_collection
from app.services.ai_service import ai_service
from app.core.logger import system_logger
import uuid

class MemoryEngine:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.career_collection = get_career_memory_collection()

    def record_event(self, event_type: str, description: str, metadata: dict = None):
        """
        Records an event in the SQL ledger and embeds it into ChromaDB for semantic search.
        """
        doc_id = f"mem_{uuid.uuid4()}"
        
        # Save to SQL
        MemoryStore.log_event(self.db, self.user.id, event_type, description, metadata, doc_id)
        
        # Embed in ChromaDB
        try:
            self.career_collection.add(
                documents=[description],
                metadatas=[{
                    "user_id": self.user.id,
                    "event_type": event_type,
                    "metadata": str(metadata)
                }],
                ids=[doc_id]
            )
            system_logger.info(f"Memory recorded and embedded: {description}")
        except Exception as e:
            system_logger.error(f"Failed to embed memory event: {e}")

    def search_memory(self, query: str, limit: int = 5):
        """
        Performs semantic search over the user's career memory.
        """
        try:
            results = self.career_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"user_id": self.user.id}
            )
            
            structured_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for idx, doc in enumerate(results['documents'][0]):
                    structured_results.append({
                        "id": results['ids'][0][idx],
                        "description": doc,
                        "metadata": results['metadatas'][0][idx],
                        "similarity": results['distances'][0][idx] if 'distances' in results else 0
                    })
            return structured_results
        except Exception as e:
            system_logger.error(f"Semantic search failed: {e}")
            return []
