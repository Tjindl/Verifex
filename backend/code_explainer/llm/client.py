import os
import json
import typing
from typing import Dict, Any, Optional
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from ..core.models import CodeMetadata

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key and genai:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash' # Using latest performant model
        else:
            self.client = None
            if not genai:
                 print("Warning: google-genai library not found. Mocking response.")
            else:
                 print("Warning: No GEMINI_API_KEY found. LLM responses will be mocked.")

    def explain(self, metadata: CodeMetadata) -> Dict[str, Any]:
        if not self.client:
            return self._mock_response(metadata)

        # Prepare context
        loops_str = json.dumps([l.model_dump(exclude={'source'}) for l in metadata.loops], indent=2)
        recursions_str = json.dumps([r.model_dump(exclude={'source'}) for r in metadata.recursions], indent=2)
        control_flow_summary = f"{len(metadata.loops)} loops, {len(metadata.recursions)} recursive calls"

        prompt = USER_PROMPT_TEMPLATE.format(
            code=metadata.raw_code,
            function_name=metadata.function_name,
            args=json.dumps(metadata.args),
            control_flow_summary=control_flow_summary,
            loops=loops_str,
            recursions=recursions_str
        )
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        try:
            # Generate valid JSON using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )
            
            content = response.text
            return json.loads(content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._mock_response(metadata, error=str(e))

    def _mock_response(self, metadata: CodeMetadata, error: str = "") -> Dict[str, Any]:
        """Fallback mock response if no API key or error."""
        return {
            "goal": f"Execute function {metadata.function_name}",
            "assumptions": ["Inputs are valid according to python typing (if any)"],
            "invariants": [l.candidate_invariant for l in metadata.loops if l.candidate_invariant] or ["None detected"],
            "correctness_argument": "Mock explanation: Logic follows standard control flow.",
            "termination_argument": "Loops terminate because counters assume finite range.",
            "edge_cases": ["None explicitly handled in mock"],
            "complexity": {"time": "O(N)", "space": "O(1)"},
            "note": "This is a MOCK response. structure. Set GEMINI_API_KEY for real analysis.",
            "error_info": error
        }
