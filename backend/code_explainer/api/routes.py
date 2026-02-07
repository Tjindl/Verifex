from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ..core.analyzer import CodeAnalyzer
from ..llm.client import LLMClient
from ..core.verifier import VerificationEngine
from ..core.models import VerificationResult

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str

class AnalyzeResponse(BaseModel):
    metadata: Dict[str, Any]
    explanation: Dict[str, Any]
    verification: VerificationResult

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
        
        # 3. Dynamic Verification
        # Extract invariants from LLM output. We assume they are strings valid in python.
        invariants = explanation.get("invariants", [])
        # Sanitize: ensure they are strings
        invariants = [str(inv) for inv in invariants if isinstance(inv, (str, int, float))]

        # Extract restrictions/preconditions
        preconditions = explanation.get("assumptions", [])
        # Sanitize: ensure they are strings and look like expressions (simple heuristic)
        preconditions = [str(pre) for pre in preconditions if isinstance(pre, (str, int, float))]

        # Extract argument types/strategies
        arg_types = explanation.get("argument_types", {})

        verifier = VerificationEngine()
        verification_result = verifier.verify(
             code=request.code,
             function_name=metadata.function_name,
             invariants=invariants,
             preconditions=preconditions,
             arg_types=arg_types
        )
        
        return AnalyzeResponse(
            metadata=metadata.model_dump(exclude={'raw_code'}), # raw_code is big and in request
            explanation=explanation,
            verification=verification_result
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
