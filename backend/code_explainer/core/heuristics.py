from .models import CodeMetadata, LoopInfo, RecursionInfo

class HeuristicsEngine:
    def apply(self, metadata: CodeMetadata):
        self._detect_loop_invariants(metadata)
        self._analyze_recursion(metadata)

    def _detect_loop_invariants(self, metadata: CodeMetadata):
        for loop in metadata.loops:
            if loop.type == "for_loop" and loop.loop_variable and loop.iterable:
                # Basic Range Heuristic
                # valid for: for i in range(n)
                # heuristic: 0 <= i < n (during), i = n (after)? 
                range_call = "range" in loop.iterable
                if range_call:
                     # Attempt to parse range args from string (very naive)
                     # ideally we'd look at AST for "range(n)"
                     loop.candidate_invariant = f"0 <= {loop.loop_variable} < len({loop.iterable}) (approx)"
            elif loop.type == "while_loop" and loop.condition:
                 # Invariant is often related to the negation of the condition or the condition boundary
                 loop.candidate_invariant = f"Loop maintains logical consistency with: {loop.condition}"

    def _analyze_recursion(self, metadata: CodeMetadata):
        if not metadata.recursions:
            return
            
        # Try to find the base case in control flow
        base_cases = [cf for cf in metadata.control_flow if cf.type == "if_condition" and "return" in cf.source] # naive check
        
        for rec in metadata.recursions:
             # Link potential base cases
             if base_cases:
                 rec.base_case_condition = " OR ".join([bc.condition for bc in base_cases if bc.condition])
