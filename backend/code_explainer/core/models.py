from typing import List, Optional, Any
from pydantic import BaseModel, Field

class VariableRole(BaseModel):
    name: str
    role: str = Field(..., description="e.g., 'iterator', 'accumulator', 'flag', 'constant'")
    extracted_source: Optional[str] = None

class ControlFlowElement(BaseModel):
    type: str = Field(..., description="e.g., 'for_loop', 'while_loop', 'recursion', 'if_condition'")
    source: str
    line_start: int
    line_end: int
    condition: Optional[str] = None

class LoopInfo(ControlFlowElement):
    loop_variable: Optional[str] = None
    iterable: Optional[str] = None
    candidate_invariant: Optional[str] = None

class RecursionInfo(ControlFlowElement):
    base_case_condition: Optional[str] = None
    recursive_step: Optional[str] = None

class CodeMetadata(BaseModel):
    function_name: str
    args: List[str]
    control_flow: List[ControlFlowElement] = []
    loops: List[LoopInfo] = []
    recursions: List[RecursionInfo] = []
    variables: List[VariableRole] = []
    raw_code: str

class VerificationResult(BaseModel):
    verified: bool
    output: str
    counter_example: Optional[str] = None
    failure_reason: Optional[str] = None
    num_tests: int = 0

