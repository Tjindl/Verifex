from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ..core.analyzer import CodeAnalyzer
from ..llm.client import LLMClient

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str

class AnalyzeResponse(BaseModel):
    metadata: Dict[str, Any]
    explanation: Dict[str, Any]

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    try:
        # 1. Static Analysis
        analyzer = CodeAnalyzer()
        metadata = analyzer.analyze(request.code)
        
        # 2. LLM Reasoning
        llm_client = LLMClient()
        explanation = llm_client.explain(metadata)
        
        return AnalyzeResponse(
            metadata=metadata.model_dump(exclude={'raw_code'}), # raw_code is big and in request
            explanation=explanation
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
