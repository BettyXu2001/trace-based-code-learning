from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api

app = FastAPI(
    title="Trace-based Code Learning API",
    description="Execution-aware code explanation and learning system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Trace-based Code Learning API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
