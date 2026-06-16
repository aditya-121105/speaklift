from fastapi import FastAPI

app = FastAPI(
    title="SpeakLift API",
    description="AI-Powered Interview & Viva Confidence Platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SpeakLift API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }