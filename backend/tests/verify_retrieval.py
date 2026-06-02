import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.vector_db.chroma_client import get_job_collection, get_embeddings
import uuid

def seed_and_verify():
    collection = get_job_collection()
    
    # 5 Sample JDs
    jds = [
        {"title": "Backend Engineer", "company": "TechCorp", "text": "Backend Engineer needed at TechCorp. Must know Python, FastAPI, and PostgreSQL. Remote."},
        {"title": "Frontend Developer", "company": "WebInc", "text": "Frontend Developer at WebInc. React, TypeScript, TailwindCSS required. Onsite in New York."},
        {"title": "AI Engineer", "company": "NextGen AI", "text": "AI Engineer required. Deep learning, NLP, OpenAI APIs, Vector databases. Remote."},
        {"title": "Data Scientist", "company": "DataWorks", "text": "Data Scientist with experience in Pandas, Scikit-learn, and SQL. Hybrid role in San Francisco."},
        {"title": "DevOps Engineer", "company": "CloudSys", "text": "DevOps Engineer. Kubernetes, Docker, AWS, CI/CD pipelines. Remote."}
    ]
    
    print("Seeding 5 sample JDs into ChromaDB...")
    for jd in jds:
        doc_id = f"test_job_{uuid.uuid4()}"
        collection.add(
            documents=[jd["text"]],
            metadatas=[{"title": jd["title"], "company": jd["company"]}],
            ids=[doc_id]
        )
        
    print("Verifying Retrieval...")
    query = "Looking for a Python backend role with FastAPI"
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    print(f"Query: '{query}'")
    if results and results['documents'] and results['documents'][0]:
        best_match = results['documents'][0][0]
        metadata = results['metadatas'][0][0]
        print(f"Top Match: {metadata['title']} at {metadata['company']}")
        assert "Backend Engineer" in metadata['title'], "Retrieval failed to find the most relevant JD!"
        print("Retrieval Verification: SUCCESS!")
    else:
        print("Retrieval Verification: FAILED (No results returned).")

if __name__ == "__main__":
    seed_and_verify()
