from fastapi.testclient import TestClient
from code_explainer.main import app

client = TestClient(app)

code_sample = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

def test_analyze_endpoint():
    response = client.post("/analyze", json={"code": code_sample})
    assert response.status_code == 200
    data = response.json()
    
    print("Status Code:", response.status_code)
    print("Response Keys:", data.keys())
    print("Metadata Keys:", data["metadata"].keys())
    print("Explanation:", data["explanation"])

if __name__ == "__main__":
    test_analyze_endpoint()
