import logging
from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse

from src.retrieval.retriever import LegalRetriever
from src.generation.generator import LegalGenerator
from src.api.session import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter()
session_manager = SessionManager()
retriever = LegalRetriever()
generator = LegalGenerator()

@router.post("/twilio/webhook")
async def twilio_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Receives incoming WhatsApp messages from Twilio.
    Returns TwiML response.
    """
    logger.info(f"Received WhatsApp message from {From}: {Body}")
    
    # Use the sender's phone number as the session ID
    session_id = f"wa_{From}"
    query = Body.strip()
    
    try:
        # 1. Retrieve Context
        docs = retriever.retrieve(query, top_k=3)
        
        # 2. Generate Answer
        response_text = generator.generate(query, docs)
        
        # 3. Store in Session
        session_manager.save_interaction(
            session_id=session_id,
            query=query,
            response=response_text,
            metadata={"channel": "whatsapp", "retrieved_docs": len(docs)}
        )
    except Exception as e:
        logger.error(f"Error processing WhatsApp query: {e}")
        response_text = "Sorry, I am facing technical difficulties at the moment. Please try again later."
    
    # 4. Create TwiML Response
    twiml_response = MessagingResponse()
    msg = twiml_response.message()
    msg.body(response_text)
    
    return PlainTextResponse(content=str(twiml_response), media_type="application/xml")
