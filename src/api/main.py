from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables for local dev BEFORE local imports
load_dotenv()

from src.api.middleware import RequestLoggingMiddleware
from src.api.routes import router

app = FastAPI(
    title="Real-Time Legal Aid Assistant API",
    description="A RAG-based API answering Indian legal queries.",
    version="1.0.0"
)

# Add Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Include Routes
app.include_router(router)

from src.channels.whatsapp import router as whatsapp_router
app.include_router(whatsapp_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8080, reload=True)
