from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from src.api.auth import get_api_key
from src.api.session import SessionManager
from src.retrieval.retriever import LegalRetriever
from src.generation.generator import LegalGenerator

router = APIRouter()

# Global instances (in a larger app these would be injected)
session_manager = SessionManager()
retriever = LegalRetriever()
generator = LegalGenerator()

class QueryRequest(BaseModel):
    session_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str

class FeedbackRequest(BaseModel):
    session_id: str
    feedback: str # e.g. "positive", "negative"
    comments: Optional[str] = None

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "legal-aid-ai-api"}

@router.post("/query", response_model=QueryResponse, dependencies=[Depends(get_api_key)])
def handle_query(req: QueryRequest):
    # 1. Retrieve Context
    docs = retriever.retrieve(req.query, top_k=3)
    
    # 2. Generate Answer
    response_text = generator.generate(req.query, docs)
    
    # 3. Store in Session
    session_manager.save_interaction(
        session_id=req.session_id,
        query=req.query,
        response=response_text,
        metadata={"retrieved_docs": len(docs)}
    )
    
    return QueryResponse(answer=response_text)

@router.post("/feedback", dependencies=[Depends(get_api_key)])
def handle_feedback(req: FeedbackRequest):
    # Log feedback into Firestore session or separate collection
    session_manager.save_interaction(
        session_id=req.session_id,
        query="[FEEDBACK_SUBMITTED]",
        response=req.feedback,
        metadata={"comments": req.comments}
    )
    return {"status": "feedback recorded"}
