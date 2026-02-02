from fastapi import FastAPI
from dotenv import load_dotenv
from code_explainer.api.routes import router

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="AI Code Explainer",
    description="Formal verification-style explanations for code.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("code_explainer.main:app", host="0.0.0.0", port=8000, reload=True)
