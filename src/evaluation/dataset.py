import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_dataset(output_path: str = "data/evaluation_dataset.json"):
    """
    Generates a mock ground-truth evaluation dataset of 50 QA pairs
    across Labour, Tenant, and Consumer Rights domains.
    """
    dataset = []
    
    domains = ["Labour Rights", "Tenant Rights", "Consumer Rights"]
    
    for i in range(1, 51):
        domain = domains[i % 3]
        
        if domain == "Labour Rights":
            question = f"What are the regulations regarding minimum wage for category {i} workers?"
            ground_truth = f"According to Section {i} of the Code on Wages, category {i} workers must be paid the stipulated minimum wage."
        elif domain == "Tenant Rights":
            question = f"Under what circumstances can a landlord evict a tenant for reason {i}?"
            ground_truth = f"Under the Rent Control Act, eviction for reason {i} requires a 30-day notice and specific grounds of breach."
        else:
            question = f"What is the remedy for a defective product of type {i}?"
            ground_truth = f"The Consumer Protection Act Section {i} states the consumer is entitled to a full refund or replacement."
            
        dataset.append({
            "question": question,
            "ground_truth": ground_truth,
            "domain": domain
        })
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=4)
        
    logger.info(f"Successfully generated 50 ground-truth QA pairs at {output_path}")

if __name__ == "__main__":
    generate_dataset()
