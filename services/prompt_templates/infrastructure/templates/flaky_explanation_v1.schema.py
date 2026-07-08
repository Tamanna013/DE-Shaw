from pydantic import BaseModel

class FlakyExplanationV1Schema(BaseModel):
    test_case_name: str
    passes: int
    fails: int
    
    @classmethod
    def generate_example(cls):
        return {
            "test_case_name": "test_network_timeout",
            "passes": 50,
            "fails": 50
        }
