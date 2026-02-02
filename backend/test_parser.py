from code_explainer.core.analyzer import CodeAnalyzer
import json

code_sample = """
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1
"""

analyzer = CodeAnalyzer()
metadata = analyzer.analyze(code_sample)

print(metadata.model_dump_json(indent=2))
