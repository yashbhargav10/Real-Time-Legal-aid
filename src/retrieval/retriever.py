import os
import logging
from typing import List, Dict, Any
from google.cloud import aiplatform
from google.cloud import firestore
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import vertexai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalRetriever:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "legalaidassistant")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.index_id = os.getenv("VERTEX_VECTOR_SEARCH_INDEX_ID")
        self.endpoint_id = os.getenv("VERTEX_VECTOR_SEARCH_ENDPOINT_ID")
        
        # We will attempt to initialize Vertex and Firestore lazily or in init
        self._init_gcp_clients()

    def _init_gcp_clients(self):
        self.mock_mode = False
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.embed_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            
            if self.index_id and self.endpoint_id and self.index_id != "your-index-id":
                self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=self.endpoint_id)
            else:
                self.mock_mode = True
                
            self.db = firestore.Client(project=self.project_id)
        except Exception as e:
            logger.warning(f"GCP Client initialization failed: {e}. Running in MOCK mode.")
            self.mock_mode = True

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Retrieving context for query: '{query}'")
        
        if self.mock_mode and not hasattr(self, 'index_endpoint'):
            # Fallback to local exact KNN if Vector Search is not configured but Vertex is!
            logger.info("Vector Search not configured. Falling back to local exact KNN over embeddings.jsonl.")
            import json
            import numpy as np
            local_path = "data/processed/embeddings.jsonl"
            
            # Embed Query using REAL Vertex AI
            inputs = [TextEmbeddingInput(query, "RETRIEVAL_QUERY")]
            query_emb = np.array(self.embed_model.get_embeddings(inputs)[0].values)
            
            results = []
            if os.path.exists(local_path):
                with open(local_path, 'r') as f:
                    for line in f:
                        data = json.loads(line)
                        doc_emb = np.array(data["embedding"])
                        score = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
                        results.append({
                            "text": data["text"],
                            "score": float(score),
                            "metadata": data["metadata"]
                        })
                # Sort by score
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:top_k]
            else:
                logger.warning("Local embeddings file missing! Please run ingestion pipeline first.")
                return []

        try:
            # 1. Embed Query
            inputs = [TextEmbeddingInput(query, "RETRIEVAL_QUERY")]
            query_embedding = self.embed_model.get_embeddings(inputs)[0].values

            # 2. Query Vector Search
            response = self.index_endpoint.find_neighbors(
                deployed_index_id="legal_index_deployment", # Placeholder deployed index id
                queries=[query_embedding],
                num_neighbors=top_k
            )

            results = []
            if response and len(response) > 0:
                neighbors = response[0]
                for neighbor in neighbors:
                    # Neighbor has id and distance. Distance is usually 1 - cosine_similarity if configured that way
                    score = max(0.0, 1.0 - neighbor.distance) 
                    
                    # 3. Fetch from Firestore
                    doc_ref = self.db.collection("legal_chunks").document(neighbor.id)
                    doc = doc_ref.get()
                    if doc.exists:
                        data = doc.to_dict()
                        results.append({
                            "text": data.get("text", ""),
                            "score": score,
                            "metadata": data.get("metadata", {})
                        })
            return results
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []

if __name__ == "__main__":
    retriever = LegalRetriever()
    results = retriever.retrieve("What is the minimum wage?")
    print(results)
