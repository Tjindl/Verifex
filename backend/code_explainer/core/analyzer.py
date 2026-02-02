from .parser import PythonParser
from .heuristics import HeuristicsEngine
from .models import CodeMetadata

class CodeAnalyzer:
    def __init__(self):
        self.parser = PythonParser()
        self.heuristics = HeuristicsEngine()

    def analyze(self, code: str) -> CodeMetadata:
        metadata = self.parser.parse(code)
        self.heuristics.apply(metadata)
        return metadata
