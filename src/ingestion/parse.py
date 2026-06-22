import os
import fitz  # PyMuPDF
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_pdfs(input_dir: str = "data/raw") -> List[Dict]:
    """
    Parses all PDFs in the input directory and returns a list of dictionaries
    containing page-level text and metadata.
    """
    documents = []
    
    if not os.path.exists(input_dir):
        logger.warning(f"Input directory {input_dir} does not exist.")
        return documents

    for filename in os.listdir(input_dir):
        if not (filename.endswith(".pdf") or filename.endswith(".txt")):
            continue
            
        file_path = os.path.join(input_dir, filename)
        logger.info(f"Parsing {filename}...")
        
        try:
            if filename.endswith(".pdf"):
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    # Basic cleanup
                    text = text.replace("\n", " ").strip()
                    if not text:
                        continue
                        
                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": filename,
                            "page": page_num + 1
                        }
                    })
                doc.close()
            elif filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    documents.append({
                        "text": text.replace("\n", " ").strip(),
                        "metadata": {
                            "source": filename,
                            "page": 1
                        }
                    })
        except Exception as e:
            logger.error(f"Error parsing {filename}: {e}")
            
    logger.info(f"Extracted {len(documents)} pages of text.")
    return documents

if __name__ == "__main__":
    docs = parse_pdfs()
    if docs:
        print(f"Sample from first doc: {docs[0]['text'][:100]}...")
