# Real-Time Legal Aid Assistant ⚖️

An AI-powered real-time legal aid assistant built using Retrieval-Augmented Generation (RAG). This application helps users navigate complex legal documents and obtain instantaneous legal guidance through multiple channels, including a web dashboard and WhatsApp.

## Features ✨

*   **RAG-Powered Legal Answers**: Uses advanced language models (Google Vertex AI) and vector search to ground answers in provided legal documents (e.g., Code on Wages, Consumer Protection Act, Tenant Rights Act).
*   **Multi-Channel Interfaces**: 
    *   **Streamlit Dashboard**: A user-friendly web interface for querying legal information.
    *   **WhatsApp Integration**: Accessible via Twilio for on-the-go legal assistance.
*   **Robust Ingestion Pipeline**: Extracts, chunks, and embeds text from legal PDFs and documents using PyMuPDF and LangChain.
*   **Evaluation & Observability**: Integrated with Langfuse and Ragas to continuously monitor and evaluate the quality of the generated answers.
*   **FastAPI Backend**: A high-performance, asynchronous REST API for powering the user interfaces.

## Architecture 🏗️

The project is structured into distinct modules:
*   `src/api`: FastAPI endpoints, authentication, and middleware.
*   `src/ingestion`: Data pipeline for downloading, parsing, chunking, and embedding legal documents.
*   `src/retrieval`: Logic for retrieving relevant context from the vector database.
*   `src/generation`: LLM components for synthesizing answers based on retrieved context.
*   `src/channels`: Integrations with external platforms like WhatsApp.
*   `src/evaluation`: Dataset generation and evaluation scripts using Ragas.
*   `dashboard`: Streamlit application for the frontend.

## Tech Stack 🛠️

*   **Backend**: Python, FastAPI, Uvicorn
*   **Frontend**: Streamlit
*   **AI/LLM**: Google Vertex AI, LangChain
*   **Data Storage**: Google Cloud Storage, Google Cloud Firestore
*   **Evaluation & Tracing**: Langfuse, Ragas
*   **Integrations**: Twilio (WhatsApp API)
*   **Package Management**: [uv](https://github.com/astral-sh/uv)

## Getting Started 🚀

### Prerequisites

*   Python >= 3.12
*   [uv](https://docs.astral.sh/uv/) package manager
*   Google Cloud Platform (GCP) Account with Vertex AI enabled
*   Twilio Account (for WhatsApp integration)
*   Langfuse Account (for observability)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yashbhargav10/Real-Time-Legal-aid.git
    cd Real-Time-Legal-aid
    ```

2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    ```

3.  **Environment Variables:**
    Copy `.env.example` to `.env` and fill in your credentials:
    ```bash
    cp .env.example .env
    ```
    *Required keys typically include GCP project details, Twilio tokens, and Langfuse API keys.*

### Running the Application

**1. Run the FastAPI Backend:**
```bash
uv run uvicorn src.api.main:app --reload
```

**2. Run the Streamlit Dashboard:**
```bash
uv run streamlit run dashboard/app.py
```

## Deployment ☁️

The project includes Dockerfiles for containerization and deployment:
*   `Dockerfile.api`: For deploying the FastAPI backend.
*   `Dockerfile.streamlit`: For deploying the Streamlit dashboard.
*   `cloudbuild.yaml`: CI/CD configuration for Google Cloud Build.
