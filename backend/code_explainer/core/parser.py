import tree_sitter_python
from tree_sitter import Language, Parser, Node
from typing import List, Optional, Dict, Any
from .models import CodeMetadata, LoopInfo, RecursionInfo, ControlFlowElement, VariableRole

class PythonParser:
    def __init__(self):
        self.language = Language(tree_sitter_python.language())
        self.parser = Parser(self.language)

    def parse(self, code: str) -> CodeMetadata:
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        # Assume input is a single function, find the function definition
        func_node = self._find_node(root_node, "function_definition")
        if not func_node:
            # Fallback if no function def found (maybe just a snippet?)
            func_node = root_node
            func_name = "unknown"
            args = []
        else:
            func_name = self._get_node_text(func_node.child_by_field_name("name"), code)
            args = self._extract_args(func_node.child_by_field_name("parameters"), code)

        metadata = CodeMetadata(
            function_name=func_name,
            args=args,
            raw_code=code
        )

        self._traverse(func_node, metadata, code)
        return metadata

    def _find_node(self, node: Node, type_name: str) -> Optional[Node]:
        if node.type == type_name:
            return node
        for child in node.children:
            res = self._find_node(child, type_name)
            if res:
                return res
        return None

    def _get_node_text(self, node: Optional[Node], code: str) -> str:
        if not node:
            return ""
        return code[node.start_byte:node.end_byte]

    def _extract_args(self, params_node: Optional[Node], code: str) -> List[str]:
        if not params_node:
            return []
        args = []
        for child in params_node.children:
            if child.type == "identifier":
                args.append(self._get_node_text(child, code))
            elif child.type in ("typed_parameter", "default_parameter"):
                 # Extract name from typed/default params
                 name_node = child.child(0)
                 if name_node:
                     args.append(self._get_node_text(name_node, code))
        return args

    def _traverse(self, node: Node, metadata: CodeMetadata, code: str):
        # Recursively traverse structure
        if node.type == "for_statement":
            self._handle_for_loop(node, metadata, code)
        elif node.type == "while_statement":
            self._handle_while_loop(node, metadata, code)
        elif node.type == "if_statement":
            self._handle_if(node, metadata, code)
        elif node.type == "call":
            self._handle_call(node, metadata, code)
        elif node.type == "assignment":
            self._handle_assignment(node, metadata, code)
        
        for child in node.children:
            self._traverse(child, metadata, code)

    def _handle_for_loop(self, node: Node, metadata: CodeMetadata, code: str):
        # In Python: for <left> in <right>:
        # child_by_field_name might vary slightly in grammar versions, so we rely on position sometimes or names if reliable
        # for_statement children: 'for', pattern, 'in', value, ':', body
        
        # Tree-sitter-python grammar:
        # left -> child(1), right -> child(3) usually?
        # Better to check children types.
        
        # Attempt to identify iterator and iterable
        # Usually: for x in y
        # x is usually child with type "identifier" or "tuple_pattern" ??
        # actually tree-sitter fields: left, right in some versions, or positional.
        
        # Let's use simple textual extraction for now based on children
        # The grammar usually exposes 'left' and 'right' ?
        # Checking `tree-sitter-python` docs or inspecting node would be ideal.
        # But we can iterate children.
        
        # Typical structure: "for" (0), left (1), "in" (2), right (3), ":" (4), body (5)
        
        loop_var_node = node.child_by_field_name("left")
        iterable_node = node.child_by_field_name("right")
        
        loop_var = self._get_node_text(loop_var_node, code)
        iterable = self._get_node_text(iterable_node, code)
        
        loop_info = LoopInfo(
            type="for_loop",
            source=self._get_node_text(node, code),
            line_start=node.start_point[0],
            line_end=node.end_point[0],
            loop_variable=loop_var,
            iterable=iterable
        )
        metadata.loops.append(loop_info)
        metadata.control_flow.append(loop_info)

    def _handle_while_loop(self, node: Node, metadata: CodeMetadata, code: str):
        condition_node = node.child_by_field_name("condition")
        condition = self._get_node_text(condition_node, code)
        
        loop_info = LoopInfo(
            type="while_loop",
            source=self._get_node_text(node, code),
            line_start=node.start_point[0],
            line_end=node.end_point[0],
            condition=condition
        )
        metadata.loops.append(loop_info)
        metadata.control_flow.append(loop_info)
        
    def _handle_if(self, node: Node, metadata: CodeMetadata, code: str):
        condition_node = node.child_by_field_name("condition")
        condition = self._get_node_text(condition_node, code)
        
        # Heuristic: Check if this if-statement is a base case
        # If it returns, it might be.
        is_base_case = False
        consequence = node.child_by_field_name("consequence")
        if consequence and self._has_return(consequence):
            is_base_case = True
            
        cf = ControlFlowElement(
            type="if_condition",
            source=self._get_node_text(node, code),
            line_start=node.start_point[0],
            line_end=node.end_point[0],
            condition=condition
        )
        metadata.control_flow.append(cf)
        
        if is_base_case:
             # We might tag this later as valid recursion base case if we find recursion
             pass

    def _handle_call(self, node: Node, metadata: CodeMetadata, code: str):
        func_node = node.child_by_field_name("function")
        func_name = self._get_node_text(func_node, code)
        
        if func_name == metadata.function_name:
             # Recursive call
             args_node = node.child_by_field_name("arguments")
             rec = RecursionInfo(
                 type="recursion",
                 source=self._get_node_text(node, code),
                 line_start=node.start_point[0],
                 line_end=node.end_point[0],
                 recursive_step=self._get_node_text(node, code)
             )
             metadata.recursions.append(rec)
             metadata.control_flow.append(rec)

    def _handle_assignment(self, node: Node, metadata: CodeMetadata, code: str):
        left = node.child_by_field_name("left")
        variable_name = self._get_node_text(left, code)
        # Simplified: just capturing all assignments
        metadata.variables.append(VariableRole(name=variable_name, role="mutated_variable"))

    def _has_return(self, node: Node) -> bool:
        if node.type == "return_statement":
            return True
        for child in node.children:
            if self._has_return(child):
                return True
        return False
