import logging
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_documents(documents: List[Dict], chunk_size: int = 800, chunk_overlap: int = 100) -> List[Dict]:
    """
    Chunks parsed documents into smaller segments using LangChain's RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_data = []
    
    logger.info(f"Chunking {len(documents)} pages with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        
        chunks = text_splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            # Extend metadata to include chunk index
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            
            chunked_data.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
            
    logger.info(f"Generated {len(chunked_data)} total chunks.")
    return chunked_data

if __name__ == "__main__":
    sample_docs = [{"text": "Sample text. " * 100, "metadata": {"source": "test.pdf", "page": 1}}]
    chunks = chunk_documents(sample_docs)
    print(f"Created {len(chunks)} chunks from sample.")
