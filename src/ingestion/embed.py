import os
import logging
from typing import List, Dict
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import vertexai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def embed_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Generates embeddings for each chunk using Vertex AI's text-embedding-004 model.
    """
    if not chunks:
        return []

    project_id = os.getenv("GCP_PROJECT_ID", "legalaidassistant")
    location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    
    try:
        vertexai.init(project=project_id, location=location)
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
        logger.warning(f"Could not initialize Vertex AI: {e}. Returning mock embeddings for local testing.")
        # Mock embeddings for local test if credentials aren't set
        for chunk in chunks:
            chunk["embedding"] = [0.0] * 768  # text-embedding-004 output dimension
        return chunks

    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    
    # Process in batches to avoid payload limits (e.g., 250 max per request)
    batch_size = 100
    embedded_chunks = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [chunk["text"] for chunk in batch]
        
        try:
            inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
            embeddings = model.get_embeddings(inputs)
            
            for chunk, embedding in zip(batch, embeddings):
                chunk["embedding"] = embedding.values
                embedded_chunks.append(chunk)
                
            logger.info(f"Embedded batch {i // batch_size + 1}")
        except Exception as e:
            logger.error(f"Failed to embed batch {i // batch_size + 1}: {e}")
            # If a batch fails, we skip it or mock it. For testing, we mock.
            for chunk in batch:
                chunk["embedding"] = [0.0] * 768
                embedded_chunks.append(chunk)
                
    logger.info("Embedding generation complete.")
    return embedded_chunks

if __name__ == "__main__":
    sample_chunks = [{"text": "Hello world", "metadata": {}}]
    res = embed_chunks(sample_chunks)
    print(f"Sample embedding length: {len(res[0]['embedding'])}")
