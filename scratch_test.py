import sys
import logging
from src.retrieval.retriever import LegalRetriever

logging.basicConfig(level=logging.INFO)

def main():
    retriever = LegalRetriever()
    query = "tenant security deposit rights"
    print(f"\n--- Running retrieval for: '{query}' ---")
    results = retriever.retrieve(query, top_k=3)
    
    print(f"\nFound {len(results)} chunks.")
    for i, res in enumerate(results):
        print(f"\n[Chunk {i+1}] Score: {res['score']:.4f}")
        print(f"Source: {res['metadata'].get('source')}")
        print(f"Text snippet: {res['text'][:150]}...")

if __name__ == '__main__':
    main()
