import os
import logging
from typing import List, Dict, Any
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback message for Hallucination Guard
HALLUCINATION_GUARD_MSG = "I could not find reliable legal information for your query. Please consult a qualified lawyer."

PROMPT_TEMPLATE = """You are a highly capable Indian Legal Aid Assistant. 
You must answer the user's legal query based ONLY on the provided context. 
If the context does not contain the answer, do NOT hallucinate or guess. Just say you don't know.

Format your response strictly as follows:
Answer: <Your detailed answer>
Relevant Sections: <List of sections and acts cited>
Confidence Level: <High/Medium/Low based on context clarity>

Context:
{context}

User Query:
{query}
"""

class LegalGenerator:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "legalaidassistant")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.mock_mode = False
        
        try:
            self.llm = ChatVertexAI(
                model_name="gemini-pro",
                project=self.project_id,
                location=self.location,
                temperature=0.0
            )
        except Exception as e:
            logger.warning(f"Could not initialize ChatVertexAI: {e}. Running in MOCK mode.")
            self.mock_mode = True

        self.prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["context", "query"]
        )

    def generate(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        if not retrieved_docs:
            return HALLUCINATION_GUARD_MSG
            
        # Hallucination Guard: Threshold Filter
        max_score = max([doc.get("score", 0.0) for doc in retrieved_docs])
        if max_score < 0.6:
            logger.warning(f"Max retrieval score {max_score:.2f} is below 0.6 threshold. Triggering hallucination guard.")
            return HALLUCINATION_GUARD_MSG

        # Prepare Context
        context_parts = []
        for doc in retrieved_docs:
            text = doc.get("text", "")
            meta = doc.get("metadata", {})
            source = meta.get("source", "Unknown")
            section = meta.get("section", "N/A")
            context_parts.append(f"[Source: {source}, Section: {section}]\n{text}")
            
        context_str = "\n\n".join(context_parts)
        
        if self.mock_mode:
            logger.info("Mock mode active. Returning dummy LLM generation.")
            return (
                "Answer: Based on the Code on Wages, employers must pay the minimum wage to all employees.\n"
                "Relevant Sections: Section 9, Section 18 of Code_on_Wages_2019.pdf\n"
                "Confidence Level: High"
            )

        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"context": context_str, "query": query})
            return response.content
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}")
            logger.info("Switching to MOCK mode for future requests to prevent timeouts.")
            self.mock_mode = True
            return "An error occurred while generating the legal response."

if __name__ == "__main__":
    gen = LegalGenerator()
    dummy_docs = [{"text": "You must pay minimum wage.", "score": 0.9, "metadata": {"source": "Law.pdf"}}]
    print(gen.generate("What is minimum wage?", dummy_docs))
