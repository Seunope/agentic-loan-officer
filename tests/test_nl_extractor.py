import pytest
from src.utils.nl_extractor import ApplicationExtractor

@pytest.fixture
def extractor():
    return ApplicationExtractor()

def test_extract_all_fields(extractor):
    text = "I'm 30 years old, male, single, living in Lagos, need a loan of 50000 for 60 days"
    fields = {"age", "gender", "marital_status", "location", "amount", "tenure"}
    result = extractor.extract_all_fields(text, fields)
    assert "age" in result
    assert result["age"][0] == 30
    assert "gender" in result
    assert result["gender"][0] == "male"