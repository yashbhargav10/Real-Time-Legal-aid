import os
import logging
from typing import List, Dict
from google.cloud import firestore
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "legalaidassistant")
        self.mock_mode = False
        
        try:
            self.db = firestore.Client(project=self.project_id)
        except Exception as e:
            logger.warning(f"Firestore Client initialization failed: {e}. SessionManager running in MOCK mode.")
            self.mock_mode = True
            self.mock_db = {}

    def save_interaction(self, session_id: str, query: str, response: str, metadata: Dict = None):
        """Saves a single Q&A interaction to the user's session history."""
        interaction = {
            "query": query,
            "response": response,
            "timestamp": datetime.now(timezone.utc),
            "metadata": metadata or {}
        }
        
        if self.mock_mode:
            if session_id not in self.mock_db:
                self.mock_db[session_id] = []
            self.mock_db[session_id].append(interaction)
            logger.info(f"Mock: Saved interaction to session {session_id}")
            return

        try:
            doc_ref = self.db.collection("sessions").document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.update({"history": firestore.ArrayUnion([interaction])})
            else:
                doc_ref.set({
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc),
                    "history": [interaction]
                })
        except Exception as e:
            logger.error(f"Failed to save session interaction to Firestore: {e}")

    def get_history(self, session_id: str) -> List[Dict]:
        """Retrieves the interaction history for a given session."""
        if self.mock_mode:
            return self.mock_db.get(session_id, [])
            
        try:
            doc = self.db.collection("sessions").document(session_id).get()
            if doc.exists:
                return doc.to_dict().get("history", [])
        except Exception as e:
            logger.error(f"Failed to retrieve session history from Firestore: {e}")
        return []
