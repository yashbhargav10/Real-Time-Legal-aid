import os
import json
import uuid
import logging
from typing import List, Dict
from google.cloud import firestore
from google.cloud import aiplatform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_to_stores(chunks: List[Dict], output_dir: str = "data/processed"):
    """
    Uploads chunks to Vertex AI Vector Search and their metadata to Firestore.
    Also saves a local backup in data/processed/.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    project_id = os.getenv("GCP_PROJECT_ID", "legalaidassistant")
    location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    index_id = os.getenv("VERTEX_VECTOR_SEARCH_INDEX_ID")
    
    # Save locally to processed directory
    local_path = os.path.join(output_dir, "embeddings.jsonl")
    with open(local_path, "w") as f:
        for chunk in chunks:
            # We add an ID to each chunk if not present
            if "id" not in chunk:
                chunk["id"] = str(uuid.uuid4())
            f.write(json.dumps(chunk) + "\n")
    logger.info(f"Saved {len(chunks)} embedded chunks locally to {local_path}")

    # Firestore Upload
    try:
        db = firestore.Client(project=project_id)
        batch = db.batch()
        collection_ref = db.collection("legal_chunks")
        
        for idx, chunk in enumerate(chunks):
            doc_ref = collection_ref.document(chunk["id"])
            batch.set(doc_ref, {
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            })
            
            # Commit every 500 records
            if (idx + 1) % 500 == 0:
                batch.commit()
                batch = db.batch()
                logger.info(f"Uploaded {idx + 1} metadata records to Firestore.")
        
        batch.commit()
        logger.info("Finished uploading metadata to Firestore.")
    except Exception as e:
        logger.warning(f"Could not upload to Firestore: {e}. Ensure credentials are valid.")

    # Vector Search Upload
    if not index_id or index_id == "your-index-id":
        logger.warning("VERTEX_VECTOR_SEARCH_INDEX_ID is not set properly. Skipping upload to Vector Search.")
        return

    try:
        aiplatform.init(project=project_id, location=location)
        my_index = aiplatform.MatchingEngineIndex(index_name=index_id)
        
        datapoints = []
        for chunk in chunks:
            datapoints.append(
                aiplatform.matching_engine.matching_engine_index.IndexDatapoint(
                    datapoint_id=chunk["id"],
                    feature_vector=chunk["embedding"],
                    restricts=[
                        {"namespace": "source", "allow_list": [chunk["metadata"].get("source", "unknown")]}
                    ]
                )
            )
            
        my_index.upsert_datapoints(datapoints=datapoints)
        logger.info("Successfully uploaded embeddings to Vertex AI Vector Search.")
    except Exception as e:
        logger.warning(f"Could not upload to Vector Search: {e}. Note: Index might need to be created first.")

if __name__ == "__main__":
    sample_data = [{"text": "Hello", "embedding": [0.1]*768, "metadata": {"source": "test"}}]
    upload_to_stores(sample_data)
