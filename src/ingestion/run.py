import logging
from dotenv import load_dotenv
from src.ingestion.download import download_pdfs
from src.ingestion.parse import parse_pdfs
from src.ingestion.chunk import chunk_documents
from src.ingestion.embed import embed_chunks
from src.ingestion.upload import upload_to_stores

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Data Ingestion Pipeline...")
    
    # 1. Load environment variables
    load_dotenv()
    
    # 2. Download raw PDFs
    logger.info("Step 1/5: Downloading PDFs")
    download_pdfs(output_dir="data/raw")
    
    # 3. Parse PDFs into text
    logger.info("Step 2/5: Parsing PDFs")
    documents = parse_pdfs(input_dir="data/raw")
    if not documents:
        logger.error("No documents parsed. Exiting pipeline.")
        return
        
    # 4. Chunk text using LangChain
    logger.info("Step 3/5: Chunking Text")
    chunks = chunk_documents(documents, chunk_size=800, chunk_overlap=100)
    
    # 5. Embed chunks using Vertex AI
    logger.info("Step 4/5: Generating Embeddings")
    embedded_chunks = embed_chunks(chunks)
    
    # 6. Upload to Vector Search & Firestore
    logger.info("Step 5/5: Uploading to Datastores")
    upload_to_stores(embedded_chunks, output_dir="data/processed")
    
    logger.info("Data Ingestion Pipeline completed successfully!")

if __name__ == "__main__":
    main()
