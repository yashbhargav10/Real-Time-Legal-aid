import logging
from src.retrieval.retriever import LegalRetriever
from src.generation.generator import LegalGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_query(query: str):
    logger.info(f"--- Querying RAG Pipeline ---")
    logger.info(f"User Query: {query}")
    
    # 1. Retrieve
    retriever = LegalRetriever()
    retrieved_docs = retriever.retrieve(query, top_k=3)
    
    logger.info(f"Retrieved {len(retrieved_docs)} documents.")
    for i, doc in enumerate(retrieved_docs):
        logger.info(f"Doc {i+1} Score: {doc.get('score', 0):.2f} | Source: {doc.get('metadata', {}).get('source')}")
    
    # 2. Generate
    generator = LegalGenerator()
    response = generator.generate(query, retrieved_docs)
    
    logger.info("\n--- RAG Response ---")
    print(response)
    logger.info("--------------------")

if __name__ == "__main__":
    # Test a query that should pass the threshold in mock mode (Mock mode returns score 0.85)
    run_query("What are the rules regarding minimum wage and deductions?")
    
    # Optional: We can manually test the hallucination guard by injecting bad scores
    print("\n\nTesting Hallucination Guard (< 0.6 threshold):")
    generator = LegalGenerator()
    bad_docs = [{"text": "Irrelevant text.", "score": 0.4, "metadata": {"source": "unknown.pdf"}}]
    fallback_response = generator.generate("How do I fix my plumbing?", bad_docs)
    print(fallback_response)
