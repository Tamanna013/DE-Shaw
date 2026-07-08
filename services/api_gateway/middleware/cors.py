from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os

# In a real environment, this comes from `shared/config` 
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

def setup_cors(app: FastAPI):
    # Enforce explicit origins. NEVER allow '*' in production.
    if "*" in ALLOWED_ORIGINS and os.environ.get("ENV") == "prod":
        raise ValueError("Wildcard CORS is strictly prohibited in production")
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
