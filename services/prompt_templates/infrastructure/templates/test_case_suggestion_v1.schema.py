from pydantic import BaseModel

class TestCaseSuggestionV1Schema(BaseModel):
    source_code: str
    
    @classmethod
    def generate_example(cls):
        return {
            "source_code": "def add(a, b): return a + b"
        }
