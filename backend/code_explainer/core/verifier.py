
import subprocess
import sys
import tempfile
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from .models import VerificationResult

class VerificationEngine:
    def __init__(self):
        pass

    def verify(self, code: str, function_name: str, invariants: List[str], preconditions: List[str] = [], arg_types: Dict[str, Any] = {}, num_tests: int = 100) -> VerificationResult:
        """
        Generates a temporary test file using Hypothesis and runs it.
        """
        if not invariants:
             return VerificationResult(verified=True, output="No invariants to verify.", num_tests=0)

        test_script = self._generate_test_script(code, function_name, invariants, preconditions, arg_types, num_tests)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_path = f.name

        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=30  # Safety timeout
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return VerificationResult(verified=True, output=output.strip(), num_tests=num_tests)
            else:
                # Hypothesis usually prints "Falsifying example: ..."
                counter_example = self._extract_counter_example(output)
                failure_reason = self._extract_failure_reason(output)
                return VerificationResult(
                    verified=False, 
                    output=output.strip(), 
                    counter_example=counter_example,
                    failure_reason=failure_reason,
                    num_tests=num_tests
                )

        except subprocess.TimeoutExpired:
             return VerificationResult(verified=False, output="Verification timed out.", counter_example=None)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _generate_test_script(self, code: str, function_name: str, invariants: List[str], preconditions: List[str], arg_types: Dict[str, Any], num_tests: int) -> str:
        # Dynamic Strategy Construction
        # arg_types example: {"n": {"type": "int", "strategy": "integers(min_value=-1000, max_value=1000)"}}
            
        # Simplified Script Template
        # Dynamic Strategy Construction
        # arg_types example: {"n": {"type": "int", "strategy": "integers(min_value=-1000, max_value=1000)"}}
        
        strategies_str = []
        args_list = []
        
        for arg_name, details in arg_types.items():
            strategy = details.get("strategy", "integers()") # Default fallback
            # Sanitize strategy string to prevent arbitrary code execution if possible, 
            # but here we trust the prompt's structured output for MVP.
            # We prefix with 'st.'
            if strategy.startswith("st."):
                strategy_code = strategy
            else:
                strategy_code = f"st.{strategy}"
            
            strategies_str.append(f"{arg_name}={strategy_code}")
            args_list.append(arg_name)
            
        given_args = ", ".join(strategies_str)
        func_args = ", ".join(args_list)

        # Fallback if no args provided (should not happen for valid functions)
        if not given_args:
             given_args = "n=st.integers(min_value=-1000, max_value=1000)"
             func_args = "n"

        script = f"""
import sys
from hypothesis import given, settings, assume, strategies as st

# User Code
{code}

# Test
@settings(max_examples={num_tests}, deadline=None)
@given({given_args})
def test_property({func_args}):
    # Preconditions
    # Filter inputs using assume()
    
    {' '.join([f'assume({pre})' for pre in preconditions])}

    # Execute
    try:
        result = {function_name}({func_args})
    except RecursionError:
        return # Recursion limit is not a logic failure for invariants per se
    except Exception:
        return # Ignore other runtime errors for now, focus on invariants

    # Check Invariants
    # The LLM invariants use argument names and 'result' (output).
    
    {' '.join([f'assert {inv}, "Invariant violation: {inv}"' for inv in invariants])}

if __name__ == "__main__":
    try:
        test_property()
        print("Verified!")
    except Exception as e:
        print(e)
        sys.exit(1)
"""
        return script

    def _extract_counter_example(self, output: str) -> Optional[str]:
        if "Falsifying example" in output:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                 if "Falsifying example" in line:
                     return line + (lines[i+1] if i+1 < len(lines) else "")
        return None

    def _extract_failure_reason(self, output: str) -> Optional[str]:
        # Look for AssertionError or other exceptions
        import re
        # Hypothesis prints the exception at the end usually
        # Pattern: "AssertionError: Invariant violation: ..."
        match = re.search(r"AssertionError: (.*)", output)
        if match:
            return match.group(1).strip()
        
        # Fallback to RecursionError or others
        if "RecursionError" in output:
             return "RecursionError: Maximum recursion depth exceeded"
             
        return "Unknown failure (check formatting)"
